"""Model registry service for dynamic model management.

This service provides a centralized registry of LLM models from various providers.
It uses static fallback lists for most providers and can query OpenAI's API for
up-to-date model information.
"""

from typing import Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..extensions import cache
from ..utils.errors import AppError


# Static model definitions for providers
OPENAI_MODELS = [
    # GPT-5 Series (2025)
    {
        "id": "gpt-5",
        "name": "GPT-5",
        "provider": "openai",
        "contextWindow": 200000,
        "maxTokens": 16384,
    },
    {
        "id": "gpt-5-mini",
        "name": "GPT-5 Mini",
        "provider": "openai",
        "contextWindow": 200000,
        "maxTokens": 16384,
    },
    {
        "id": "gpt-5-nano",
        "name": "GPT-5 Nano",
        "provider": "openai",
        "contextWindow": 200000,
        "maxTokens": 8192,
    },
    {
        "id": "gpt-5-pro",
        "name": "GPT-5 Pro",
        "provider": "openai",
        "contextWindow": 200000,
        "maxTokens": 32768,
    },
    # GPT-4.1 Series (2025)
    {
        "id": "gpt-4.1",
        "name": "GPT-4.1",
        "provider": "openai",
        "contextWindow": 150000,
        "maxTokens": 16384,
    },
    {
        "id": "gpt-4.1-mini",
        "name": "GPT-4.1 Mini",
        "provider": "openai",
        "contextWindow": 150000,
        "maxTokens": 8192,
    },
    {
        "id": "gpt-4.1-nano",
        "name": "GPT-4.1 Nano",
        "provider": "openai",
        "contextWindow": 150000,
        "maxTokens": 4096,
    },
    # o3/o4 Series (2025 reasoning models)
    {
        "id": "o3",
        "name": "o3",
        "provider": "openai",
        "contextWindow": 200000,
        "maxTokens": 100000,
    },
    {
        "id": "o3-mini",
        "name": "o3-mini",
        "provider": "openai",
        "contextWindow": 200000,
        "maxTokens": 65536,
    },
    {
        "id": "o3-pro",
        "name": "o3-pro",
        "provider": "openai",
        "contextWindow": 200000,
        "maxTokens": 100000,
    },
    {
        "id": "o4-mini",
        "name": "o4-mini",
        "provider": "openai",
        "contextWindow": 200000,
        "maxTokens": 65536,
    },
    {
        "id": "o3-deep-research",
        "name": "o3-deep-research",
        "provider": "openai",
        "contextWindow": 200000,
        "maxTokens": 100000,
    },
    {
        "id": "o4-mini-deep-research",
        "name": "o4-mini-deep-research",
        "provider": "openai",
        "contextWindow": 200000,
        "maxTokens": 65536,
    },
    # GPT-4 Series (2024 - legacy but still supported)
    {
        "id": "gpt-4o",
        "name": "GPT-4o",
        "provider": "openai",
        "contextWindow": 128000,
        "maxTokens": 4096,
    },
    {
        "id": "gpt-4o-mini",
        "name": "GPT-4o Mini",
        "provider": "openai",
        "contextWindow": 128000,
        "maxTokens": 16384,
    },
    {
        "id": "o1-preview",
        "name": "o1 Preview",
        "provider": "openai",
        "contextWindow": 128000,
        "maxTokens": 32768,
    },
    {
        "id": "o1-mini",
        "name": "o1 Mini",
        "provider": "openai",
        "contextWindow": 128000,
        "maxTokens": 65536,
    },
    {
        "id": "gpt-4-turbo",
        "name": "GPT-4 Turbo",
        "provider": "openai",
        "contextWindow": 128000,
        "maxTokens": 4096,
    },
    {
        "id": "gpt-4",
        "name": "GPT-4",
        "provider": "openai",
        "contextWindow": 8192,
        "maxTokens": 4096,
    },
    {
        "id": "gpt-3.5-turbo",
        "name": "GPT-3.5 Turbo",
        "provider": "openai",
        "contextWindow": 16385,
        "maxTokens": 4096,
    },
]

ANTHROPIC_MODELS = [
    # Claude 4 Series (2025)
    {
        "id": "claude-sonnet-4-5-20250929",
        "name": "Claude Sonnet 4.5",
        "provider": "anthropic",
        "contextWindow": 200000,
        "maxTokens": 8192,
    },
    {
        "id": "claude-haiku-4-5-20251001",
        "name": "Claude Haiku 4.5",
        "provider": "anthropic",
        "contextWindow": 200000,
        "maxTokens": 8192,
    },
    {
        "id": "claude-opus-4-1-20250805",
        "name": "Claude Opus 4.1",
        "provider": "anthropic",
        "contextWindow": 200000,
        "maxTokens": 8192,
    },
    # Claude 3 Series (2024 - legacy but still supported)
    {
        "id": "claude-3-5-sonnet-20241022",
        "name": "Claude 3.5 Sonnet",
        "provider": "anthropic",
        "contextWindow": 200000,
        "maxTokens": 8192,
    },
    {
        "id": "claude-3-opus-20240229",
        "name": "Claude 3 Opus",
        "provider": "anthropic",
        "contextWindow": 200000,
        "maxTokens": 4096,
    },
    {
        "id": "claude-3-haiku-20240307",
        "name": "Claude 3 Haiku",
        "provider": "anthropic",
        "contextWindow": 200000,
        "maxTokens": 4096,
    },
]

