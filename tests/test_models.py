"""Tests for model registry service and API endpoint."""

from llmselect.services.model_registry import ModelRegistryService


def register_and_login(client, username="modeluser", password="model-password"):
    client.post("/api/v1/auth/register", json={"username": username, "password": password})
    client.post("/api/v1/auth/login", json={"username": username, "password": password})


def test_get_all_models(client):
    """Test retrieving all models from all providers."""
    register_and_login(client)

    response = client.get("/api/v1/models")
    assert response.status_code == 200

    data = response.get_json()
    assert "models" in data
    assert len(data["models"]) > 0

    # Check that we have models from all providers
    providers = {model["provider"] for model in data["models"]}
    assert "openai" in providers
    assert "anthropic" in providers
    assert "gemini" in providers
    assert "mistral" in providers

    # Check cache header
    assert "Cache-Control" in response.headers
    assert "max-age=3600" in response.headers["Cache-Control"]


def test_get_openai_models(client):
    """Test retrieving OpenAI models only."""
    register_and_login(client)

    response = client.get("/api/v1/models?provider=openai")
    assert response.status_code == 200

    data = response.get_json()
    assert "models" in data
    models = data["models"]

    # All models should be from OpenAI
    assert all(model["provider"] == "openai" for model in models)

    # Check for 2025 models (GPT-5 series)
    model_ids = {model["id"] for model in models}
    assert "gpt-5.1" in model_ids

    # Check for GPT-4.1 series
    assert "gpt-4.1" in model_ids
    assert "gpt-4.1-mini" in model_ids
    assert "gpt-4.1-nano" in model_ids

    # Check for o3/o4 reasoning models
    assert "o3" in model_ids
    assert "o3-mini" in model_ids
    assert "o3-pro" in model_ids
    assert "o4-mini" in model_ids
    assert "o3-deep-research" in model_ids
    assert "o4-mini-deep-research" in model_ids

    # Check for legacy 2024 models still supported
    assert "gpt-4o" in model_ids
    assert "gpt-4o-mini" in model_ids
    assert "o1-preview" in model_ids
    assert "o1-mini" in model_ids


def test_get_anthropic_models(client):
    """Test retrieving Anthropic models only."""
    register_and_login(client)

    response = client.get("/api/v1/models?provider=anthropic")
    assert response.status_code == 200

    data = response.get_json()
    models = data["models"]

    assert all(model["provider"] == "anthropic" for model in models)
    model_ids = {model["id"] for model in models}

    # Check for 2025 Claude 4 series
    assert "claude-sonnet-4-5-20250929" in model_ids
    assert "claude-haiku-4-5-20251001" in model_ids
    assert "claude-opus-4-1-20250805" in model_ids

    # Check for legacy 2024 models still supported
    assert "claude-3-5-sonnet-20241022" in model_ids


def test_get_gemini_models(client):
    """Test retrieving Gemini models only."""
    register_and_login(client)

    response = client.get("/api/v1/models?provider=gemini")
    assert response.status_code == 200

    data = response.get_json()
    models = data["models"]

    assert all(model["provider"] == "gemini" for model in models)
    model_ids = {model["id"] for model in models}

    # Check for 2025 Gemini 2.5 series
    assert "gemini-2.5-pro" in model_ids
    assert "gemini-2.5-flash" in model_ids
    assert "gemini-2.5-flash-lite" in model_ids

    # Check for legacy 2024 models still supported
    assert "gemini-2.0-flash-exp" in model_ids
    assert "gemini-1.5-pro" in model_ids
    assert "gemini-1.5-flash" in model_ids


def test_get_mistral_models(client):
    """Test retrieving Mistral models only."""
    register_and_login(client)

    response = client.get("/api/v1/models?provider=mistral")
    assert response.status_code == 200

    data = response.get_json()
    models = data["models"]

    assert all(model["provider"] == "mistral" for model in models)
    model_ids = {model["id"] for model in models}
    assert "mistral-large-latest" in model_ids


def test_models_endpoint_is_public(client):
    """Test that models endpoint is publicly accessible (no auth required)."""
    response = client.get("/api/v1/models")
    assert response.status_code == 200
    data = response.get_json()
    assert "models" in data


def test_model_registry_caching(app):
    """Test that model registry caches results."""
    registry = ModelRegistryService(cache_ttl_seconds=60)

    # First call should populate cache
    models1 = registry.get_models(provider="openai")
    assert len(models1) > 0

    # Second call should use cache
    models2 = registry.get_models(provider="openai")
    assert models1 == models2

    # Clear cache
    registry.clear_cache("openai")

    # Should fetch again
    models3 = registry.get_models(provider="openai")
    assert models1 == models3
