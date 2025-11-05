from flask import Flask

from .auth import bp as auth_bp
from .chat import bp as chat_bp
from .comparisons import bp as comparisons_bp
from .conversations import bp as conversations_bp
from .keys import bp as keys_bp
from .models import bp as models_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(comparisons_bp)
    app.register_blueprint(conversations_bp)
    app.register_blueprint(keys_bp)
    app.register_blueprint(models_bp)
