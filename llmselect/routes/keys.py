import os
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import current_user, jwt_required

from ..extensions import limiter
from ..models.api_key import APIKey
from ..models import PROVIDERS
from ..schemas import APIKeySchema
from ..services.api_keys import set_api_keys

bp = Blueprint("keys", __name__, url_prefix="/api/v1/keys")

schema = APIKeySchema()


def _rate_limit():
    return current_app.config["RATE_LIMIT"]


@bp.get("")
@jwt_required()
@limiter.limit(_rate_limit)
def get_keys():
    """Get list of providers with API keys configured and their override status."""
    keys = APIKey.query.filter_by(user_id=current_user.id).all()
    
    # Return provider names and override flags
    result = [
        {
            "provider": key.provider,
            "override_system_key": key.override_system_key
        }
        for key in keys
    ]
    
    return jsonify({"keys": result})


@bp.post("")
@jwt_required()
@limiter.limit(_rate_limit)
def save_keys():
    payload = schema.load(request.get_json() or {})
    encryption_service = current_app.extensions["key_encryption"]
    set_api_keys(current_user, payload, encryption_service)
    return jsonify({"message": "API keys updated successfully"})


@bp.get("/system-keys")
@limiter.limit(_rate_limit)
def get_system_keys():
    """Check which providers have system-wide environment keys configured.
    
    No authentication required - this is public information about system capabilities.
    """
    env_key_map = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "gemini": ["GEMINI_API_KEY", "GOOGLE_API_KEY"],
        "mistral": "MISTRAL_API_KEY",
    }
    
    result = {}
    for provider in PROVIDERS:
        env_vars = env_key_map.get(provider, [])
        if isinstance(env_vars, str):
            env_vars = [env_vars]
        
        # Check if any of the env vars are set
        has_system_key = any(
            os.environ.get(var) and os.environ.get(var).strip()
            for var in env_vars
        )
        result[provider] = has_system_key
    
    return jsonify({"system_keys": result})
