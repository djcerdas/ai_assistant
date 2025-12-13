from loguru import logger
from config import LOG_DIR
import os

# Ensure log directory exists before configuring the logger
os.makedirs(LOG_DIR, exist_ok=True)

# Configure file-based logging with rotation and a clear timestamped format
logger.add(
    f"{LOG_DIR}/assistant.log",
    rotation="10 MB",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)


def log_detected(labels):
    """Log detected object labels."""
    logger.info(f"DETECTED: {labels}")


def log_spoken(label):
    """Log labels that were spoken aloud."""
    logger.info(f"SPOKEN: {label}")


def log_saved(path):
    """Log saved frame paths."""
    logger.info(f"FRAME_SAVED: {path}")
