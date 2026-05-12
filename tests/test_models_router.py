import asyncio

import pytest
import requests
from fastapi import HTTPException

from app.routers import models


def test_models_list_returns_503_when_ollama_unavailable(monkeypatch):
    def fake_get(*args, **kwargs):
        raise requests.RequestException("connection failed")

    monkeypatch.setattr(models.requests, "get", fake_get)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(models.list_models())

    assert exc_info.value.status_code == 503
    assert exc_info.value.detail == "Ollama service is unavailable"
