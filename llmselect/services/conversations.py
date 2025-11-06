from datetime import datetime
from typing import Optional, List

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from ..extensions import db, cache
from ..models import Conversation, Message
from ..utils.errors import AppError, NotFoundError


class ConversationService:
    def get_conversation(self, conversation_id: str, user_id: int) -> Conversation:
        conversation = Conversation.query.filter_by(
            id=conversation_id, user_id=user_id
        ).one_or_none()
        if conversation is None:
            raise NotFoundError("Conversation not found")
        return conversation

    def get_user_conversations(
        self, user_id: int, limit: int = 50, offset: int = 0
    ) -> List[Conversation]:
        """Get user's conversations with eager-loaded messages to avoid N+1 queries."""
        cache_key = f"conversations_{user_id}_{limit}_{offset}"

        # Try to get from cache first
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        conversations = (
            Conversation.query.filter_by(user_id=user_id)
            .options(joinedload(Conversation.messages))  # Eager load messages
            .order_by(Conversation.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

        # Cache for 1 hour
        cache.set(cache_key, conversations, timeout=3600)
        return conversations

    def invalidate_conversation_cache(self, user_id: int):
        """Invalidate conversation cache for a user."""
        # Clear all cache keys for this user (simplified approach)
        # Common pagination limits
        for limit in [10, 20, 50, 100, 200]:
            for offset in range(0, 500, limit):
                cache.delete(f"conversations_{user_id}_{limit}_{offset}")

    def create_conversation(self, user_id: int, provider: str, model: str) -> Conversation:
        conversation = Conversation(user_id=user_id, provider=provider, model=model)
        try:
            db.session.add(conversation)
            db.session.commit()
            # Invalidate cache when creating new conversation
            self.invalidate_conversation_cache(user_id)
            return conversation
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise AppError("Unable to create conversation") from exc

    def append_message(self, conversation: Conversation, role: str, content: str) -> Message:
        message = Message(conversation=conversation, role=role, content=content)
        conversation.last_message_at = datetime.utcnow()
        try:
            db.session.add(message)
            db.session.commit()
            # Invalidate cache when adding message
            self.invalidate_conversation_cache(conversation.user_id)
            return message
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise AppError("Unable to persist message") from exc

    def ensure_conversation(
        self,
        user_id: int,
        provider: str,
        model: str,
        conversation_id: Optional[str],
    ) -> Conversation:
        if conversation_id:
            conversation = self.get_conversation(conversation_id, user_id)
            if conversation.provider != provider or conversation.model != model:
                conversation.provider = provider
                conversation.model = model
                conversation.last_message_at = datetime.utcnow()
                try:
                    db.session.commit()
                    # Invalidate cache when updating conversation
                    self.invalidate_conversation_cache(user_id)
                except SQLAlchemyError as exc:
                    db.session.rollback()
                    raise AppError("Unable to update conversation metadata") from exc
            return conversation
        return self.create_conversation(user_id=user_id, provider=provider, model=model)
