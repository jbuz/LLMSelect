from http import HTTPStatus
from typing import Any, Dict, Optional

from flask import g, jsonify
from marshmallow import ValidationError as MarshmallowValidationError
from werkzeug.exceptions import HTTPException


def _attach_conversation_context(payload: Dict[str, Any]) -> Dict[str, Any]:
    conversation_id = getattr(g, "conversation_id", None)
    if conversation_id:
        details = payload.setdefault("details", {})
        if isinstance(details, dict):
            details.setdefault("conversationId", conversation_id)
    return payload


class AppError(Exception):
    status_code = HTTPStatus.BAD_REQUEST
    error_code = "bad_request"

    def __init__(self, message: str, *, extra: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.extra = extra or {}

    def to_dict(self) -> Dict[str, Any]:
        payload = {"error": self.error_code, "message": self.message}
        if self.extra:
            payload["details"] = self.extra
        return payload


class AuthenticationError(AppError):
    status_code = HTTPStatus.UNAUTHORIZED
    error_code = "authentication_error"


class AuthorizationError(AppError):
    status_code = HTTPStatus.FORBIDDEN
    error_code = "authorization_error"


class NotFoundError(AppError):
    status_code = HTTPStatus.NOT_FOUND
    error_code = "not_found"


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(err: AppError):
        payload = _attach_conversation_context(err.to_dict())
        response = jsonify(payload)
        response.status_code = err.status_code
        return response

    @app.errorhandler(MarshmallowValidationError)
    def handle_validation_error(err: MarshmallowValidationError):
        payload = _attach_conversation_context(
            {
                "error": "validation_error",
                "message": "Invalid request payload",
                "details": err.messages,
            }
        )
        response = jsonify(payload)
        response.status_code = HTTPStatus.UNPROCESSABLE_ENTITY
        return response

    @app.errorhandler(HTTPException)
    def handle_http_exception(err: HTTPException):
        payload = _attach_conversation_context(
            {"error": err.name.lower().replace(" ", "_"), "message": err.description}
        )
        response = jsonify(payload)
        response.status_code = err.code or HTTPStatus.INTERNAL_SERVER_ERROR
        return response

    @app.errorhandler(Exception)
    def handle_unexpected_error(err: Exception):
        app.logger.exception("Unexpected server error")
        payload = _attach_conversation_context(
            {"error": "internal_error", "message": "An unexpected error occurred"}
        )
        response = jsonify(payload)
        response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
        return response
