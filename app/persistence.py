import gzip
import logging
import os
import pickle
import shutil
import tempfile
import time
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

PERSISTENCE_DIR = "data"
QA_STATE_FILE = os.path.join(PERSISTENCE_DIR, "qa_state.pkl.gz")
LEGACY_STATE_FILE = os.path.join(PERSISTENCE_DIR, "qa_state.pkl")
BACKUP_DIR = os.path.join(PERSISTENCE_DIR, "backups")
MAX_BACKUPS = 5


def ensure_persistence_dir() -> None:
    """Ensure persistence and backup directories exist."""
    os.makedirs(PERSISTENCE_DIR, exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)


def _is_valid_state(state: Any) -> bool:
    """Validate shape of persisted QA state before returning it to callers."""
    return isinstance(state, dict) and "vector_store" in state


def create_backup(filename: str) -> bool:
    """Create a timestamped backup and rotate old backups."""
    if not os.path.exists(filename):
        return False

    ensure_persistence_dir()
    try:
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        backup_filename = os.path.join(BACKUP_DIR, f"qa_state-{timestamp}.pkl.gz")
        shutil.copy2(filename, backup_filename)

        backups = sorted(
            os.path.join(BACKUP_DIR, entry)
            for entry in os.listdir(BACKUP_DIR)
            if entry.startswith("qa_state-") and entry.endswith(".pkl.gz")
        )
        for old_backup in backups[:-MAX_BACKUPS]:
            os.remove(old_backup)

        logger.info("Created state backup at %s", backup_filename)
        return True
    except Exception as exc:
        logger.error("Failed to create backup: %s", exc)
        return False


def save_qa_state(state: Dict[str, Any]) -> bool:
    """Persist QA state to disk using gzip compression and atomic move."""
    if not isinstance(state, dict):
        logger.error("Failed to save QA state: state must be a dictionary")
        return False

    ensure_persistence_dir()
    if os.path.exists(QA_STATE_FILE):
        create_backup(QA_STATE_FILE)

    temp_file: Optional[str] = None
    try:
        fd, temp_file = tempfile.mkstemp(dir=PERSISTENCE_DIR, suffix=".tmp.gz")
        os.close(fd)

        start_time = time.time()
        with gzip.open(temp_file, "wb", compresslevel=6) as handle:
            pickle.dump(state, handle, protocol=pickle.HIGHEST_PROTOCOL)

        shutil.move(temp_file, QA_STATE_FILE)
        file_size_kb = os.path.getsize(QA_STATE_FILE) / 1024
        logger.info(
            "QA state saved to %s (%.1f KB) in %.2f seconds",
            QA_STATE_FILE,
            file_size_kb,
            time.time() - start_time,
        )
        return True
    except Exception as exc:
        logger.error("Failed to save QA state: %s", exc)
        return False
    finally:
        if temp_file and os.path.exists(temp_file):
            try:
                os.unlink(temp_file)
            except OSError:
                pass


def _load_gzip_state(file_path: str) -> Optional[Dict[str, Any]]:
    """Load and validate a gzip-compressed state file."""
    try:
        with gzip.open(file_path, "rb") as handle:
            state = pickle.load(handle)
        if not _is_valid_state(state):
            logger.warning("Ignoring invalid state structure in %s", file_path)
            return None
        return state
    except Exception as exc:
        logger.error("Failed to load gzip state from %s: %s", file_path, exc)
        return None


def _load_legacy_state() -> Optional[Dict[str, Any]]:
    """Load legacy uncompressed state format and migrate it."""
    if not os.path.exists(LEGACY_STATE_FILE):
        return None

    logger.info("Found legacy state file at %s; attempting migration", LEGACY_STATE_FILE)
    try:
        with open(LEGACY_STATE_FILE, "rb") as handle:
            state = pickle.load(handle)
        if not _is_valid_state(state):
            logger.warning("Ignoring invalid legacy state structure")
            return None

        if save_qa_state(state):
            try:
                os.rename(LEGACY_STATE_FILE, f"{LEGACY_STATE_FILE}.converted")
            except OSError as exc:
                logger.warning("Could not rename legacy state file: %s", exc)
        return state
    except Exception as exc:
        logger.error("Failed to load legacy state file: %s", exc)
        return None


def load_qa_state() -> Optional[Dict[str, Any]]:
    """Load QA state from primary storage, backups, or legacy format."""
    ensure_persistence_dir()

    if os.path.exists(QA_STATE_FILE):
        state = _load_gzip_state(QA_STATE_FILE)
        if state is not None:
            logger.info("QA state loaded from %s", QA_STATE_FILE)
            return state

        backups = sorted(
            (
                os.path.join(BACKUP_DIR, entry)
                for entry in os.listdir(BACKUP_DIR)
                if entry.startswith("qa_state-") and entry.endswith(".pkl.gz")
            ),
            reverse=True,
        )
        for backup in backups:
            logger.info("Attempting recovery from backup %s", backup)
            state = _load_gzip_state(backup)
            if state is not None:
                logger.info("Recovered QA state from backup")
                return state

    state = _load_legacy_state()
    if state is not None:
        logger.info("QA state loaded from legacy format")
        return state

    logger.info("No valid QA state file found")
    return None
