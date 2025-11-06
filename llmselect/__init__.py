import os
from datetime import datetime

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from flask_compress import Compress
from dotenv import load_dotenv
from sqlalchemy import event
from sqlalchemy.engine import Engine
import time

from .config import get_config
from .extensions import db, jwt, limiter, cache
from .models import User
from .security import KeyEncryptionService
from .container import create_service_container
from .routes import register_blueprints
from .utils.errors import register_error_handlers
from .utils.logging import configure_logging


def create_app() -> Flask:
    """
    Application factory that wires together configuration, extensions, blueprints,
    and cross-cutting concerns like logging and error handling.
    """
    load_dotenv()

    env_name = os.getenv("FLASK_ENV", "production")
    config_class = get_config(env_name)

    configure_logging()

    # Use absolute paths for static and template folders relative to project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    static_folder = os.path.join(project_root, "static")
    template_folder = os.path.join(project_root, "templates")

    app = Flask(__name__, static_folder=static_folder, template_folder=template_folder)
    app.config.from_object(config_class)
    config_class.validate()

    CORS(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
        supports_credentials=True,
    )

    db.init_app(app)
    # Configure limiter with testing support
    limiter.init_app(app)
    if app.config.get("RATELIMIT_ENABLED") is False:
        limiter.enabled = False
    jwt.init_app(app)
    cache.init_app(app)

    # Initialize response compression for better network performance
    Compress(app)

    # Set up query monitoring with SQLAlchemy events
    @event.listens_for(Engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        conn.info.setdefault("query_start_time", []).append(time.time())

    @event.listens_for(Engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        total = time.time() - conn.info["query_start_time"].pop(-1)
        if total > 0.1:  # Log queries slower than 100ms
            app.logger.warning(
                f"Slow query ({total:.2f}s): {statement[:200]}",
                extra={"query_time": total, "statement": statement[:200]},
            )

    register_blueprints(app)
    register_error_handlers(app)

    services = create_service_container(app)
    app.extensions["services"] = services
    app.extensions["key_encryption"] = KeyEncryptionService(app.config["ENCRYPTION_KEY"])

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return User.query.get(int(identity))

    @jwt.unauthorized_loader
    def unauthorized_callback(reason):
        response = jsonify({"error": "authentication_error", "message": reason})
        response.status_code = 401
        return response

    @jwt.invalid_token_loader
    def invalid_token_callback(reason):
        response = jsonify({"error": "invalid_token", "message": reason})
        response.status_code = 401
        return response

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_data):
        response = jsonify(
            {"error": "token_expired", "message": "Authentication token has expired"}
        )
        response.status_code = 401
        return response

    @app.before_request
    def log_request():
        app.logger.info(
            "request_received",
            extra={
                "event": "request_received",
                "method": request.method,
                "path": request.path,
                "remote_addr": request.remote_addr,
            },
        )

    @app.after_request
    def finalize_response(response):
        # Log slow database queries in development mode
        if app.config.get("SQLALCHEMY_RECORD_QUERIES") and hasattr(db, "get_app"):
            from flask_sqlalchemy import get_debug_queries

            queries = get_debug_queries()
            slow_query_threshold = app.config.get("SLOW_QUERY_THRESHOLD", 0.1)
            for query in queries:
                if query.duration >= slow_query_threshold:
                    app.logger.warning(
                        f"Slow query detected: {query.duration:.3f}s - {query.statement[:200]}"
                    )

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        # Allow inline styles for webpack style-loader, fonts from Google, and inline scripts
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "script-src 'self' 'unsafe-inline'; "
            "connect-src 'self'"
        )

        # Add caching headers for static assets and suitable API responses
        if request.path.startswith("/static/"):
            # Cache static assets for 1 year with immutable flag
            response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        elif request.path.startswith("/api/") and request.method == "GET":
            # Cache GET API responses for short duration
            if "models" in request.path:
                # Model list can be cached longer
                response.headers["Cache-Control"] = "public, max-age=3600"
            elif response.status_code == 200:
                # Other successful GET requests cached briefly
                response.headers["Cache-Control"] = "private, max-age=60"

        app.logger.info(
            "response_sent",
            extra={
                "event": "response_sent",
                "method": request.method,
                "path": request.path,
                "status_code": response.status_code,
            },
        )
        return response

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/health")
    def health_check():
        return jsonify(
            {
                "status": "ok",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "environment": env_name,
            }
        )

    with app.app_context():
        db.create_all()

    return app
