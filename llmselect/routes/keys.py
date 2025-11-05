from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import current_user, jwt_required

from ..extensions import limiter
from ..models.api_key import APIKey
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
    """Get list of providers with API keys configured (doesn't return actual keys)."""
    keys = APIKey.query.filter_by(user_id=current_user.id).all()
    providers = [key.provider for key in keys]
    return jsonify({"providers": providers})


@bp.post("")
@jwt_required()
@limiter.limit(_rate_limit)
def save_keys():
    payload = schema.load(request.get_json() or {})
    encryption_service = current_app.extensions["key_encryption"]
    set_api_keys(current_user, payload, encryption_service)
    return jsonify({"message": "API keys updated successfully"})
