from llmselect.models import APIKey, Conversation


def register_and_login(client, username="chatuser", password="chat-password"):
    client.post("/api/v1/auth/register", json={"username": username, "password": password})
    client.post("/api/v1/auth/login", json={"username": username, "password": password})


def test_chat_creates_and_reuses_conversation(client, app, monkeypatch):
    register_and_login(client)

    # Set up fake API key
    payload = {
        "openai": "sk-test-fake-key",
        "anthropic": "",
        "gemini": "",
        "mistral": "",
    }
    response = client.post("/api/v1/keys", json=payload)
    assert response.status_code == 200

    responses = iter(["First reply", "Follow-up reply"])

    def fake_invoke(provider, model, messages, api_key):
        assert provider == "openai"
        assert model == "gpt-4"
        assert messages[-1]["role"] == "user"
        return next(responses)

    services = app.extensions["services"]
    monkeypatch.setattr(services.llm, "invoke", fake_invoke)

    payload = {
        "provider": "openai",
        "model": "gpt-4",
        "messages": [{"role": "user", "content": "Hello there"}],
    }
    first_response = client.post("/api/v1/chat", json=payload)
    assert first_response.status_code == 200
    first_data = first_response.get_json()
    assert first_data["response"] == "First reply"
    conversation_id = first_data["conversationId"]
    assert conversation_id

    payload["messages"].append({"role": "assistant", "content": "First reply"})
    payload["messages"].append({"role": "user", "content": "And another thing"})
    payload["conversationId"] = conversation_id

    second_response = client.post("/api/v1/chat", json=payload)
    assert second_response.status_code == 200
    second_data = second_response.get_json()
    assert second_data["response"] == "Follow-up reply"
    assert second_data["conversationId"] == conversation_id

    with app.app_context():
        conversation = Conversation.query.filter_by(id=conversation_id).one()
        assert conversation.provider == "openai"
        assert conversation.model == "gpt-4"
        # Two user messages + two assistant replies
        assert len(conversation.messages) == 4
        assert conversation.messages[0].role == "user"
        assert conversation.messages[-1].role == "assistant"


def test_api_key_storage(client, app):
    register_and_login(client, username="keyuser", password="keypass123")
    payload = {"openai": "sk-test-123", "anthropic": "", "gemini": "", "mistral": ""}
    response = client.post("/api/v1/keys", json=payload)
    assert response.status_code == 200
    assert response.get_json()["message"] == "API keys updated successfully"

    with app.app_context():
        stored = APIKey.query.filter_by(provider="openai").one()
        assert stored.user.username == "keyuser"


def test_chat_stream_endpoint(client, app, monkeypatch):
    """Test SSE streaming chat endpoint."""
    register_and_login(client)

    # Set up fake API key
    payload = {
        "openai": "sk-test-fake-key",
        "anthropic": "",
        "gemini": "",
        "mistral": "",
    }
    response = client.post("/api/v1/keys", json=payload)
    assert response.status_code == 200

    # Mock LLM service to return chunks
    def fake_stream_invoke(provider, model, messages, api_key):
        yield "Hello"
        yield " "
        yield "world"
        yield "!"

    services = app.extensions["services"]
    monkeypatch.setattr(services.llm, "invoke_stream", fake_stream_invoke)

    # Make streaming request
    response = client.post(
        "/api/v1/chat/stream",
        json={
            "provider": "openai",
            "model": "gpt-4",
            "messages": [{"role": "user", "content": "Test message"}],
        },
    )

    assert response.status_code == 200
    assert response.content_type == "text/event-stream; charset=utf-8"

    # Verify chunks received
    data = response.get_data(as_text=True)
    assert "Hello" in data
    assert "world" in data
    assert '"done": true' in data
    assert '"conversationId"' in data
