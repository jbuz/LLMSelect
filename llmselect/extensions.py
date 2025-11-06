from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache

# SQLAlchemy instance (engine options configured via config.py)
db = SQLAlchemy()
jwt = JWTManager()
# Limiter will be initialized with enabled=False in testing config
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],
    enabled=True,  # Default to enabled, will be overridden by app config
)
# Cache for model registry and conversation lists
cache = Cache(
    config={
        "CACHE_TYPE": "SimpleCache",  # In-memory for demo (use Redis in production)
        "CACHE_DEFAULT_TIMEOUT": 3600,  # 1 hour default
        "CACHE_THRESHOLD": 500,  # Max 500 items in cache
    }
)
