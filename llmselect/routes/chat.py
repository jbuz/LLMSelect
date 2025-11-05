from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from time import time
from typing import Optional

from flask import (
    Blueprint,
    current_app,
    g,
    jsonify,
    request,
    Response,
    stream_with_context,
)
from flask_jwt_extended import current_user, jwt_required

from ..extensions import limiter
from ..services.api_keys import get_api_key
from ..schemas import ChatRequestSchema, CompareRequestSchema

bp = Blueprint("chat", __name__, url_prefix="/api/v1")

chat_schema = ChatRequestSchema()
compare_schema = CompareRequestSchema()


def _rate_limit():
    return current_app.config["RATE_LIMIT"]


def _estimate_tokens(text: str) -> int:
    """Rough token estimation: ~4 characters per token for English text.

    Note: This is a simple heuristic that may be less accurate for:
    - Non-English languages (especially CJK languages)
    - Code and technical content
    - Text with many special characters

    For production use, consider using provider-specific tokenizers.
    """
    return max(1, len(text) // 4)


@bp.post("/chat")
@jwt_required()
@limiter.limit(_rate_limit)
def send_chat_message():
    payload = chat_schema.load(request.get_json() or {})
    provider = payload["provider"]
    model = payload["model"]

    services = current_app.extensions["services"]
    conversation_service = services.conversations
    llm_service = services.llm
    encryption_service = current_app.extensions["key_encryption"]

    conversation_id_value: Optional[str] = None
    if payload.get("conversation_id"):
        conversation_id_value = str(payload["conversation_id"])

    conversation = conversation_service.ensure_conversation(
        user_id=current_user.id,
        provider=provider,
        model=model,
        conversation_id=conversation_id_value,
    )
    g.conversation_id = conversation.id

    messages = payload["messages"]
    if messages:
        latest_message = messages[-1]
        if latest_message.get("role") == "user":
            conversation_service.append_message(conversation, "user", latest_message["content"])

    api_key = get_api_key(current_user, provider, encryption_service)

    response_text = llm_service.invoke(provider, model, messages, api_key)

    conversation_service.append_message(conversation, "assistant", response_text)

    return jsonify({"response": response_text, "conversationId": conversation.id})


@bp.post("/chat/stream")
@jwt_required()
@limiter.limit(_rate_limit)
def stream_chat():
    """Stream single-model chat response via SSE."""
    payload = chat_schema.load(request.get_json() or {})
    provider = payload["provider"]
    model = payload["model"]

    services = current_app.extensions["services"]
    conversation_service = services.conversations
    llm_service = services.llm
    encryption_service = current_app.extensions["key_encryption"]

    conversation_id_value: Optional[str] = None
    if payload.get("conversation_id"):
        conversation_id_value = str(payload["conversation_id"])

    conversation = conversation_service.ensure_conversation(
        user_id=current_user.id,
        provider=provider,
        model=model,
        conversation_id=conversation_id_value,
    )
    g.conversation_id = conversation.id

    messages = payload["messages"]
    if messages:
        latest_message = messages[-1]
        if latest_message.get("role") == "user":
            conversation_service.append_message(conversation, "user", latest_message["content"])

    api_key = get_api_key(current_user, provider, encryption_service)

    def generate():
        """Generator function for SSE stream."""
        try:
            full_response = ""
            start_time = time()
            first_token_time = None
            chunk_count = 0

            # Stream from provider
            for chunk in llm_service.invoke_stream(provider, model, messages, api_key):
                if first_token_time is None:
                    first_token_time = time()
                    ttft = (first_token_time - start_time) * 1000  # Convert to ms
                    current_app.logger.info(
                        f"[Streaming] Time to first token: {ttft:.2f}ms "
                        f"(provider={provider}, model={model})"
                    )

                full_response += chunk
                chunk_count += 1
                yield f"data: {json.dumps({'content': chunk})}\n\n"

            # Log streaming metrics
            total_time = (time() - start_time) * 1000  # Convert to ms
            current_app.logger.info(
                f"[Streaming] Complete: {total_time:.2f}ms total, {chunk_count} chunks "
                f"(provider={provider}, model={model})"
            )

            # Save assistant response after streaming completes
            conversation_service.append_message(conversation, "assistant", full_response)

            # Send completion event
            yield f"data: {json.dumps({'done': True, 'conversationId': str(conversation.id)})}\n\n"

        except Exception as exc:
            current_app.logger.error(
                "Chat streaming failed",
                extra={
                    "provider": provider,
                    "model": model,
                    "error_type": type(exc).__name__,
                },
            )
            error_msg = "Streaming failed. Please check your API key " "and try again."
            yield f"data: {json.dumps({'error': error_msg})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",  # Add keep-alive header
        },
    )


