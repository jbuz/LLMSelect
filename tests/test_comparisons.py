"""Tests for comparison functionality."""

import time


def register_and_login(client, username="testuser", password="testpassword"):
    """Helper to register and login a test user."""
    # Add timestamp to username to avoid conflicts
    unique_username = f"{username}_{int(time.time() * 1000000)}"
    client.post(
        "/api/v1/auth/register",
        json={"username": unique_username, "password": password},
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"username": unique_username, "password": password},
    )

    # Extract and store CSRF token for authenticated requests
    csrf_token = None
    for cookie_header in response.headers.getlist("Set-Cookie"):
        if cookie_header.startswith("csrf_access_token="):
            csrf_token = cookie_header.split("=")[1].split(";")[0]
            break

    # Store CSRF token as client attribute
    client.csrf_token = csrf_token

    return response


def make_authenticated_post(client, url, json=None):
    """Make an authenticated POST request with CSRF token."""
    headers = {}
    # Get CSRF token from client's stored attribute
    csrf_token = getattr(client, "csrf_token", None)
    if csrf_token:
        headers["X-CSRF-Token"] = csrf_token

    return client.post(url, json=json, headers=headers)


def test_compare_saves_to_database(client, app, monkeypatch):
    """Comparison results are persisted to database."""
    register_and_login(client)

    # Mock LLM service to avoid real API calls
    def fake_invoke(provider, model, messages, api_key):
        if provider == "openai":
            return "Response from GPT-4"
        return "Response from Claude"

    services = app.extensions["services"]
    monkeypatch.setattr(services.llm, "invoke", fake_invoke)

    response = make_authenticated_post(
        client,
        "/api/v1/compare",
        json={
            "providers": [
                {"provider": "openai", "model": "gpt-4"},
                {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022"},
            ],
            "prompt": "Test prompt for comparison",
        },
    )

    assert response.status_code == 200
    data = response.get_json()

    # Check new response format
    assert "id" in data
    assert "results" in data
    assert "prompt" in data
    assert data["prompt"] == "Test prompt for comparison"

    # Check results structure
    results = data["results"]
    assert len(results) == 2

    # Check first result
    assert results[0]["provider"] in ["openai", "anthropic"]
    assert "model" in results[0]
    assert "response" in results[0]
    assert "time" in results[0]
    assert "tokens" in results[0]

    # Verify saved to database
    from llmselect.models import ComparisonResult

    with app.app_context():
        comparison = ComparisonResult.query.get(data["id"])
        assert comparison is not None
        assert comparison.prompt == "Test prompt for comparison"
        assert len(comparison.results) == 2


def test_get_comparison_history(client, app, monkeypatch):
    """Users can retrieve comparison history."""
    register_and_login(client)

    # Create some comparisons
    def fake_invoke(provider, model, messages, api_key):
        return "Mock response"

    services = app.extensions["services"]
    monkeypatch.setattr(services.llm, "invoke", fake_invoke)

    for i in range(3):
        make_authenticated_post(
            client,
            "/api/v1/compare",
            json={
                "providers": [
                    {"provider": "openai", "model": "gpt-4"},
                ],
                "prompt": f"Test prompt {i}",
            },
        )

    # Get history
    response = client.get("/api/v1/comparisons")
    assert response.status_code == 200

    data = response.get_json()
    assert "comparisons" in data
    assert len(data["comparisons"]) == 3

    # Check ordering (newest first)
    assert data["comparisons"][0]["prompt"] == "Test prompt 2"
    assert data["comparisons"][1]["prompt"] == "Test prompt 1"
    assert data["comparisons"][2]["prompt"] == "Test prompt 0"


def test_vote_on_comparison(client, app, monkeypatch):
    """Users can vote for preferred response."""
    register_and_login(client)

    # Create comparison
    def fake_invoke(provider, model, messages, api_key):
        if provider == "openai":
            return "Response from GPT-4"
        return "Response from Claude"

    services = app.extensions["services"]
    monkeypatch.setattr(services.llm, "invoke", fake_invoke)

    compare_response = make_authenticated_post(
        client,
        "/api/v1/compare",
        json={
            "providers": [
                {"provider": "openai", "model": "gpt-4"},
                {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022"},
            ],
            "prompt": "Which is better?",
        },
    )

    comparison_id = compare_response.get_json()["id"]

    # Vote for first response
    vote_response = make_authenticated_post(
        client,
        f"/api/v1/comparisons/{comparison_id}/vote",
        json={"preferred_index": 0},
    )

    assert vote_response.status_code == 200
    data = vote_response.get_json()
    assert data["preferred_index"] == 0

    # Update vote to second response
    vote_response2 = make_authenticated_post(
        client,
        f"/api/v1/comparisons/{comparison_id}/vote",
        json={"preferred_index": 1},
    )

    assert vote_response2.status_code == 200
    data2 = vote_response2.get_json()
    assert data2["preferred_index"] == 1


def test_vote_invalid_index(client, app, monkeypatch):
    """Voting with invalid index returns error."""
    register_and_login(client)

    # Create comparison with 2 results
    def fake_invoke(provider, model, messages, api_key):
        return f"Response from {provider}"

    services = app.extensions["services"]
    monkeypatch.setattr(services.llm, "invoke", fake_invoke)

    compare_response = make_authenticated_post(
        client,
        "/api/v1/compare",
        json={
            "providers": [
                {"provider": "openai", "model": "gpt-4"},
                {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022"},
            ],
            "prompt": "Test",
        },
    )

    comparison_id = compare_response.get_json()["id"]

    # Try to vote with invalid index
    vote_response = make_authenticated_post(
        client,
        f"/api/v1/comparisons/{comparison_id}/vote",
        json={"preferred_index": 5},  # Out of range
    )

    assert vote_response.status_code == 400


def test_comparison_requires_auth(client):
    """Comparison endpoints require authentication."""
    # Try to get history without auth
    response = client.get("/api/v1/comparisons")
    assert response.status_code == 401

    # Try to vote without auth
    response = make_authenticated_post(
        client, "/api/v1/comparisons/1/vote", json={"preferred_index": 0}
    )
    assert response.status_code == 401


def test_comparison_pagination(client, app, monkeypatch):
    """Comparison history supports pagination."""
    register_and_login(client)

    # Create 10 comparisons
    def fake_invoke(provider, model, messages, api_key):
        return "Mock response"

    services = app.extensions["services"]
    monkeypatch.setattr(services.llm, "invoke", fake_invoke)

    for i in range(10):
        make_authenticated_post(
            client,
            "/api/v1/compare",
            json={
                "providers": [{"provider": "openai", "model": "gpt-4"}],
                "prompt": f"Prompt {i}",
            },
        )

    # Get first page (limit 5)
    response = client.get("/api/v1/comparisons?limit=5&offset=0")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["comparisons"]) == 5
    assert data["limit"] == 5
    assert data["offset"] == 0

    # Get second page
    response2 = client.get("/api/v1/comparisons?limit=5&offset=5")
    data2 = response2.get_json()
    assert len(data2["comparisons"]) == 5

    # Ensure different results
    assert data["comparisons"][0]["id"] != data2["comparisons"][0]["id"]


def test_comparison_with_error_handling(client, app, monkeypatch):
    """Comparison handles errors gracefully when a provider fails."""
    register_and_login(client)

    # Mock one success and one failure
    responses = iter(["Successful response", None])
    errors = iter([None, Exception("Provider failed")])

    def fake_invoke(provider, model, messages, api_key):
        error = next(errors)
        if error:
            raise error
        return next(responses)

    services = app.extensions["services"]
    monkeypatch.setattr(services.llm, "invoke", fake_invoke)

    response = make_authenticated_post(
        client,
        "/api/v1/compare",
        json={
            "providers": [
                {"provider": "openai", "model": "gpt-4"},
                {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022"},
            ],
            "prompt": "Test error handling",
        },
    )

    assert response.status_code == 200
    data = response.get_json()
    results = data["results"]

    # Both providers should return a result (one success, one error)
    assert len(results) == 2

    # At least one should have the error flag
    has_error = any(r.get("error") for r in results)
    assert has_error


def test_delete_comparison(client, app, monkeypatch):
    """Test deleting a comparison from history."""
    register_and_login(client)

    # Mock LLM service
    def fake_invoke(provider, model, messages, api_key):
        return "Test response"

    services = app.extensions["services"]
    monkeypatch.setattr(services.llm, "invoke", fake_invoke)

    # Create a comparison
    response = make_authenticated_post(
        client,
        "/api/v1/compare",
        json={
            "providers": [{"provider": "openai", "model": "gpt-4o"}],
            "prompt": "Test prompt to delete",
        },
    )
    assert response.status_code == 200
    comparison_id = response.get_json()["id"]

    # Verify it exists
    list_response = client.get("/api/v1/comparisons")
    assert list_response.status_code == 200
    assert len(list_response.get_json()["comparisons"]) == 1

    # Delete it
    delete_response = client.delete(f"/api/v1/comparisons/{comparison_id}")
    assert delete_response.status_code == 200

    # Verify it's gone
    list_response2 = client.get("/api/v1/comparisons")
    assert list_response2.status_code == 200
    assert len(list_response2.get_json()["comparisons"]) == 0
