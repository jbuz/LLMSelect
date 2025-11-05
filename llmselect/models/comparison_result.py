from ..extensions import db
from .base import TimestampMixin


class ComparisonResult(db.Model, TimestampMixin):
    """Stores comparison results for multi-model comparisons."""

    __tablename__ = "comparison_results"
    __table_args__ = (db.Index("idx_comparison_user_created", "user_id", "created_at"),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    prompt = db.Column(db.Text, nullable=False)

    # Store results as JSON array of dictionaries.
    # Example entry:
    # {
    #     "provider": "openai",
    #     "model": "gpt-4",
    #     "response": "...",
    #     "time": 1.2,
    #     "tokens": 245,
    # }
    results = db.Column(db.JSON, nullable=False)

    # Optional: User's preference (model index or null)
    preferred_index = db.Column(db.Integer, nullable=True)

    # Relationships
    user = db.relationship("User", backref=db.backref("comparisons", lazy="dynamic"))

    def to_dict(self):
        """Serialize comparison result to dictionary."""
        return {
            "id": self.id,
            "prompt": self.prompt,
            "results": self.results,
            "preferred_index": self.preferred_index,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
