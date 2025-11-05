import pytest

from llmselect.services.llm import LLMService
from llmselect.utils.errors import AppError


class DummyResponse:
    def __init__(self, ok, json_data=None, status=500, text="error"):
        self.ok = ok
        self._json = json_data
        self.status_code = status
        self.text = text

    def json(self):
        if self._json is None:
            raise ValueError("No JSON available")
        return self._json


def test_openai_request_sanitises_messages(monkeypatch):
    service = LLMService()
    captured = {}

    def fake_post(url, headers=None, json=None, timeout=None):
        captured["url"] = url
        captured["json"] = json
        return DummyResponse(
            ok=True,
            json_data={
                "choices": [
                    {
                        "message": {
                            "content": "sanitised response",
                        }
                    }
                ]
            },
            status=200,
        )

    monkeypatch.setattr(service.session, "post", fake_post)

    result = service.invoke(
        "openai",
        "gpt-4",
        [{"role": "user", "content": "hello\x00 world"}],
        api_key="fake-key",
    )

    assert result == "sanitised response"
    assert "\x00" not in captured["json"]["messages"][0]["content"]
    assert captured["url"].endswith("/v1/chat/completions")


def test_provider_error_raises_app_error(monkeypatch):
    service = LLMService()

    def failing_post(*args, **kwargs):
        return DummyResponse(
            ok=False,
            json_data={"error": "invalid"},
            status=429,
            text="Too many requests",
        )

    monkeypatch.setattr(service.session, "post", failing_post)

    with pytest.raises(AppError) as excinfo:
        service.invoke("openai", "gpt-4", [{"role": "user", "content": "test"}], api_key="fake")

    error = excinfo.value
    assert error.error_code == "bad_request"
    assert error.extra["status_code"] == 429
