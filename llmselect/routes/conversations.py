from flask import Blueprint, current_app, jsonify, request, Response
from flask_jwt_extended import current_user, jwt_required
from marshmallow import Schema, fields, validate

from ..extensions import limiter, db, cache
from ..models import Conversation

bp = Blueprint("conversations", __name__, url_prefix="/api/v1/conversations")


def _rate_limit():
    return current_app.config["RATE_LIMIT"]


def _invalidate_conversation_cache():
    """Invalidate conversation list cache.

    Note: This invalidates the entire cache regardless of user_id.
    For production at scale, consider implementing user-specific cache keys.
    """
    cache.delete_memoized(list_conversations)


class UpdateConversationSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1, max=255))


update_schema = UpdateConversationSchema()


@bp.get("")
@jwt_required()
@limiter.limit(_rate_limit)
@cache.cached(timeout=300, query_string=True)  # Cache for 5 minutes based on query params
def list_conversations():
    """List all conversations for the current user with pagination and search."""
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 20, type=int)
    search = request.args.get("search", "").strip()

    # Validate pagination parameters
    if page < 1:
        page = 1
    if limit < 1 or limit > 100:
        limit = 20

    query = Conversation.query.filter_by(user_id=current_user.id)

    # Apply search filter if provided
    if search:
        query = query.filter(
            db.or_(
                Conversation.title.ilike(f"%{search}%"),
                Conversation.provider.ilike(f"%{search}%"),
                Conversation.model.ilike(f"%{search}%"),
            )
        )

    # Order by most recent first
    query = query.order_by(Conversation.last_message_at.desc())

    # Apply pagination
    offset = (page - 1) * limit
    conversations = query.limit(limit).offset(offset).all()

    # Calculate total for pagination info
    total = query.count()
    total_pages = (total + limit - 1) // limit if limit > 0 else 0

    # Format response
    result = []
    for conv in conversations:
        # Get message count and preview
        message_count = len(conv.messages)
        preview = ""
        if conv.messages:
            # Get the last user message as preview
            for msg in reversed(conv.messages):
                if msg.role == "user":
                    preview = msg.content[:100]
                    break

        result.append(
            {
                "id": conv.id,
                "title": conv.title or f"{conv.provider} - {conv.model}",
                "provider": conv.provider,
                "model": conv.model,
                "lastMessageAt": conv.last_message_at.isoformat() + "Z",
                "messageCount": message_count,
                "preview": preview,
            }
        )

    return jsonify(
        {
            "conversations": result,
            "page": page,
            "limit": limit,
            "total": total,
            "totalPages": total_pages,
        }
    )


@bp.get("/<conversation_id>")
@jwt_required()
@limiter.limit(_rate_limit)
def get_conversation(conversation_id):
    """Get a single conversation with all messages."""
    services = current_app.extensions["services"]
    conversation_service = services.conversations

    conversation = conversation_service.get_conversation(conversation_id, current_user.id)

    messages = [
        {
            "role": msg.role,
            "content": msg.content,
            "createdAt": msg.created_at.isoformat() + "Z",
        }
        for msg in conversation.messages
    ]

    return jsonify(
        {
            "id": conversation.id,
            "title": conversation.title or f"{conversation.provider} - {conversation.model}",
            "provider": conversation.provider,
            "model": conversation.model,
            "lastMessageAt": conversation.last_message_at.isoformat() + "Z",
            "messages": messages,
            "messageCount": len(messages),
        }
    )


@bp.patch("/<conversation_id>")
@jwt_required()
@limiter.limit(_rate_limit)
def update_conversation(conversation_id):
    """Update conversation metadata (currently only title)."""
    payload = update_schema.load(request.get_json() or {})

    services = current_app.extensions["services"]
    conversation_service = services.conversations

    conversation = conversation_service.get_conversation(conversation_id, current_user.id)
    conversation.title = payload["title"]

    try:
        db.session.commit()
        # Invalidate cache after successful update
        _invalidate_conversation_cache()
    except Exception as exc:
        db.session.rollback()
        current_app.logger.error(f"Failed to update conversation: {exc}")
        return jsonify({"error": "Failed to update conversation"}), 500

    return jsonify(
        {
            "id": conversation.id,
            "title": conversation.title,
            "provider": conversation.provider,
            "model": conversation.model,
            "lastMessageAt": conversation.last_message_at.isoformat() + "Z",
        }
    )


@bp.delete("/<conversation_id>")
@jwt_required()
@limiter.limit(_rate_limit)
def delete_conversation(conversation_id):
    """Delete a conversation and all its messages."""
    services = current_app.extensions["services"]
    conversation_service = services.conversations

    conversation = conversation_service.get_conversation(conversation_id, current_user.id)

    try:
        db.session.delete(conversation)
        db.session.commit()
        # Invalidate cache after successful deletion
        _invalidate_conversation_cache()
    except Exception as exc:
        db.session.rollback()
        current_app.logger.error(f"Failed to delete conversation: {exc}")
        return jsonify({"error": "Failed to delete conversation"}), 500

    return jsonify({"message": "Conversation deleted successfully"}), 200


@bp.get("/<conversation_id>/export")
@jwt_required()
@limiter.limit(_rate_limit)
def export_conversation(conversation_id):
    """Export conversation as markdown or JSON."""
    format_type = request.args.get("format", "markdown").lower()

    if format_type not in ("markdown", "json"):
        return jsonify({"error": "Invalid format. Must be 'markdown' or 'json'"}), 400

    services = current_app.extensions["services"]
    conversation_service = services.conversations

    conversation = conversation_service.get_conversation(conversation_id, current_user.id)

    if format_type == "json":
        # Export as JSON
        messages = [
            {
                "role": msg.role,
                "content": msg.content,
                "createdAt": msg.created_at.isoformat() + "Z",
            }
            for msg in conversation.messages
        ]

        return jsonify(
            {
                "id": conversation.id,
                "title": conversation.title or f"{conversation.provider} - {conversation.model}",
                "provider": conversation.provider,
                "model": conversation.model,
                "lastMessageAt": conversation.last_message_at.isoformat() + "Z",
                "messages": messages,
            }
        )
    else:
        # Export as markdown
        title = conversation.title or f"{conversation.provider} - {conversation.model}"
        lines = [
            f"# {title}",
            "",
            f"**Provider:** {conversation.provider}",
            f"**Model:** {conversation.model}",
            f"**Last Updated:** {conversation.last_message_at.isoformat()}",
            "",
            "---",
            "",
        ]

        for msg in conversation.messages:
            role_label = "User" if msg.role == "user" else "Assistant"
            lines.append(f"## {role_label}")
            lines.append("")
            lines.append(msg.content)
            lines.append("")
            lines.append("---")
            lines.append("")

        markdown_content = "\n".join(lines)

        return Response(
            markdown_content,
            mimetype="text/markdown",
            headers={"Content-Disposition": f'attachment; filename="{conversation.id}.md"'},
        )
