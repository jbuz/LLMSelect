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
        command = (
            'python -c "from cryptography.fernet import Fernet; '
            'print(Fernet.generate_key().decode())"'
        )
        message = (
            "ENCRYPTION_KEY must be a valid Fernet key. "
            "Generate one with the following command:\n"
            f"{command}"
        )
        raise ConfigError(message)


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///llmselect.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Connection pooling configuration (only for non-SQLite databases)
    SQLALCHEMY_ENGINE_OPTIONS = (
        {
            "pool_size": int(os.getenv("DB_POOL_SIZE", "10")),
            "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "20")),
            "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", "30")),
            "pool_recycle": 3600,  # Recycle connections after 1 hour
            "pool_pre_ping": True,  # Verify connections before using them
        }
        if not os.getenv("DATABASE_URL", "sqlite:///llmselect.db").startswith("sqlite")
        else {}
    )

    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_COOKIE_SECURE = os.getenv("JWT_COOKIE_SECURE", "false").lower() == "true"
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_CSRF_HEADER_NAME = "X-CSRF-Token"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=int(os.getenv("ACCESS_TOKEN_EXPIRES_MINUTES", "15"))
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.getenv("REFRESH_TOKEN_EXPIRES_DAYS", "7")))

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

    # Azure AI Foundry configuration
    AZURE_AI_FOUNDRY_ENDPOINT = os.getenv("AZURE_AI_FOUNDRY_ENDPOINT")
    AZURE_AI_FOUNDRY_KEY = os.getenv("AZURE_AI_FOUNDRY_KEY")
    AZURE_AI_FOUNDRY_API_VERSION = os.getenv("AZURE_AI_FOUNDRY_API_VERSION", "2024-02-15-preview")
    USE_AZURE_FOUNDRY = os.getenv("USE_AZURE_FOUNDRY", "false").lower() == "true"

    # Azure deployment name mappings (model -> deployment name)
    AZURE_DEPLOYMENT_MAPPINGS = {
        # OpenAI models
        "gpt-4o": os.getenv("AZURE_DEPLOYMENT_GPT4O", "gpt-4o-deployment"),
        "gpt-4o-mini": os.getenv("AZURE_DEPLOYMENT_GPT4O_MINI", "gpt-4o-mini-deployment"),
        "gpt-4-turbo": os.getenv("AZURE_DEPLOYMENT_GPT4_TURBO", "gpt-4-turbo-deployment"),
        "gpt-4": os.getenv("AZURE_DEPLOYMENT_GPT4", "gpt-4-deployment"),
        "gpt-3.5-turbo": os.getenv("AZURE_DEPLOYMENT_GPT35_TURBO", "gpt-35-turbo-deployment"),
        # Anthropic models
        "claude-3-5-sonnet-20241022": os.getenv(
            "AZURE_DEPLOYMENT_CLAUDE_35_SONNET", "claude-35-sonnet-deployment"
        ),
        "claude-3-5-haiku-20241022": os.getenv(
            "AZURE_DEPLOYMENT_CLAUDE_35_HAIKU", "claude-35-haiku-deployment"
        ),
        "claude-3-opus-20240229": os.getenv(
            "AZURE_DEPLOYMENT_CLAUDE_3_OPUS", "claude-3-opus-deployment"
        ),
        # Gemini models
        "gemini-1.5-pro": os.getenv("AZURE_DEPLOYMENT_GEMINI_15_PRO", "gemini-15-pro-deployment"),
        "gemini-1.5-flash": os.getenv(
            "AZURE_DEPLOYMENT_GEMINI_15_FLASH", "gemini-15-flash-deployment"
        ),
        "gemini-1.5-flash-8b": os.getenv(
            "AZURE_DEPLOYMENT_GEMINI_15_FLASH_8B", "gemini-15-flash-8b-deployment"
        ),
        # Mistral models
        "mistral-large-latest": os.getenv(
            "AZURE_DEPLOYMENT_MISTRAL_LARGE", "mistral-large-deployment"
        ),
        "mistral-medium-latest": os.getenv(
            "AZURE_DEPLOYMENT_MISTRAL_MEDIUM", "mistral-medium-deployment"
        ),
        "mistral-small-latest": os.getenv(
            "AZURE_DEPLOYMENT_MISTRAL_SMALL", "mistral-small-deployment"
        ),
    }

    @classmethod
    def validate(cls) -> None:
        missing = [
            key
            for key in ("SECRET_KEY", "JWT_SECRET_KEY", "ENCRYPTION_KEY")
            if not getattr(cls, key)
        ]
        if missing:
            raise ConfigError(f"Missing required environment variables: {', '.join(missing)}")
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
