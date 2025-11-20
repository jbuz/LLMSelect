import os
from typing import Dict, Optional

from sqlalchemy.exc import SQLAlchemyError

from ..extensions import db
from ..models import APIKey, PROVIDERS, User
from ..security import KeyEncryptionService
from ..utils.errors import AppError, NotFoundError


def set_api_keys(user: User, key_payload: Dict[str, str], encryptor: KeyEncryptionService) -> None:
    """Set or update API keys for a user.
    
    Args:
        user: User object
        key_payload: Dictionary with provider keys and optional override flags
                    Format: {
                        'openai': 'sk-...',
                        'openai_override': True,  # Optional: set override flag
                        'anthropic': 'sk-ant-...',
                        ...
                    }
        encryptor: Encryption service
    """
    try:
        # Process providers (filter out override flags)
        providers_to_update = {k: v for k, v in key_payload.items() if not k.endswith('_override')}
        
        for provider, value in providers_to_update.items():
            if provider not in PROVIDERS:
                raise AppError(f"Unsupported provider '{provider}'", extra={"field": provider})

            normalized = (value or "").strip()
            existing = APIKey.query.filter_by(user_id=user.id, provider=provider).one_or_none()

            # Check if override flag is set in payload
            override_key = f"{provider}_override"
            override_flag = bool(key_payload.get(override_key, False))

            # Only update if a non-empty value is provided
            if normalized:
                encrypted = encryptor.encrypt(normalized)
                if existing:
                    existing.key_encrypted = encrypted
                    existing.override_system_key = override_flag
                else:
                    db.session.add(
                        APIKey(
                            user_id=user.id,
                            provider=provider,
                            key_encrypted=encrypted,
                            override_system_key=override_flag
                        )
                    )
            elif override_key in key_payload:
                # If only override flag is being updated (no key change)
                if existing:
                    existing.override_system_key = override_flag

        db.session.commit()
    except SQLAlchemyError as exc:
        db.session.rollback()
        raise AppError("Unable to persist API keys") from exc


def get_api_key(user: User, provider: str, encryptor: KeyEncryptionService) -> str:
    """Get API key for a provider with environment-first priority (unless overridden).
    
    Priority order:
    1. User's database key IF override_system_key=True (explicit override)
    2. Environment variables (system-wide default)
    3. User's database key IF override_system_key=False (fallback when no env key)
    
    Args:
        user: User object
        provider: Provider name (openai, anthropic, gemini, mistral)
        encryptor: Encryption service for decrypting stored keys
        
    Returns:
        API key string
        
    Raises:
        AppError: If provider is unsupported
        NotFoundError: If no API key is found
    """
    if provider not in PROVIDERS:
        raise AppError(f"Unsupported provider '{provider}'")

    # Check if user has a key with override flag set
    user_key = APIKey.query.filter_by(user_id=user.id, provider=provider).one_or_none()
    if user_key and user_key.override_system_key:
        # Priority 1: User explicitly wants to override system key
        return encryptor.decrypt(user_key.key_encrypted)
    
    # Priority 2: Check environment variables (system-wide default)
    env_key = _get_api_key_from_env(provider)
    if env_key:
        return env_key
    
    # Priority 3: Fall back to user's key if no system key exists
    if user_key:
        return encryptor.decrypt(user_key.key_encrypted)
    
    raise NotFoundError(f"API key for provider '{provider}' not configured")


def _get_api_key_from_env(provider: str) -> Optional[str]:
    """Get API key from environment variables.
    
    Args:
        provider: Provider name (openai, anthropic, gemini, mistral)
        
    Returns:
        API key from environment or None if not found
    """
    env_var_map = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "gemini": ["GEMINI_API_KEY", "GOOGLE_API_KEY"],  # Try both
        "mistral": "MISTRAL_API_KEY",
    }
    
    env_vars = env_var_map.get(provider)
    if not env_vars:
        return None
    
    # Handle both single string and list of strings
    if isinstance(env_vars, str):
        env_vars = [env_vars]
    
    for env_var in env_vars:
        key = os.environ.get(env_var)
        if key and key.strip():
            return key.strip()
    
    return None
