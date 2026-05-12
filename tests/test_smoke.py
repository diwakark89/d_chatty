from app import qa_service
from run import find_app_module


def test_find_app_module_detects_main_app() -> None:
    assert find_app_module() == "app.main:app"


def test_system_status_returns_ok() -> None:
    payload = qa_service.get_system_status()
    assert payload.get("status") == "ok"
