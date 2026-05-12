import asyncio
from io import BytesIO

import pytest
from fastapi import HTTPException
from starlette.datastructures import UploadFile

from app.routers import pdf_qa


def test_pdf_upload_rejects_non_pdf_content():
    upload = UploadFile(filename="fake.pdf", file=BytesIO(b"not a real pdf"))

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(pdf_qa.upload_pdf(upload))

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Uploaded file content is not a valid PDF"


def test_pdf_upload_accepts_valid_signature_and_calls_processor(monkeypatch):
    called = {"value": False}

    def fake_process_pdf(file_path):
        called["value"] = True
        return {"chunks_created": 2, "total_pages": 1, "processing_time_seconds": 0.01}

    monkeypatch.setattr(pdf_qa.qa_service, "process_pdf", fake_process_pdf)
    upload = UploadFile(filename="sample.pdf", file=BytesIO(b"%PDF-1.4\n1 0 obj\n"))

    response = asyncio.run(pdf_qa.upload_pdf(upload))

    assert response["status"] == "success"
    assert called["value"] is True


def test_pdf_upload_rejects_oversized_file(monkeypatch):
    monkeypatch.setattr(pdf_qa, "MAX_UPLOAD_SIZE", 5)
    upload = UploadFile(filename="big.pdf", file=BytesIO(b"%PDF-1.4\nabcdefghij"))

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(pdf_qa.upload_pdf(upload))

    assert exc_info.value.status_code == 413
