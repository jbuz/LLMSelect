import json
import re
from typing import List, Mapping, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..utils.errors import AppError


def _sanitize_message_content(content: str) -> str:
    content = content.strip()
    content = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", content)
    return content


class LLMService:
    def __init__(
        self,
        max_tokens=1000,
        use_azure: bool = False,
        azure_endpoint: Optional[str] = None,
        azure_api_key: Optional[str] = None,
        azure_api_version: Optional[str] = None,
        azure_deployment_mappings: Optional[dict] = None,
    ):
        self.session = requests.Session()
        retry = Retry(
            total=3,
            read=3,
            connect=3,
            backoff_factor=0.3,
            status_forcelist=(429, 500, 502, 503, 504),
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        self.max_tokens = max_tokens

        # Azure AI Foundry configuration
        self.use_azure = use_azure
        self.azure_endpoint = azure_endpoint
        self.azure_api_key = azure_api_key
        self.azure_api_version = azure_api_version or "2024-02-15-preview"
        self.azure_deployment_mappings = azure_deployment_mappings or {}

    def invoke(
        self, provider: str, model: str, messages: List[Mapping[str, str]], api_key: str
    ) -> str:
        sanitized = [
            {
                "role": message["role"],
                "content": _sanitize_message_content(message["content"]),
            }
            for message in messages
        ]

        # Route through Azure AI Foundry if configured
        if self.use_azure and self.azure_endpoint and self.azure_api_key:
            return self._call_azure_foundry(provider, model, sanitized)

        if provider == "openai":
            return self._call_openai(model, sanitized, api_key)
        if provider == "anthropic":
            return self._call_anthropic(model, sanitized, api_key)
        if provider == "gemini":
            return self._call_gemini(model, sanitized, api_key)
        if provider == "mistral":
            return self._call_mistral(model, sanitized, api_key)
        raise AppError(f"Unsupported provider '{provider}'")

    def _call_openai(self, model: str, messages, api_key: str) -> str:
        # GPT-5+ models use max_completion_tokens, older models use max_tokens
        token_param = (
            "max_completion_tokens" if model.startswith(("gpt-5", "o3", "o4")) else "max_tokens"
        )

        response = self.session.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={"model": model, "messages": messages, token_param: 1000},
            timeout=30,
        )
        return self._handle_response(response, "OpenAI")

    def _call_anthropic(self, model: str, messages, api_key: str) -> str:
        system_message = next((m for m in messages if m["role"] == "system"), None)
        filtered = [m for m in messages if m["role"] != "system"]

        payload = {"model": model, "max_tokens": 1000, "messages": filtered}
        if system_message:
            payload["system"] = system_message["content"]

        response = self.session.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01",
            },
            json=payload,
            timeout=30,
        )
        data = self._parse_json(response, "Anthropic")
        try:
            return data["content"][0]["text"]
        except (KeyError, IndexError) as exc:
            raise AppError("Malformed response from Anthropic") from exc

    def _call_gemini(self, model: str, messages, api_key: str) -> str:
        contents = []
        for message in messages:
            if message["role"] == "system":
                continue
            contents.append(
                {
                    "role": "model" if message["role"] == "assistant" else "user",
                    "parts": [{"text": message["content"]}],
                }
            )

        response = self.session.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            headers={"Content-Type": "application/json"},
            params={"key": api_key},
            json={"contents": contents},
            timeout=30,
        )
        data = self._parse_json(response, "Gemini")
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as exc:
            raise AppError("Malformed response from Gemini") from exc

    def _call_mistral(self, model: str, messages, api_key: str) -> str:
        response = self.session.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={"model": model, "messages": messages, "max_tokens": 1000},
            timeout=30,
        )
        data = self._parse_json(response, "Mistral")
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise AppError("Malformed response from Mistral") from exc

    def _handle_response(self, response: requests.Response, provider_name: str) -> str:
        data = self._parse_json(response, provider_name)
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise AppError(f"Malformed response from {provider_name}") from exc

    @staticmethod
    def _parse_json(response: requests.Response, provider_name: str) -> dict:
        if response.ok:
            try:
                return response.json()
            except ValueError as exc:
                raise AppError(f"Unable to parse {provider_name} response") from exc

        try:
            payload = response.json()
        except ValueError:
            payload = {"message": response.text}

        raise AppError(
            f"{provider_name} API error",
            extra={"status_code": response.status_code, "payload": payload},
        )

    def invoke_stream(
        self, provider: str, model: str, messages: List[Mapping[str, str]], api_key: str
    ):
        """Stream response from LLM provider.

        Yields:
            str: Chunks of the response as they arrive
        """
        sanitized = [
            {
                "role": message["role"],
                "content": _sanitize_message_content(message["content"]),
            }
            for message in messages
        ]

        # Route through Azure AI Foundry if configured
        if self.use_azure and self.azure_endpoint and self.azure_api_key:
            yield from self._stream_azure_foundry(provider, model, sanitized)
            return

        if provider == "openai":
            yield from self._stream_openai(model, sanitized, api_key)
        elif provider == "anthropic":
            yield from self._stream_anthropic(model, sanitized, api_key)
        elif provider == "gemini":
            yield from self._stream_gemini(model, sanitized, api_key)
        elif provider == "mistral":
            yield from self._stream_mistral(model, sanitized, api_key)
        else:
            raise AppError(f"Unsupported provider '{provider}'")

    def _stream_openai(self, model: str, messages, api_key: str):
        """Stream response from OpenAI API."""
        # GPT-5+ models use max_completion_tokens, older models use max_tokens
        token_param = (
            "max_completion_tokens" if model.startswith(("gpt-5", "o3", "o4")) else "max_tokens"
        )

        response = self.session.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": messages,
                token_param: self.max_tokens,
                "stream": True,
            },
            timeout=30,
            stream=True,
        )

        if not response.ok:
            self._parse_json(response, "OpenAI")

        for line in response.iter_lines():
            if not line:
                continue
            line_str = line.decode("utf-8")
            if line_str.startswith("data: "):
                data_str = line_str[6:]
                if data_str == "[DONE]":
                    break
                try:
                    data = json.loads(data_str)
                    if (
                        data.get("choices")
                        and data["choices"][0].get("delta")
                        and data["choices"][0]["delta"].get("content")
                    ):
                        yield data["choices"][0]["delta"]["content"]
                except (ValueError, KeyError, IndexError):
                    continue

    def _stream_anthropic(self, model: str, messages, api_key: str):
        """Stream response from Anthropic Claude API."""
        system_message = next((m for m in messages if m["role"] == "system"), None)
        filtered = [m for m in messages if m["role"] != "system"]

        payload = {
            "model": model,
            "max_tokens": self.max_tokens,
            "messages": filtered,
            "stream": True,
        }
        if system_message:
            payload["system"] = system_message["content"]

        response = self.session.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01",
            },
            json=payload,
            timeout=30,
            stream=True,
        )

        if not response.ok:
            self._parse_json(response, "Anthropic")

        for line in response.iter_lines():
            if not line:
                continue
            line_str = line.decode("utf-8")
            if line_str.startswith("data: "):
                data_str = line_str[6:]
                try:
                    data = json.loads(data_str)
                    if data.get("type") == "content_block_delta":
                        if data.get("delta", {}).get("text"):
                            yield data["delta"]["text"]
                except (ValueError, KeyError):
                    continue

    def _stream_gemini(self, model: str, messages, api_key: str):
        """Stream response from Google Gemini API."""
        contents = []
        for message in messages:
            if message["role"] == "system":
                continue
            contents.append(
                {
                    "role": "model" if message["role"] == "assistant" else "user",
                    "parts": [{"text": message["content"]}],
                }
            )

        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:streamGenerateContent"
        )
        response = self.session.post(
            url,
            headers={"Content-Type": "application/json"},
            params={"key": api_key, "alt": "sse"},
            json={"contents": contents},
            timeout=30,
            stream=True,
        )

        if not response.ok:
            self._parse_json(response, "Gemini")

        for line in response.iter_lines():
            if not line:
                continue
            line_str = line.decode("utf-8")
            if line_str.startswith("data: "):
                data_str = line_str[6:]
                try:
                    data = json.loads(data_str)
                    candidates = data.get("candidates") or []
                    if candidates:
                        content = candidates[0].get("content", {})
                        parts = content.get("parts") or []
                        if parts:
                            text = parts[0].get("text")
                            if text:
                                yield text
                except (ValueError, KeyError, IndexError):
                    continue

    def _stream_mistral(self, model: str, messages, api_key: str):
        """Stream response from Mistral API."""
        response = self.session.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": messages,
                "max_tokens": self.max_tokens,
                "stream": True,
            },
            timeout=30,
            stream=True,
        )

        if not response.ok:
            self._parse_json(response, "Mistral")

        for line in response.iter_lines():
            if not line:
                continue
            line_str = line.decode("utf-8")
            if line_str.startswith("data: "):
                data_str = line_str[6:]
                if data_str == "[DONE]":
                    break
                try:
                    data = json.loads(data_str)
                    if (
                        data.get("choices")
                        and data["choices"][0].get("delta")
                        and data["choices"][0]["delta"].get("content")
                    ):
                        yield data["choices"][0]["delta"]["content"]
                except (ValueError, KeyError, IndexError):
                    continue

    def _get_azure_deployment_name(self, model: str) -> str:
        """Get Azure deployment name for a given model.

        Args:
            model: The model name (e.g., 'gpt-4', 'claude-3-5-sonnet-20241022')

        Returns:
            The Azure deployment name

        Raises:
            AppError: If no deployment mapping found
        """
        deployment = self.azure_deployment_mappings.get(model)
        if not deployment:
            raise AppError(
                f"No Azure deployment mapping found for model '{model}'. "
                f"Please configure the deployment in your environment variables."
            )
        return deployment

    def _call_azure_foundry(
        self, provider: str, model: str, messages: List[Mapping[str, str]]
    ) -> str:
        """Call Azure AI Foundry unified API.

        Azure AI Foundry provides OpenAI-compatible endpoints for all providers
        (OpenAI, Anthropic, Gemini, Mistral) through a single interface.

        Args:
            provider: The provider name (used for error messages)
            model: The model name to map to Azure deployment
            messages: List of message dictionaries

        Returns:
            The response text
        """
        deployment_name = self._get_azure_deployment_name(model)

        # Azure AI Foundry uses OpenAI-compatible format for all providers
        url = (
            f"{self.azure_endpoint}/openai/deployments/{deployment_name}"
            f"/chat/completions?api-version={self.azure_api_version}"
        )

        response = self.session.post(
            url,
            headers={
                "api-key": self.azure_api_key,
                "Content-Type": "application/json",
            },
            json={
                "messages": messages,
                "max_tokens": self.max_tokens,
            },
            timeout=30,
        )

        if not response.ok:
            self._parse_json(response, f"Azure AI Foundry ({provider})")

        return self._handle_response(response, f"Azure AI Foundry ({provider})")

    def _stream_azure_foundry(self, provider: str, model: str, messages: List[Mapping[str, str]]):
        """Stream response from Azure AI Foundry unified API.

        Args:
            provider: The provider name (used for error messages)
            model: The model name to map to Azure deployment
            messages: List of message dictionaries

        Yields:
            str: Chunks of the response as they arrive
        """
        deployment_name = self._get_azure_deployment_name(model)

        # Azure AI Foundry uses OpenAI-compatible format for all providers
        url = (
            f"{self.azure_endpoint}/openai/deployments/{deployment_name}"
            f"/chat/completions?api-version={self.azure_api_version}"
        )

        response = self.session.post(
            url,
            headers={
                "api-key": self.azure_api_key,
                "Content-Type": "application/json",
            },
            json={
                "messages": messages,
                "max_tokens": self.max_tokens,
                "stream": True,
            },
            timeout=30,
            stream=True,
        )

        if not response.ok:
            self._parse_json(response, f"Azure AI Foundry ({provider})")

        # Azure returns OpenAI-compatible streaming format
        for line in response.iter_lines():
            if not line:
                continue
            line_str = line.decode("utf-8")
            if line_str.startswith("data: "):
                data_str = line_str[6:]
                if data_str == "[DONE]":
                    break
                try:
                    data = json.loads(data_str)
                    if (
                        data.get("choices")
                        and data["choices"][0].get("delta")
                        and data["choices"][0]["delta"].get("content")
                    ):
                        yield data["choices"][0]["delta"]["content"]
                except (ValueError, KeyError, IndexError):
                    continue