GEMINI_MODELS = [
    # Gemini 2.5 Series (2025)
    {
        "id": "gemini-2.5-pro",
        "name": "Gemini 2.5 Pro",
        "provider": "gemini",
        "contextWindow": 2000000,
        "maxTokens": 8192,
    },
    {
        "id": "gemini-2.5-flash",
        "name": "Gemini 2.5 Flash",
        "provider": "gemini",
        "contextWindow": 1000000,
        "maxTokens": 8192,
    },
    {
        "id": "gemini-2.5-flash-lite",
        "name": "Gemini 2.5 Flash-Lite",
        "provider": "gemini",
        "contextWindow": 1000000,
        "maxTokens": 8192,
    },
    # Gemini 2.0 Series (2024 - legacy but still supported)
    {
        "id": "gemini-2.0-flash-exp",
        "name": "Gemini 2.0 Flash (Experimental)",
        "provider": "gemini",
        "contextWindow": 1000000,
        "maxTokens": 8192,
    },
    # Gemini 1.5 Series (2024 - legacy but still supported)
    {
        "id": "gemini-1.5-pro",
        "name": "Gemini 1.5 Pro",
        "provider": "gemini",
        "contextWindow": 2000000,
        "maxTokens": 8192,
    },
    {
        "id": "gemini-1.5-flash",
        "name": "Gemini 1.5 Flash",
        "provider": "gemini",
        "contextWindow": 1000000,
        "maxTokens": 8192,
    },
    {
        "id": "gemini-pro",
        "name": "Gemini Pro",
        "provider": "gemini",
        "contextWindow": 32760,
        "maxTokens": 2048,
    },
    {
        "id": "gemini-pro-vision",
        "name": "Gemini Pro Vision",
        "provider": "gemini",
        "contextWindow": 16384,
        "maxTokens": 2048,
    },
]

MISTRAL_MODELS = [
    {
        "id": "mistral-large-latest",
        "name": "Mistral Large",
        "provider": "mistral",
        "contextWindow": 128000,
        "maxTokens": 4096,
    },
    {
        "id": "mistral-medium-latest",
        "name": "Mistral Medium",
        "provider": "mistral",
        "contextWindow": 32000,
        "maxTokens": 4096,
    },
    {
        "id": "mistral-small-latest",
        "name": "Mistral Small",
        "provider": "mistral",
        "contextWindow": 32000,
        "maxTokens": 4096,
    },
]


class ModelRegistryService:
    """Service for managing LLM model registry with Flask-Caching integration."""

    def __init__(self, cache_ttl_seconds: int = 86400):
        """Initialize the model registry service.

        Args:
            cache_ttl_seconds: Time-to-live for cached model data in seconds (default: 24 hours)
        """
        self.cache_ttl_seconds = cache_ttl_seconds

        # HTTP session with retries
        self.session = requests.Session()
        retry = Retry(
            total=2,
            read=2,
            connect=2,
            backoff_factor=0.3,
            status_forcelist=(429, 500, 502, 503, 504),
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    @cache.cached(timeout=86400, key_prefix="all_models")
    def get_models(self, provider: Optional[str] = None) -> List[Dict]:
        """Get list of available models with 24-hour caching.

        Args:
            provider: Optional provider filter (openai, anthropic, gemini, mistral)

        Returns:
            List of model dictionaries with id, name, provider, and metadata
        """
        if provider:
            return self._get_provider_models(provider)

        # Return all models from all providers
        all_models = []
        for p in ["openai", "anthropic", "gemini", "mistral"]:
            all_models.extend(self._get_provider_models(p))
        return all_models

    def _get_provider_models(self, provider: str) -> List[Dict]:
        """Get models for a specific provider with caching.

        Args:
            provider: Provider name (openai, anthropic, gemini, mistral)

        Returns:
            List of model dictionaries
        """
        cache_key = f"models_{provider}"

        # Try to get from Flask-Cache
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        # Get fresh data
        if provider == "openai":
            models = self._get_openai_models_static()
        elif provider == "anthropic":
            models = ANTHROPIC_MODELS.copy()
        elif provider == "gemini":
            models = GEMINI_MODELS.copy()
        elif provider == "mistral":
            models = MISTRAL_MODELS.copy()
        else:
            raise AppError(f"Unsupported provider: {provider}")

        # Update cache (24 hours)
        cache.set(cache_key, models, timeout=self.cache_ttl_seconds)

        return models

    def _get_openai_models_static(self) -> List[Dict]:
        """Get OpenAI models from static list.

        Returns fallback static list. Dynamic API querying can be added later.

        Returns:
            List of OpenAI model dictionaries
        """
        return OPENAI_MODELS.copy()

    def clear_cache(self, provider: Optional[str] = None):
        """Clear the model cache.

        Args:
            provider: Optional provider to clear. If None, clears all caches.
        """
        if provider:
            cache.delete(f"models_{provider}")
        else:
            cache.delete("all_models")
            for p in ["openai", "anthropic", "gemini", "mistral"]:
                cache.delete(f"models_{p}")
