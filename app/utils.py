import os
import time
import logging
from typing import Dict, Any, Callable, Optional
from functools import wraps
from datetime import datetime

logger = logging.getLogger(__name__)

# Check if memory monitoring is enabled
MEMORY_MONITORING = os.getenv("MEMORY_MONITORING", "false").lower() in ("true", "1", "t")

# Try to import psutil for memory monitoring
try:
    import psutil
    _process = psutil.Process()
    _has_psutil = True
except ImportError:
    _has_psutil = False
    if MEMORY_MONITORING:
        logger.warning("psutil not installed, memory monitoring disabled. Install with: pip install psutil")

def get_memory_usage() -> Dict[str, float]:
    """Get current memory usage in MB"""
    if not _has_psutil:
        return {}

    try:
        memory_info = _process.memory_info()
        return {
            "rss_mb": memory_info.rss / (1024 * 1024),
            "vms_mb": memory_info.vms / (1024 * 1024)
        }
    except Exception as e:
        logger.error(f"Error getting memory usage: {e}")
        return {}

def timed_function(func: Callable) -> Callable:
    """Decorator to time function execution"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        start_memory = get_memory_usage() if MEMORY_MONITORING else {}

        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = time.time()
            execution_time = end_time - start_time

            # Log execution time
            logger.info(f"{func.__name__} executed in {execution_time:.4f} seconds")

            # Log memory usage if enabled
            if MEMORY_MONITORING and start_memory:
                end_memory = get_memory_usage()
                memory_diff = {
                    k: end_memory.get(k, 0) - start_memory.get(k, 0)
                    for k in set(end_memory) | set(start_memory)
                }
                logger.info(f"Memory change during {func.__name__}: {memory_diff}")

    return wrapper

def format_size(size_bytes: int) -> str:
    """Format size in bytes to human readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes/1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes/(1024*1024):.2f} MB"
    else:
        return f"{size_bytes/(1024*1024*1024):.2f} GB"
