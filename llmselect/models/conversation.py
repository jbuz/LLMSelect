from datetime import datetime
from uuid import uuid4

from ..extensions import db
from .base import TimestampMixin


class Conversation(db.Model, TimestampMixin):
    __tablename__ = "conversations"
    __table_args__ = (
        db.Index("idx_conversation_user_created", "user_id", "created_at"),
        db.Index("idx_conversations_user_provider", "user_id", "provider"),
    )

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    provider = db.Column(db.String(32), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(255), nullable=True)
    last_message_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("User", back_populates="conversations")
    messages = db.relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )
