import os

from app import persistence


def _configure_temp_paths(monkeypatch, tmp_path):
    persistence_dir = tmp_path / "data"
    backup_dir = persistence_dir / "backups"
    monkeypatch.setattr(persistence, "PERSISTENCE_DIR", str(persistence_dir))
    monkeypatch.setattr(persistence, "BACKUP_DIR", str(backup_dir))
    monkeypatch.setattr(persistence, "QA_STATE_FILE", str(persistence_dir / "qa_state.pkl.gz"))
    monkeypatch.setattr(persistence, "LEGACY_STATE_FILE", str(persistence_dir / "qa_state.pkl"))
    return persistence_dir, backup_dir


def test_persistence_roundtrip(monkeypatch, tmp_path):
    _configure_temp_paths(monkeypatch, tmp_path)

    state = {"vector_store": {"id": "v1"}, "meta": {"pages": 1}}
    assert persistence.save_qa_state(state) is True

    loaded = persistence.load_qa_state()
    assert loaded is not None
    assert loaded["vector_store"]["id"] == "v1"


def test_persistence_recovers_from_backup(monkeypatch, tmp_path):
    _, backup_dir = _configure_temp_paths(monkeypatch, tmp_path)

    first_state = {"vector_store": {"id": "backup"}}
    second_state = {"vector_store": {"id": "current"}}

    assert persistence.save_qa_state(first_state) is True
    assert persistence.save_qa_state(second_state) is True

    # Corrupt the primary state file to force backup recovery.
    with open(persistence.QA_STATE_FILE, "wb") as handle:
        handle.write(b"corrupted")

    loaded = persistence.load_qa_state()
    assert loaded is not None
    assert loaded["vector_store"]["id"] == "backup"
    assert os.path.isdir(backup_dir)


def test_persistence_rejects_invalid_state_structure(monkeypatch, tmp_path):
    _configure_temp_paths(monkeypatch, tmp_path)

    assert persistence.save_qa_state({"meta": "missing vector store"}) is True

    loaded = persistence.load_qa_state()
    assert loaded is None
