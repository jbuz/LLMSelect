"""Admin routes for cache management and system monitoring."""

from datetime import datetime

from flask import Blueprint, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..extensions import db, cache
from ..models import User
from ..utils.errors import AuthorizationError

bp = Blueprint("admin", __name__, url_prefix="/api/v1/admin")


def require_admin():
    """Verify that the current user is an admin.

    Raises:
        AuthorizationError: If user is not an admin
    """
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()

    # For now, check if user is the first user (admin)
    # In production, you'd have a proper role/permission system
    if not user:
        raise AuthorizationError("User not found")
    if user.id != 1:
        raise AuthorizationError("Admin access required")


@bp.route("/cache/clear", methods=["POST"])
@jwt_required()
def clear_cache():
    """Clear all application caches.

    Admin endpoint to clear Flask-Caching cache.
    Useful for forcing fresh data or debugging cache issues.

    Returns:
        JSON response with success message
    """
    require_admin()

    # Clear all caches
    cache.clear()

    return (
        jsonify(
            {
                "message": "All caches cleared successfully",
                "cleared_at": datetime.utcnow().isoformat() + "Z",
            }
        ),
        200,
    )


@bp.route("/cache/stats", methods=["GET"])
@jwt_required()
def cache_stats():
    """Get cache statistics.

    Admin endpoint to view cache performance metrics.

    Returns:
        JSON response with cache statistics
    """
    require_admin()

    # SimpleCache doesn't provide detailed stats, but we can show config
    return (
        jsonify(
            {
                "cache_type": current_app.config.get("CACHE_TYPE", "unknown"),
                "default_timeout": current_app.config.get("CACHE_DEFAULT_TIMEOUT", "unknown"),
                "threshold": current_app.config.get("CACHE_THRESHOLD", "unknown"),
                "message": "Cache is operational",
            }
        ),
        200,
    )


@bp.route("/health/detailed", methods=["GET"])
@jwt_required()
def detailed_health():
    """Get detailed health information including database pool stats.

    Admin endpoint for comprehensive system health monitoring.

    Returns:
        JSON response with detailed health metrics
    """
    require_admin()

    health_info = {"status": "healthy", "database": {"connected": True}}

    # Add database pool statistics if available (not available for SQLite)
    try:
        pool = db.engine.pool
        checked_out = (
            pool.checked_out_connections
            if hasattr(pool, "checked_out_connections") and pool.checked_out_connections is not None
            else 0
        )
        health_info["database"]["pool"] = {
            "size": pool.size(),
            "checked_out": checked_out,
            "overflow": pool.overflow() if hasattr(pool, "overflow") else None,
            "checked_in": pool.size() - checked_out,
        }
    except AttributeError:
        # SQLite doesn't have pooling
        health_info["database"]["pool"] = "N/A (SQLite)"
    except Exception as e:
        current_app.logger.exception("Unexpected error in health_check database pool stats")
        health_info["database"]["pool"] = "Error retrieving stats"

    return jsonify(health_info), 200
