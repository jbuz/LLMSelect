import os
from datetime import datetime

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from dotenv import load_dotenv

from .config import get_config
from .extensions import db, jwt, limiter
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

    app = Flask(__name__, static_folder="dist", template_folder="templates")
    app.config.from_object(config_class)
    config_class.validate()

    CORS(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
        supports_credentials=True,
    )

    db.init_app(app)
    limiter.init_app(app)
    jwt.init_app(app)

    register_blueprints(app)
    register_error_handlers(app)

    services = create_service_container()
    app.extensions["services"] = services
    app.extensions["key_encryption"] = KeyEncryptionService(app.config["ENCRYPTION_KEY"])


    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return User.query.get(identity)

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
        response = jsonify({"error": "token_expired", "message": "Authentication token has expired"})
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
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
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
        return render_template("multi-llm-chat.html")

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
