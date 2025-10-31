from flask import Blueprint, Flask

from .auth import bp as auth_bp
from .chat import bp as chat_bp
from .comparisons import bp as comparisons_bp
from .keys import bp as keys_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(comparisons_bp)
    app.register_blueprint(keys_bp)
