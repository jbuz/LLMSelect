from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError

from ..extensions import db
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

    def create_conversation(self, user_id: int, provider: str, model: str) -> Conversation:
        conversation = Conversation(user_id=user_id, provider=provider, model=model)
        try:
            db.session.add(conversation)
            db.session.commit()
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
            return message
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise AppError("Unable to persist message") from exc

    def ensure_conversation(
        self,
        user_id: int,
        provider: str,
        model: str,
        conversation_id: str | None,
    ) -> Conversation:
        if conversation_id:
            conversation = self.get_conversation(conversation_id, user_id)
            if conversation.provider != provider or conversation.model != model:
                conversation.provider = provider
                conversation.model = model
                conversation.last_message_at = datetime.utcnow()
                try:
                    db.session.commit()
                except SQLAlchemyError as exc:
                    db.session.rollback()
                    raise AppError("Unable to update conversation metadata") from exc
            return conversation
        return self.create_conversation(user_id=user_id, provider=provider, model=model)
