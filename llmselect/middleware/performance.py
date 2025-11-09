"""Performance monitoring middleware for request timing and slow request logging."""

import time
import logging
from flask import request, g

logger = logging.getLogger(__name__)


def init_performance_monitoring(app):
    """Initialize performance monitoring middleware.

    This middleware:
    - Tracks request duration
    - Adds X-Response-Time header to all responses
    - Logs slow requests (>500ms)

    Args:
        app: Flask application instance
    """

    @app.before_request
    def before_request():
        """Record start time before processing request."""
        g.start_time = time.time()

    @app.after_request
    def after_request(response):
        """Add timing header and log slow requests after processing."""
        if hasattr(g, "start_time"):
            elapsed = time.time() - g.start_time

            # Log slow requests (>500ms)
            if elapsed > 0.5:
                # Sanitize user-controlled values to prevent log injection
                sanitized_method = str(request.method).replace("\r", "").replace("\n", "")
                sanitized_path = str(request.path).replace("\r", "").replace("\n", "")
                sanitized_remote_addr = str(request.remote_addr).replace("\r", "").replace("\n", "")

                logger.warning(
                    f"Slow request: {sanitized_method} {sanitized_path} ({elapsed:.3f}s)",
                    extra={
                        "event": "slow_request",
                        "method": sanitized_method,
                        "path": sanitized_path,
                        "duration": elapsed,
                        "status": response.status_code,
                        "remote_addr": sanitized_remote_addr,
                    },
                )

            # Add timing header to response
            response.headers["X-Response-Time"] = f"{elapsed:.3f}s"

        return response
