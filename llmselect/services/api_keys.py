from typing import Dict

from sqlalchemy.exc import SQLAlchemyError

from ..extensions import db
from ..models import APIKey, PROVIDERS, User
from ..security import KeyEncryptionService
from ..utils.errors import AppError, NotFoundError


def set_api_keys(user: User, key_payload: Dict[str, str], encryptor: KeyEncryptionService) -> None:
    try:
        for provider, value in key_payload.items():
            if provider not in PROVIDERS:
                raise AppError(f"Unsupported provider '{provider}'", extra={"field": provider})

            normalized = (value or "").strip()
            existing = APIKey.query.filter_by(user_id=user.id, provider=provider).one_or_none()

            # Only update if a non-empty value is provided
            # Empty/blank values are ignored (keeps existing key)
            if normalized:
                encrypted = encryptor.encrypt(normalized)
                if existing:
                    existing.key_encrypted = encrypted
                else:
                    db.session.add(
                        APIKey(user_id=user.id, provider=provider, key_encrypted=encrypted)
                    )
            # If blank value provided, keep existing key (do nothing)
            # To delete a key, user would need to use a separate delete endpoint

        db.session.commit()
    except SQLAlchemyError as exc:
        db.session.rollback()
        raise AppError("Unable to persist API keys") from exc


def get_api_key(user: User, provider: str, encryptor: KeyEncryptionService) -> str:
    if provider not in PROVIDERS:
        raise AppError(f"Unsupported provider '{provider}'")

    api_key = APIKey.query.filter_by(user_id=user.id, provider=provider).one_or_none()
    if not api_key:
        raise NotFoundError(f"API key for provider '{provider}' not configured")

    return encryptor.decrypt(api_key.key_encrypted)
