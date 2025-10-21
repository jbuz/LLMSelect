from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import current_user, jwt_required

from ..extensions import limiter
from ..schemas import APIKeySchema
from ..services.api_keys import set_api_keys

bp = Blueprint("keys", __name__, url_prefix="/api/v1/keys")

schema = APIKeySchema()


def _rate_limit():
    return current_app.config["RATE_LIMIT"]


@bp.post("")
@jwt_required()
@limiter.limit(_rate_limit)
def save_keys():
    payload = schema.load(request.get_json() or {})
    encryption_service = current_app.extensions["key_encryption"]
    set_api_keys(current_user, payload, encryption_service)
    return jsonify({"message": "API keys updated successfully"})
