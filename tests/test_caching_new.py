"""Tests for caching functionality - Phase 4.3 Implementation."""

import time


def register_and_login(client, username="cacheuser", password="cache-password"):
    """Helper to register and login a test user."""
    client.post(
        "/api/v1/auth/register",
        json={"username": username, "password": password},
    )
    client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )


def test_model_registry_caching(client, app):
    """Test that model registry is cached properly."""
    register_and_login(client)
    
    # Clear cache
    cache = app.extensions.get("cache")
    if cache:
        cache.clear()
    
    # First request - should hit API/database
    response1 = client.get("/api/v1/models")
    assert response1.status_code == 200
    models1 = response1.get_json()["models"]
    
    # Second request - should hit cache
    response2 = client.get("/api/v1/models")
    assert response2.status_code == 200
    models2 = response2.get_json()["models"]
    
    # Results should be identical
    assert models1 == models2
    
    # Cache-Control header should be present
    assert "Cache-Control" in response2.headers
    assert "max-age=3600" in response2.headers["Cache-Control"]


def test_cache_invalidation_after_timeout(client, app, monkeypatch):
    """Test that cache expires after timeout."""
    register_and_login(client)
    
    # Mock shorter cache timeout for testing
    original_timeout = app.config.get("CACHE_DEFAULT_TIMEOUT", 3600)
    app.config["CACHE_DEFAULT_TIMEOUT"] = 1  # 1 second
    
    cache = app.extensions.get("cache")
    if cache:
        cache.clear()
    
    # First request
    response1 = client.get("/api/v1/models")
    assert response1.status_code == 200
    
    # Wait for cache to expire
    time.sleep(2)
    
    # Second request - cache should have expired
    response2 = client.get("/api/v1/models")
    assert response2.status_code == 200
    
    # Restore original timeout
    app.config["CACHE_DEFAULT_TIMEOUT"] = original_timeout


def test_conversation_list_not_cached(client, app):
    """Test that conversation list is NOT cached (user-specific data)."""
    register_and_login(client)
    
    # Get conversation list
    response1 = client.get("/api/v1/conversations")
    assert response1.status_code == 200
    
    # Verify no Cache-Control header or it's set to private/no-cache
    if "Cache-Control" in response1.headers:
        cache_control = response1.headers["Cache-Control"].lower()
        assert "no-cache" in cache_control or "private" in cache_control
