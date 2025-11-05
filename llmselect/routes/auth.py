from http import HTTPStatus

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    current_user,
    get_jwt_identity,
    jwt_required,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
)

from ..extensions import db, limiter
from ..models import User
from ..schemas import LoginSchema, RegistrationSchema
from ..utils.errors import AppError, AuthenticationError, AuthorizationError

bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")

registration_schema = RegistrationSchema()
login_schema = LoginSchema()


@bp.post("/register")
@limiter.limit("5 per minute")
def register():
    payload = registration_schema.load(request.get_json() or {})
    username = payload["username"].lower()
    password = payload["password"]
    registration_token = payload.get("registration_token")

    if not current_app.config["ALLOW_OPEN_REGISTRATION"]:
        configured = current_app.config["REGISTRATION_TOKEN"]
        user_exists = db.session.query(User.id).first()
        if configured:
            if registration_token != configured:
                raise AuthorizationError("Invalid registration token supplied")
        elif user_exists:
            raise AppError(
                "Registration is disabled. Contact an administrator to create an account.",
                extra={"code": "registration_closed"},
            )

    if User.query.filter_by(username=username).first():
        raise AppError("Username already exists", extra={"field": "username"})

    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    response = jsonify({"message": "Registration successful"})
    response.status_code = HTTPStatus.CREATED
    return response


@bp.post("/login")
@limiter.limit("10 per minute")
def login():
    payload = login_schema.load(request.get_json() or {})
    username = payload["username"].lower()
    password = payload["password"]

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        raise AuthenticationError("Invalid username or password")

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    response = jsonify({"message": "Login successful", "user": {"username": user.username}})
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)
    return response


@bp.post("/logout")
@limiter.limit("20 per minute")
def logout():
    response = jsonify({"message": "Logged out"})
    unset_jwt_cookies(response)
    return response


@bp.post("/refresh")
@limiter.limit("20 per minute")
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    response = jsonify({"message": "Token refreshed"})
    set_access_cookies(response, access_token)
    return response


@bp.get("/me")
@jwt_required()
def me():
    return jsonify({"user": {"username": current_user.username}})
