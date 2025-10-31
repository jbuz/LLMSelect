import html
import re
from typing import List, Mapping

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..utils.errors import AppError


def _sanitize_message_content(content: str) -> str:
    content = content.strip()
    content = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", content)
    return content


class LLMService:
    def __init__(self):
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
        response = self.session.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={"model": model, "messages": messages, "max_tokens": 1000},
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
