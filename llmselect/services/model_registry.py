"""Model registry service for dynamic model management.

This service provides a centralized registry of LLM models from various providers.
It uses static fallback lists for most providers and can query OpenAI's API for
up-to-date model information.
"""

import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..utils.errors import AppError


# Static model definitions for providers
OPENAI_MODELS = [
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
    {
        "id": "gemini-2.0-flash-exp",
        "name": "Gemini 2.0 Flash (Experimental)",
        "provider": "gemini",
        "contextWindow": 1000000,
        "maxTokens": 8192,
    },
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
    """Service for managing LLM model registry with caching."""

    def __init__(self, cache_ttl_seconds: int = 3600):
        """Initialize the model registry service.

        Args:
            cache_ttl_seconds: Time-to-live for cached model data in seconds (default: 1 hour)
        """
        self.cache_ttl_seconds = cache_ttl_seconds
        self._cache: Dict[str, List[Dict]] = {}
        self._cache_timestamp: Dict[str, float] = {}
        
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

    def get_models(self, provider: Optional[str] = None) -> List[Dict]:
        """Get list of available models.

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
        # Check cache
        if self._is_cache_valid(provider):
            return self._cache[provider]

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

        # Update cache
        self._cache[provider] = models
        self._cache_timestamp[provider] = time.time()

        return models

    def _is_cache_valid(self, provider: str) -> bool:
        """Check if cached data is still valid.

        Args:
            provider: Provider name

        Returns:
            True if cache is valid, False otherwise
        """
        if provider not in self._cache:
            return False
        
        cache_age = time.time() - self._cache_timestamp[provider]
        return cache_age < self.cache_ttl_seconds

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
            self._cache.pop(provider, None)
            self._cache_timestamp.pop(provider, None)
        else:
            self._cache.clear()
            self._cache_timestamp.clear()
