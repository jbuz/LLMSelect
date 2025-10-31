from concurrent.futures import ThreadPoolExecutor, as_completed
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


@bp.post("/chat")
@jwt_required()
@limiter.limit(_rate_limit)
def chat():
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
    encryption_service = current_app.extensions["key_encryption"]

    results: Dict[str, str] = {}
    messages = [{"role": "user", "content": prompt}]

    user = current_user

    with ThreadPoolExecutor(max_workers=len(providers)) as executor:
        futures = {}
        for entry in providers:
            provider_name = entry["provider"]
            model = entry["model"]
            futures[
                executor.submit(
                    _invoke_provider,
                    encryption_service,
                    llm_service,
                    user,
                    provider_name,
                    model,
                    messages,
                )
            ] = provider_name

        for future in as_completed(futures):
            provider_name = futures[future]
            try:
                results[provider_name] = future.result()
            except Exception as exc:  # noqa: PERF203
                results[provider_name] = str(exc)

    return jsonify(results)


def _invoke_provider(encryption_service, llm_service, user, provider, model, messages):
    api_key = get_api_key(user, provider, encryption_service)
    return llm_service.invoke(provider, model, messages, api_key)
