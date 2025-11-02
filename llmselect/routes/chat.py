from concurrent.futures import ThreadPoolExecutor, as_completed
from time import time
from typing import Dict, Optional

from flask import Blueprint, current_app, g, jsonify, request
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
            conversation_service.append_message(
                conversation, "user", latest_message["content"]
            )

    api_key = get_api_key(current_user, provider, encryption_service)

    response_text = llm_service.invoke(provider, model, messages, api_key)

    conversation_service.append_message(conversation, "assistant", response_text)

    return jsonify({"response": response_text, "conversationId": conversation.id})


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
                        "response": "Provider request failed. Please check your API key and try again.",
                        "time": 0,
                        "tokens": 0,
                        "error": True,
                    }
                )

    # Save comparison to database
    comparison = comparison_service.save_comparison(
        user_id=user.id, prompt=prompt, results=results
    )

    return jsonify({"id": comparison.id, "results": results, "prompt": prompt})


def _invoke_provider_with_timing(
    encryption_service, llm_service, user, provider, model, messages
):
    """Invoke provider and measure elapsed time."""
    api_key = get_api_key(user, provider, encryption_service)
    start_time = time()
    response = llm_service.invoke(provider, model, messages, api_key)
    elapsed_time = time() - start_time
    return response, elapsed_time
