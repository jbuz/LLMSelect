import os
from datetime import timedelta
from typing import List

from cryptography.fernet import Fernet, InvalidToken


class ConfigError(Exception):
    """Raised when environment configuration is invalid."""


def _split_csv(value: str) -> List[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _validate_encryption_key(key: str) -> None:
    try:
        Fernet(key)
    except (InvalidToken, ValueError, TypeError):
        raise ConfigError(
            "ENCRYPTION_KEY must be a valid Fernet key. "
            'Generate one with `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`'
        )


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///llmselect.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_COOKIE_SECURE = os.getenv("JWT_COOKIE_SECURE", "false").lower() == "true"
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_CSRF_HEADER_NAME = "X-CSRF-Token"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=int(os.getenv("ACCESS_TOKEN_EXPIRES_MINUTES", "15"))
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        days=int(os.getenv("REFRESH_TOKEN_EXPIRES_DAYS", "7"))
    )

    RATE_LIMIT = os.getenv("API_RATE_LIMIT", "60 per minute")
    CORS_ORIGINS = _split_csv(
        os.getenv("CORS_ORIGINS", "http://localhost:3044,http://localhost:3000")
    )

    REGISTRATION_TOKEN = os.getenv("REGISTRATION_TOKEN")
    ALLOW_OPEN_REGISTRATION = os.getenv("ALLOW_OPEN_REGISTRATION", "false").lower() in {
        "1",
        "true",
        "yes",
    }

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "1000"))

    @classmethod
    def validate(cls) -> None:
        missing = [
            key
            for key in ("SECRET_KEY", "JWT_SECRET_KEY", "ENCRYPTION_KEY")
            if not getattr(cls, key)
        ]
        if missing:
            raise ConfigError(
                f"Missing required environment variables: {', '.join(missing)}"
            )
        _validate_encryption_key(cls.ENCRYPTION_KEY)


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    RATELIMIT_ENABLED = False  # Disable rate limiting in tests
    JWT_COOKIE_CSRF_PROTECT = False  # Disable CSRF protection for JWT in tests


class ProductionConfig(BaseConfig):
    DEBUG = False


def get_config(env: str):
    env = env.lower()
    if env == "development":
        return DevelopmentConfig
    if env == "testing":
        return TestingConfig
    return ProductionConfig
