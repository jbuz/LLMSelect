from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import current_user, jwt_required

from ..extensions import limiter
from ..schemas import VotePreferenceSchema

bp = Blueprint("comparisons", __name__, url_prefix="/api/v1/comparisons")

vote_schema = VotePreferenceSchema()


def _rate_limit():
    return current_app.config["RATE_LIMIT"]


@bp.get("")
@jwt_required()
@limiter.limit(_rate_limit)
def list_comparisons():
    """Get user's comparison history."""
    limit = min(int(request.args.get("limit", 50)), 100)
    offset = int(request.args.get("offset", 0))

    services = current_app.extensions["services"]
    comparisons = services.comparisons.get_user_comparisons(
        user_id=current_user.id, limit=limit, offset=offset
    )

    return jsonify(
        {
            "comparisons": [c.to_dict() for c in comparisons],
            "limit": limit,
            "offset": offset,
        }
    )


@bp.post("/<int:comparison_id>/vote")
@jwt_required()
@limiter.limit(_rate_limit)
def vote_on_comparison(comparison_id: int):
    """Record preferred model for a comparison."""
    data = vote_schema.load(request.get_json() or {})
    preferred_index = data["preferred_index"]

    services = current_app.extensions["services"]
    comparison = services.comparisons.vote_preference(
        comparison_id=comparison_id,
        user_id=current_user.id,
        preferred_index=preferred_index,
    )

    return jsonify(comparison.to_dict())


@bp.delete("/<int:comparison_id>")
@jwt_required()
@limiter.limit(_rate_limit)
def delete_comparison(comparison_id: int):
    """Delete a comparison from user's history."""
    services = current_app.extensions["services"]
    services.comparisons.delete_comparison(
        comparison_id=comparison_id,
        user_id=current_user.id,
    )

    return jsonify({"message": "Comparison deleted successfully"}), 200
