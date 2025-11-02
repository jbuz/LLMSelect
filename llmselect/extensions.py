from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
jwt = JWTManager()
# Limiter will be initialized with enabled=False in testing config
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],
    enabled=True,  # Default to enabled, will be overridden by app config
)