@bp.post("/compare")
@jwt_required()
@limiter.limit(_rate_limit)
def compare():
    payload = compare_schema.load(request.get_json() or {})
    prompt = payload["prompt"]
    providers = payload["providers"]

    services = current_app.extensions["services"]
    llm_service = services.llm
    comparison_service = services.comparisons
    encryption_service = current_app.extensions["key_encryption"]

    results = []
    messages = [{"role": "user", "content": prompt}]

    user = current_user

    with ThreadPoolExecutor(max_workers=len(providers)) as executor:
        futures = {}
        for entry in providers:
            provider_name = entry["provider"]
            model = entry["model"]
            futures[
                executor.submit(
                    _invoke_provider_with_timing,
                    encryption_service,
                    llm_service,
                    user,
                    provider_name,
                    model,
                    messages,
                )
            ] = (provider_name, model)

        for future in as_completed(futures):
            provider_name, model = futures[future]
            try:
                response_text, elapsed_time = future.result()
                results.append(
                    {
                        "provider": provider_name,
                        "model": model,
                        "response": response_text,
                        "time": elapsed_time,
                        "tokens": _estimate_tokens(response_text),
                    }
                )
            except Exception as exc:  # noqa: PERF203
                # Log the full exception for debugging but don't expose details to user
                current_app.logger.error(
                    f"Provider {provider_name} failed",
                    extra={
                        "provider": provider_name,
                        "model": model,
                        "error": str(exc),
                    },
                )
                results.append(
                    {
                        "provider": provider_name,
                        "model": model,
                        "response": (
                            "Provider request failed. Please check your " "API key and try again."
                        ),
                        "time": 0,
                        "tokens": 0,
                        "error": True,
                    }
                )

    # Save comparison to database
    comparison = comparison_service.save_comparison(user_id=user.id, prompt=prompt, results=results)

    return jsonify({"id": comparison.id, "results": results, "prompt": prompt})


def _invoke_provider_with_timing(encryption_service, llm_service, user, provider, model, messages):
    """Invoke provider and measure elapsed time."""
    api_key = get_api_key(user, provider, encryption_service)
    start_time = time()
    response = llm_service.invoke(provider, model, messages, api_key)
    elapsed_time = time() - start_time
    return response, elapsed_time


@bp.post("/compare/stream")
@jwt_required()
@limiter.limit(_rate_limit)
def compare_stream():
    """Stream comparison results from multiple providers in real-time using SSE."""
    payload = compare_schema.load(request.get_json() or {})
    prompt = payload["prompt"]
    providers = payload["providers"]

    services = current_app.extensions["services"]
    llm_service = services.llm
    comparison_service = services.comparisons
    encryption_service = current_app.extensions["key_encryption"]
    user = current_user

    def generate():
        """Generator function for SSE stream."""
        results = {}
        completed_count = 0
        total_providers = len(providers)

        # Send initial event
        yield f"data: {json.dumps({'event': 'start', 'total': total_providers})}\n\n"

        with ThreadPoolExecutor(max_workers=len(providers)) as executor:
            futures = {}
            for entry in providers:
                provider_name = entry["provider"]
                model = entry["model"]
                futures[
                    executor.submit(
                        _stream_provider,
                        encryption_service,
                        llm_service,
                        user,
                        provider_name,
                        model,
                        [{"role": "user", "content": prompt}],
                    )
                ] = (provider_name, model)

            # Process results as they complete
            for future in as_completed(futures):
                provider_name, model = futures[future]
                try:
                    for chunk_data in future.result():
                        # Stream each chunk
                        yield f"data: {json.dumps(chunk_data)}\n\n"

                        # Track completion
                        if chunk_data.get("event") == "complete":
                            completed_count += 1
                            if provider_name not in results:
                                results[provider_name] = chunk_data.get("data", {})

                except Exception as exc:  # noqa: PERF203
                    error_details = {
                        "provider": provider_name,
                        "model": model,
                        "error_type": type(exc).__name__,
                        "error_message": str(exc),
                    }
                    # Try to extract API error details if available
                    if hasattr(exc, "extra"):
                        error_details["api_error"] = exc.extra

                    current_app.logger.error(
                        f"Provider {provider_name} streaming failed",
                        extra=error_details,
                    )
                    error_data = {
                        "event": "error",
                        "provider": provider_name,
                        "model": model,
                        "error": ("Streaming failed. Please check your " "API key and try again."),
                    }
                    yield f"data: {json.dumps(error_data)}\n\n"
                    completed_count += 1

        # Save comparison to database after all streams complete
        comparison_id = None
        if results:
            comparison = comparison_service.save_comparison(
                user_id=user.id,
                prompt=prompt,
                results=[
                    {
                        "provider": provider,
                        "model": data.get("model", ""),
                        "response": data.get("response", ""),
                        "time": data.get("time", 0),
                        "tokens": data.get("tokens", 0),
                    }
                    for provider, data in results.items()
                ],
            )
            comparison_id = comparison.id

        # Send completion event
        done_data = {"event": "done"}
        if comparison_id:
            done_data["comparisonId"] = comparison_id
        yield f"data: {json.dumps(done_data)}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


def _stream_provider(encryption_service, llm_service, user, provider, model, messages):
    """Stream results from a single provider."""
    try:
        api_key = get_api_key(user, provider, encryption_service)
        start_time = time()

        # Send start event for this provider
        yield {
            "event": "chunk",
            "provider": provider,
            "model": model,
            "chunk": "",
            "time": 0,
        }

        full_response = ""
        first_chunk = True

        # Stream from provider
        for chunk in llm_service.invoke_stream(provider, model, messages, api_key):
            full_response += chunk
            elapsed = time() - start_time

            yield {
                "event": "chunk",
                "provider": provider,
                "model": model,
                "chunk": chunk,
                "time": elapsed,
                "first_chunk": first_chunk,
            }
            first_chunk = False

        # Send completion event
        elapsed_time = time() - start_time
        yield {
            "event": "complete",
            "provider": provider,
            "model": model,
            "data": {
                "provider": provider,
                "model": model,
                "response": full_response,
                "time": elapsed_time,
                "tokens": _estimate_tokens(full_response),
            },
        }

    except Exception as exc:
        # Log error type but not full exception message to avoid leaking sensitive data
        current_app.logger.error(
            f"Provider {provider} streaming failed",
            extra={
                "provider": provider,
                "model": model,
                "error_type": type(exc).__name__,
            },
        )
        raise
