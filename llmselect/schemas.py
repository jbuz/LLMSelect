from marshmallow import Schema, fields, validate

from .models import PROVIDERS


class MessageSchema(Schema):
    role = fields.String(required=True, validate=validate.OneOf(["system", "user", "assistant"]))
    content = fields.String(required=True, validate=validate.Length(min=1, max=4000))


class ChatRequestSchema(Schema):
    provider = fields.String(required=True, validate=validate.OneOf(sorted(PROVIDERS)))
    model = fields.String(required=True, validate=validate.Length(min=1, max=100))
    messages = fields.List(
        fields.Nested(MessageSchema),
        required=True,
        validate=validate.Length(min=1, max=25),
    )
    conversation_id = fields.UUID(load_default=None, data_key="conversationId", allow_none=True)


class CompareProviderSchema(Schema):
    provider = fields.String(required=True, validate=validate.OneOf(sorted(PROVIDERS)))
    model = fields.String(required=True, validate=validate.Length(min=1, max=100))


class CompareRequestSchema(Schema):
    providers = fields.List(
        fields.Nested(CompareProviderSchema),
        required=True,
        validate=validate.Length(min=1, max=4),
    )
    prompt = fields.String(required=True, validate=validate.Length(min=1, max=2000))


class APIKeySchema(Schema):
    openai = fields.String(load_default="")
    anthropic = fields.String(load_default="")
    gemini = fields.String(load_default="")
    mistral = fields.String(load_default="")


class RegistrationSchema(Schema):
    username = fields.String(required=True, validate=validate.Length(min=3, max=50))
    password = fields.String(required=True, validate=validate.Length(min=8, max=128))
    registration_token = fields.String(load_default="")


class LoginSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)


class VotePreferenceSchema(Schema):
    preferred_index = fields.Integer(required=True, validate=validate.Range(min=0))
