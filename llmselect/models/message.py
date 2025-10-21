from ..extensions import db
from .base import TimestampMixin


class Message(db.Model, TimestampMixin):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)

    conversation_id = db.Column(db.String(36), db.ForeignKey("conversations.id"), nullable=False)
    conversation = db.relationship("Conversation", back_populates="messages")
