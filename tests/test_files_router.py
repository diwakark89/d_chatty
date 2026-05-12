import asyncio
import os

import pytest
from fastapi import HTTPException

from app.routers import files
from app import config


def test_delete_file_rejects_path_traversal(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "UPLOAD_DIR", str(tmp_path))

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(files.delete_file(".."))

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Invalid filename"


def test_delete_file_rejects_backslash_traversal(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "UPLOAD_DIR", str(tmp_path))

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(files.delete_file("..\\secret.txt"))

    assert exc_info.value.status_code == 400


def test_delete_file_success(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "UPLOAD_DIR", str(tmp_path))

    file_path = tmp_path / "test.txt"
    file_path.write_text("demo", encoding="utf-8")

    response = asyncio.run(files.delete_file("test.txt"))

    assert response["status"] == "success"
    assert not os.path.exists(file_path)
