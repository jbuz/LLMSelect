"""API routes for model registry."""

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import jwt_required

from ..extensions import limiter

bp = Blueprint("models", __name__, url_prefix="/api/v1/models")


def _rate_limit():
    return current_app.config["RATE_LIMIT"]


@bp.get("")
@jwt_required()
@limiter.limit(_rate_limit)
def list_models():
    """Get list of available models from all providers.

    Query Parameters:
        provider (str, optional): Filter by provider (openai, anthropic, gemini, mistral)

    Returns:
        JSON response with list of models
    """
    provider = request.args.get("provider")

    services = current_app.extensions["services"]
    models = services.model_registry.get_models(provider=provider)

    return (
        jsonify({"models": models}),
        200,
        {
            "Cache-Control": "max-age=3600",  # Cache for 1 hour
        },
    )
