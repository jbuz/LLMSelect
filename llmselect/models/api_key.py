from ..extensions import db
from .base import TimestampMixin


class APIKey(db.Model, TimestampMixin):
    __tablename__ = "api_keys"

    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(32), nullable=False)
    key_encrypted = db.Column(db.LargeBinary, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("User", back_populates="api_keys")

    __table_args__ = (
        db.UniqueConstraint("user_id", "provider", name="uq_user_provider"),
        db.Index("idx_apikeys_user_provider", "user_id", "provider"),
    )
