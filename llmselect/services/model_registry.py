"""Model registry service for dynamic model management.

This service provides a centralized registry of LLM models from various providers.
It uses static fallback lists for most providers and can query OpenAI's API for
up-to-date model information.
"""

import os
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
        "id": "gpt-5.1",
        "name": "GPT-5.1",
        "provider": "openai",
        "contextWindow": 250000,
        "maxTokens": 20000,
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
    # Gemini 3 Series (2025)
    {
        "id": "gemini-3-pro-preview",
        "name": "Gemini 3 Pro (Preview)",
        "provider": "gemini",
        "contextWindow": 2000000,
        "maxTokens": 8192,
    },
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

    def get_models(self, provider: Optional[str] = None) -> List[Dict]:
        """Get list of available models with 24-hour caching.

        Args:
            provider: Optional provider filter (openai, anthropic, gemini, mistral)

        Returns:
            List of model dictionaries with id, name, provider, and metadata
        """
        if provider:
            return self._get_provider_models(provider)

        # Check cache for all models
        cache_key = "all_models"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        # Return all models from all providers
        all_models = []
        for p in ["openai", "anthropic", "gemini", "mistral"]:
            all_models.extend(self._get_provider_models(p))
        
        # Cache for 24 hours
        cache.set(cache_key, all_models, timeout=86400)
        return all_models

    def _get_provider_models(self, provider: str) -> List[Dict]:
        """Get models for a specific provider with caching.
        
        Automatically attempts to verify models with environment API keys if available.

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

        # Check if we have an environment API key for verification
        env_api_key = self._get_env_api_key(provider)
        
        # Get fresh data (with verification if API key available)
        if provider == "openai":
            static_models = OPENAI_MODELS.copy()
            if env_api_key:
                available_ids = self._fetch_openai_models_from_api(env_api_key)
                models = self._filter_available_models(static_models, available_ids)
            else:
                models = static_models
        elif provider == "gemini":
            static_models = GEMINI_MODELS.copy()
            if env_api_key:
                available_ids = self._fetch_gemini_models_from_api(env_api_key)
                models = self._filter_available_models(static_models, available_ids)
            else:
                models = static_models
        elif provider == "mistral":
            static_models = MISTRAL_MODELS.copy()
            if env_api_key:
                available_ids = self._fetch_mistral_models_from_api(env_api_key)
                models = self._filter_available_models(static_models, available_ids)
            else:
                models = static_models
        elif provider == "anthropic":
            # Anthropic doesn't have a models API endpoint
            models = ANTHROPIC_MODELS.copy()
        else:
            raise AppError(f"Unsupported provider: {provider}")

        # Update cache (24 hours for static, 1 hour if verified)
        cache_timeout = 3600 if env_api_key else self.cache_ttl_seconds
        cache.set(cache_key, models, timeout=cache_timeout)

        return models
    
    def _get_env_api_key(self, provider: str) -> Optional[str]:
        """Get API key from environment variables.
        
        Args:
            provider: Provider name (openai, anthropic, gemini, mistral)
            
        Returns:
            API key from environment or None if not found
        """
        env_var_map = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "gemini": ["GEMINI_API_KEY", "GOOGLE_API_KEY"],  # Try both
            "mistral": "MISTRAL_API_KEY",
        }
        
        env_vars = env_var_map.get(provider)
        if not env_vars:
            return None
        
        # Handle both single string and list of strings
        if isinstance(env_vars, str):
            env_vars = [env_vars]
        
        for env_var in env_vars:
            key = os.environ.get(env_var)
            if key and key.strip():
                return key.strip()
        
        return None

    def _fetch_openai_models_from_api(self, api_key: str) -> List[str]:
        """Fetch available OpenAI models from the API.
        
        Args:
            api_key: OpenAI API key
            
        Returns:
            List of available model IDs
        """
        try:
            response = self.session.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            
            # Filter for chat models (gpt and o-series)
            models = [
                m["id"]
                for m in data.get("data", [])
                if "gpt" in m["id"].lower() or m["id"].startswith("o")
            ]
            return models
        except Exception:
            return []

    def _fetch_gemini_models_from_api(self, api_key: str) -> List[str]:
        """Fetch available Gemini models from the API.
        
        Args:
            api_key: Google API key
            
        Returns:
            List of available model IDs
        """
        try:
            response = self.session.get(
                f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}",
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            
            # Filter for generateContent models
            models = [
                m["name"].replace("models/", "")
                for m in data.get("models", [])
                if "generateContent" in m.get("supportedGenerationMethods", [])
            ]
            return models
        except Exception:
            return []

    def _fetch_mistral_models_from_api(self, api_key: str) -> List[str]:
        """Fetch available Mistral models from the API.
        
        Args:
            api_key: Mistral API key
            
        Returns:
            List of available model IDs
        """
        try:
            response = self.session.get(
                "https://api.mistral.ai/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            return [m["id"] for m in data.get("data", [])]
        except Exception:
            return []

    def _filter_available_models(
        self, static_models: List[Dict], available_ids: List[str]
    ) -> List[Dict]:
        """Filter static model list to only include models available via API.
        
        Args:
            static_models: Static list of model definitions
            available_ids: List of model IDs available from the API
            
        Returns:
            Filtered list of model definitions
        """
        if not available_ids:
            # If API query failed, return all static models as fallback
            return static_models
        
        return [m for m in static_models if m["id"] in available_ids]

    def get_models_with_verification(
        self, provider: str, api_key: Optional[str] = None
    ) -> List[Dict]:
        """Get models for a provider with API verification.
        
        This queries the provider's API to verify which models are actually available
        and filters the static list accordingly.
        
        Args:
            provider: Provider name (openai, gemini, mistral)
            api_key: API key for the provider (optional, uses static list if not provided)
            
        Returns:
            List of verified model dictionaries
        """
        cache_key = f"models_verified_{provider}"
        
        # Try cache first
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
        
        # Get static models
        if provider == "openai":
            static_models = OPENAI_MODELS.copy()
            if api_key:
                available_ids = self._fetch_openai_models_from_api(api_key)
                models = self._filter_available_models(static_models, available_ids)
            else:
                models = static_models
        elif provider == "gemini":
            static_models = GEMINI_MODELS.copy()
            if api_key:
                available_ids = self._fetch_gemini_models_from_api(api_key)
                models = self._filter_available_models(static_models, available_ids)
            else:
                models = static_models
        elif provider == "mistral":
            static_models = MISTRAL_MODELS.copy()
            if api_key:
                available_ids = self._fetch_mistral_models_from_api(api_key)
                models = self._filter_available_models(static_models, available_ids)
            else:
                models = static_models
        elif provider == "anthropic":
            # Anthropic doesn't have a models API endpoint
            models = ANTHROPIC_MODELS.copy()
        else:
            raise AppError(f"Unsupported provider: {provider}")
        
        # Cache for 1 hour (shorter than static cache since we verified)
        cache.set(cache_key, models, timeout=3600)
        
        return models


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
