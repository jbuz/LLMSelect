"""Tests for parallel comparison execution - Phase 4.3 Implementation."""

import time


def register_and_login_with_csrf(client):
    """Helper to register/login and return CSRF token."""
    username = f"paralleluser_{int(time.time() * 1000000)}"
    client.post(
        "/api/v1/auth/register",
        json={"username": username, "password": "password"},
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": "password"},
    )
    
    csrf_token = None
    for cookie_header in response.headers.getlist("Set-Cookie"):
        if cookie_header.startswith("csrf_access_token="):
            csrf_token = cookie_header.split("=")[1].split(";")[0]
            break
    
    return csrf_token


def test_comparison_executes_in_parallel(client, app, monkeypatch):
    """Test that multiple models are queried in parallel, not sequentially."""
    csrf_token = register_and_login_with_csrf(client)
    
    # Setup API keys
    client.post(
        "/api/v1/keys",
        json={
            "openai": "sk-test",
            "anthropic": "sk-ant-test",
            "gemini": "test-key",
            "mistral": "test-key",
        },
        headers={"X-CSRF-Token": csrf_token},
    )
    
    # Track execution times
    execution_times = {}
    
    def fake_invoke(provider, model, messages, api_key):
        """Simulate 1 second API delay per provider."""
        start_time = time.time()
        time.sleep(0.1)  # Simulate API delay (reduced for testing)
        execution_times[provider] = time.time() - start_time
        return f"Response from {provider}"
    
    services = app.extensions["services"]
    monkeypatch.setattr(services.llm, "invoke", fake_invoke)
    
    # Measure total execution time
    start_time = time.time()
    
    response = client.post(
        "/api/v1/compare",
        json={
            "providers": [
                {"provider": "openai", "model": "gpt-4o"},
                {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022"},
                {"provider": "gemini", "model": "gemini-2.0-flash-exp"},
                {"provider": "mistral", "model": "mistral-large-latest"},
            ],
            "prompt": "Test parallel execution",
        },
        headers={"X-CSRF-Token": csrf_token},
    )
    
    total_time = time.time() - start_time
    
    assert response.status_code == 200
    
    # If sequential: 4 * 0.1 = 0.4s
    # If parallel: ~0.1s (all execute together)
    # Allow some overhead, so test for < 0.3s (proving parallelism)
    assert total_time < 0.3, f"Execution took {total_time}s, expected < 0.3s (parallel)"
    
    # All providers should have been called
    assert len(execution_times) == 4


def test_comparison_partial_failure(client, app, monkeypatch):
    """Test that comparison continues even if one provider fails."""
    csrf_token = register_and_login_with_csrf(client)
    
    client.post(
        "/api/v1/keys",
        json={
            "openai": "sk-test",
            "anthropic": "sk-ant-test",
            "gemini": "",
            "mistral": "",
        },
        headers={"X-CSRF-Token": csrf_token},
    )
    
    def fake_invoke(provider, model, messages, api_key):
        """Simulate failure for one provider."""
        if provider == "anthropic":
            raise Exception("API error")
        return f"Response from {provider}"
    
    services = app.extensions["services"]
    monkeypatch.setattr(services.llm, "invoke", fake_invoke)
    
    response = client.post(
        "/api/v1/compare",
        json={
            "providers": [
                {"provider": "openai", "model": "gpt-4o"},
                {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022"},
            ],
            "prompt": "Test partial failure",
        },
        headers={"X-CSRF-Token": csrf_token},
    )
    
    assert response.status_code == 200
    data = response.get_json()
    
    # Should have results
    assert "results" in data
    results = data["results"]
    
    # OpenAI should succeed
    openai_results = [r for r in results if r["provider"] == "openai"]
    assert len(openai_results) == 1
    assert "error" not in openai_results[0]
    
    # Anthropic should have error
    anthropic_results = [r for r in results if r["provider"] == "anthropic"]
    assert len(anthropic_results) == 1
    assert "error" in anthropic_results[0]
