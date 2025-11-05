def test_registration_and_login_flow(client):
    register_payload = {
        "username": "testuser",
        "password": "super-secret-password",
        "registration_token": "",
    }
    response = client.post("/api/v1/auth/register", json=register_payload)
    assert response.status_code == 201
    assert response.get_json()["message"] == "Registration successful"

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "username": register_payload["username"],
            "password": register_payload["password"],
        },
    )
    assert login_response.status_code == 200
    data = login_response.get_json()
    assert data["message"] == "Login successful"
    assert data["user"]["username"] == register_payload["username"]
    assert any(
        cookie.startswith("access_token_cookie")
        for cookie in login_response.headers.getlist("Set-Cookie")
    )

    me_response = client.get("/api/v1/auth/me")
    assert me_response.status_code == 200
    assert me_response.get_json()["user"]["username"] == register_payload["username"]


def test_refresh_and_logout(client):
    client.post(
        "/api/v1/auth/register",
        json={"username": "refreshuser", "password": "refresh-password"},
    )
    client.post(
        "/api/v1/auth/login",
        json={"username": "refreshuser", "password": "refresh-password"},
    )

    refresh_response = client.post("/api/v1/auth/refresh")
    assert refresh_response.status_code == 200
    assert refresh_response.get_json()["message"] == "Token refreshed"

    logout_response = client.post("/api/v1/auth/logout")
    assert logout_response.status_code == 200
    assert logout_response.get_json()["message"] == "Logged out"

    me_response = client.get("/api/v1/auth/me")
    assert me_response.status_code == 401
