import os
import pickle
import gzip
import time
import shutil
import tempfile
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Define file paths for persistence
PERSISTENCE_DIR = "data"
QA_STATE_FILE = os.path.join(PERSISTENCE_DIR, "qa_state.pkl.gz")  # Use gzip compression
BACKUP_DIR = os.path.join(PERSISTENCE_DIR, "backups")

def ensure_persistence_dir():
    """Ensure the persistence directories exist"""
    os.makedirs(PERSISTENCE_DIR, exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)

def create_backup(filename: str) -> bool:
    """Create a backup of the state file

    Args:
        filename: Path to the file to backup

    Returns:
        bool: True if backup was successful
    """
    if not os.path.exists(filename):
        return False

    try:
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        backup_filename = os.path.join(BACKUP_DIR, f"qa_state-{timestamp}.pkl.gz")
        shutil.copy2(filename, backup_filename)
        logger.info(f"Created backup at {backup_filename}")

        # Clean up old backups (keep only 5 most recent)
        backups = sorted([
            os.path.join(BACKUP_DIR, f) for f in os.listdir(BACKUP_DIR)
            if f.startswith("qa_state-") and f.endswith(".pkl.gz")
        ])

        for old_backup in backups[:-5]:
            os.remove(old_backup)
            logger.debug(f"Removed old backup: {old_backup}")

        return True
    except Exception as e:
        logger.error(f"Failed to create backup: {e}")
        return False

def save_qa_state(state: Dict[str, Any]) -> bool:
    """Save the QA system state to disk with compression and atomic write

    Args:
        state: Dictionary containing the QA system state

    Returns:
        bool: True if saved successfully, False otherwise
    """
    ensure_persistence_dir()
import os
import pickle
import logging
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

# Default state file path
STATE_FILE_PATH = os.environ.get("STATE_FILE_PATH", "qa_state.pkl")

def save_qa_state(state: Dict[str, Any], file_path: Optional[str] = None) -> bool:
    """
    Save QA state to a file

    Args:
        state: The state dictionary to save
        file_path: Optional custom file path

    Returns:
        True if successful, False otherwise
    """
    try:
        path = file_path or STATE_FILE_PATH
        with open(path, "wb") as f:
            pickle.dump(state, f)
        logger.info(f"Saved state to {path}")
        return True
    except Exception as e:
        logger.error(f"Error saving state: {e}")
        return False

def load_qa_state(file_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Load QA state from a file

    Args:
        file_path: Optional custom file path

    Returns:
        State dictionary if successful, None otherwise
    """
    try:
        path = file_path or STATE_FILE_PATH
        if not os.path.exists(path):
            logger.info(f"No state file found at {path}")
            return None

        with open(path, "rb") as f:
            state = pickle.load(f)
        logger.info(f"Loaded state from {path}")
        return state
    except Exception as e:
        logger.error(f"Error loading state: {e}")
        return None
    # Create backup of existing file
    if os.path.exists(QA_STATE_FILE):
        create_backup(QA_STATE_FILE)

    # Use atomic write pattern with temporary file
    temp_file = None
    try:
        # Create temporary file
        temp_fd, temp_file = tempfile.mkstemp(dir=PERSISTENCE_DIR, suffix=".tmp.gz")
        os.close(temp_fd)

        # Save state to temporary file with compression
        start_time = time.time()
        with gzip.open(temp_file, 'wb', compresslevel=6) as f:
            pickle.dump(state, f, protocol=pickle.HIGHEST_PROTOCOL)

        # Atomic move to final location
        shutil.move(temp_file, QA_STATE_FILE)

        # Get file size for logging
        file_size = os.path.getsize(QA_STATE_FILE)
        save_time = time.time() - start_time
        logger.info(f"QA state saved to {QA_STATE_FILE} ({file_size/1024:.1f} KB) in {save_time:.2f} seconds")
        return True
    except Exception as e:
        logger.error(f"Failed to save QA state: {e}")
        return False
    finally:
        # Clean up temporary file if still exists
        if temp_file and os.path.exists(temp_file):
            try:
                os.unlink(temp_file)
            except Exception:
                pass

def load_qa_state() -> Optional[Dict[str, Any]]:
    """Load the QA system state from disk with compression support

    Returns:
        Optional[Dict[str, Any]]: The QA system state if it exists, None otherwise
    """
    # Check for new compressed format
    if os.path.exists(QA_STATE_FILE):
        try:
            start_time = time.time()
            with gzip.open(QA_STATE_FILE, 'rb') as f:
                state = pickle.load(f)
            load_time = time.time() - start_time
            file_size = os.path.getsize(QA_STATE_FILE)
            logger.info(f"QA state loaded from {QA_STATE_FILE} ({file_size/1024:.1f} KB) in {load_time:.2f} seconds")
            return state
        except Exception as e:
            logger.error(f"Failed to load compressed QA state: {e}")

            # Try to recover from backup
            try:
                backups = sorted([
                    os.path.join(BACKUP_DIR, f) for f in os.listdir(BACKUP_DIR)
                    if f.startswith("qa_state-") and f.endswith(".pkl.gz")
                ], reverse=True)

                if backups:
                    latest_backup = backups[0]
                    logger.info(f"Attempting to recover from backup: {latest_backup}")
                    with gzip.open(latest_backup, 'rb') as f:
                        state = pickle.load(f)
                    logger.info(f"Successfully recovered from backup")
                    return state
            except Exception as backup_error:
                logger.error(f"Failed to recover from backup: {backup_error}")

    # Check for old uncompressed format as fallback
    old_file = os.path.join(PERSISTENCE_DIR, "qa_state.pkl")
    if os.path.exists(old_file):
        logger.info(f"Found old format state file, attempting to load")
        try:
            with open(old_file, 'rb') as f:
                state = pickle.load(f)
            logger.info(f"QA state loaded from old format file {old_file}")

            # Save in new format for future use
            save_qa_state(state)

            # Remove old format file after successful conversion
            try:
                os.rename(old_file, f"{old_file}.converted")
                logger.info(f"Renamed old format file to {old_file}.converted")
            except Exception as e:
                logger.warning(f"Could not rename old format file: {e}")

            return state
        except Exception as e:
            logger.error(f"Failed to load old format QA state: {e}")

    logger.info(f"No valid QA state file found")
    return None
