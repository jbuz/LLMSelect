from typing import List, Dict

from sqlalchemy.exc import SQLAlchemyError

from ..extensions import db
from ..models import ComparisonResult
from ..utils.errors import AppError, NotFoundError


class ComparisonService:
    """Business logic for comparison management."""

    def save_comparison(self, user_id: int, prompt: str, results: List[Dict]) -> ComparisonResult:
        """Save a comparison result to the database.

        Args:
            user_id: The ID of the user who created the comparison
            prompt: The prompt text used for the comparison
            results: List of result dictionaries containing provider, model, response, etc.

        Returns:
            ComparisonResult: The saved comparison object

        Raises:
            AppError: If the comparison cannot be saved
        """
        comparison = ComparisonResult(user_id=user_id, prompt=prompt, results=results)
        try:
            db.session.add(comparison)
            db.session.commit()
            return comparison
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise AppError("Unable to save comparison") from exc

    def get_user_comparisons(
        self, user_id: int, limit: int = 50, offset: int = 0
    ) -> List[ComparisonResult]:
        """Get comparison history for a user.

        Args:
            user_id: The ID of the user
            limit: Maximum number of results to return (default 50, max 100)
            offset: Number of results to skip (for pagination)

        Returns:
            List of ComparisonResult objects ordered by creation date (newest first)
        """
        return (
            ComparisonResult.query.filter_by(user_id=user_id)
            .order_by(ComparisonResult.created_at.desc())
            .limit(min(limit, 100))
            .offset(offset)
            .all()
        )

    def get_comparison(self, comparison_id: int, user_id: int) -> ComparisonResult:
        """Get a specific comparison by ID.

        Args:
            comparison_id: The ID of the comparison
            user_id: The ID of the user (for authorization)

        Returns:
            ComparisonResult: The requested comparison

        Raises:
            NotFoundError: If the comparison doesn't exist or doesn't belong to the user
        """
        comparison = ComparisonResult.query.filter_by(id=comparison_id, user_id=user_id).first()
        if comparison is None:
            raise NotFoundError("Comparison not found")
        return comparison

    def vote_preference(
        self, comparison_id: int, user_id: int, preferred_index: int
    ) -> ComparisonResult:
        """Record user's preference for a specific model's response.

        Args:
            comparison_id: The ID of the comparison
            user_id: The ID of the user (for authorization)
            preferred_index: The index of the preferred result (0-based)

        Returns:
            ComparisonResult: The updated comparison

        Raises:
            NotFoundError: If the comparison doesn't exist or doesn't belong to the user
            AppError: If the update fails
        """
        comparison = self.get_comparison(comparison_id, user_id)

        # Validate preferred_index
        if preferred_index < 0 or preferred_index >= len(comparison.results):
            raise AppError("Invalid preferred_index: out of valid range")

        comparison.preferred_index = preferred_index
        try:
            db.session.commit()
            return comparison
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise AppError("Unable to save vote") from exc

    def delete_comparison(self, comparison_id: int, user_id: int) -> None:
        """Delete a comparison from user's history.

        Args:
            comparison_id: The ID of the comparison to delete
            user_id: The ID of the user (for authorization)

        Raises:
            NotFoundError: If the comparison doesn't exist or doesn't belong to the user
            AppError: If the deletion fails
        """
        comparison = self.get_comparison(comparison_id, user_id)

        try:
            db.session.delete(comparison)
            db.session.commit()
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise AppError("Unable to delete comparison") from exc
