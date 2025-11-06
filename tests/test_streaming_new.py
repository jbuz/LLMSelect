"""Tests for streaming endpoints - Phase 4.3 Implementation."""

import json
from unittest.mock import Mock, patch


def register_and_login(client, username="streamuser", password="stream-password"):
    """Helper to register and login a test user."""
    client.post(
        "/api/v1/auth/register",
        json={"username": username, "password": password},
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    
    # Extract CSRF token
    csrf_token = None
    for cookie_header in response.headers.getlist("Set-Cookie"):
        if cookie_header.startswith("csrf_access_token="):
            csrf_token = cookie_header.split("=")[1].split(";")[0]
            break
    
    client.csrf_token = csrf_token
    return response


def make_authenticated_post(client, url, json_data=None):
    """Make authenticated POST with CSRF token."""
    headers = {}
    csrf_token = getattr(client, "csrf_token", None)
    if csrf_token:
        headers["X-CSRF-Token"] = csrf_token
    
    return client.post(url, json=json_data, headers=headers)


def test_chat_stream_endpoint_success(client, app, monkeypatch):
    """Test successful SSE streaming response."""
    register_and_login(client)
    
    # Setup API key
    make_authenticated_post(
        client,
        "/api/v1/keys",
        json_data={
            "openai": "sk-test-key",
            "anthropic": "",
            "gemini": "",
            "mistral": "",
        },
    )
    
    # Mock streaming response
    def fake_stream(provider, model, messages, api_key):
        """Yield chunks like real LLM would."""
        chunks = ["Hello", " ", "world", "!"]
        for chunk in chunks:
            yield chunk
    
    services = app.extensions["services"]
    monkeypatch.setattr(services.llm, "stream", fake_stream)
    
    # Make streaming request
    response = make_authenticated_post(
        client,
        "/api/v1/chat/stream",
        json_data={
            "provider": "openai",
            "model": "gpt-4o",
            "messages": [{"role": "user", "content": "Hello"}],
        },
    )
    
    assert response.status_code == 200
    assert response.content_type == "text/event-stream; charset=utf-8"
    
    # Parse SSE events
    events = []
    for line in response.data.decode("utf-8").split("\n"):
        if line.startswith("data: "):
            data = line[6:]  # Remove "data: " prefix
            if data and data != "[DONE]":
                events.append(json.loads(data))
    
    # Verify streaming chunks
    assert len(events) >= 4
    assert events[0]["content"] == "Hello"
    assert events[1]["content"] == " "
    assert events[2]["content"] == "world"
    assert events[3]["content"] == "!"
    
    # Verify conversation ID in events
    assert all("conversationId" in event for event in events)


def test_chat_stream_error_handling(client, app, monkeypatch):
    """Test streaming error handling."""
    register_and_login(client)
    
    # Setup API key
    make_authenticated_post(
        client,
        "/api/v1/keys",
        json_data={
            "openai": "sk-test-key",
            "anthropic": "",
            "gemini": "",
            "mistral": "",
        },
    )
    
    # Mock stream that raises error
    def fake_stream(provider, model, messages, api_key):
        """Simulate API error during streaming."""
        yield "Starting"
        raise Exception("API connection lost")
    
    services = app.extensions["services"]
    monkeypatch.setattr(services.llm, "stream", fake_stream)
    
    response = make_authenticated_post(
        client,
        "/api/v1/chat/stream",
        json_data={
            "provider": "openai",
            "model": "gpt-4o",
            "messages": [{"role": "user", "content": "Hello"}],
        },
    )
    
    assert response.status_code == 200
    
    # Parse SSE events
    events = []
    for line in response.data.decode("utf-8").split("\n"):
        if line.startswith("data: "):
            data = line[6:]
            if data and data != "[DONE]":
                events.append(json.loads(data))
    
    # Should have error event
    error_events = [e for e in events if e.get("error")]
    assert len(error_events) > 0
    assert "error" in error_events[0]


def test_chat_stream_missing_api_key(client, app):
    """Test streaming without configured API key."""
    register_and_login(client)
    
    # Don't setup API key
    response = make_authenticated_post(
        client,
        "/api/v1/chat/stream",
        json_data={
            "provider": "openai",
            "model": "gpt-4o",
            "messages": [{"role": "user", "content": "Hello"}],
        },
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "API key" in data["error"]
