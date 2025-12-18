# ==========================
# Global configuration file
# ==========================
# Centralized configuration used across the AI assistant to ensure
# consistent paths, camera settings, and runtime behavior.

import os

# --------------------------------------------------
# Base installation directory (MUST remain constant)
# --------------------------------------------------
# Raspberry Pi production path (defined by project README)
BASE_DIR = "/opt/ai_assistant"

# --------------------------------------------------
# Paths
# --------------------------------------------------
MODELS_DIR = f"{BASE_DIR}/models"
LOG_DIR = f"{BASE_DIR}/logs"
CAPTURE_DIR = f"{BASE_DIR}/captures"

# --------------------------------------------------
# Models
# --------------------------------------------------
MODEL_PATH = f"{MODELS_DIR}/yolov8n.pt"

# --------------------------------------------------
# Camera configuration
# --------------------------------------------------
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# --------------------------------------------------
# Detection / performance
# --------------------------------------------------
# Run inference every N frames to improve FPS on embedded hardware
INFER_EVERY_N_FRAMES = 3
CONF_THRES = 0.35

# --------------------------------------------------
# Anti-repeat logic
# --------------------------------------------------
MAX_REPEAT = 2
COOLDOWN_SECONDS = 600  # 10 minutes

# --------------------------------------------------
# Database (SQLite)
# --------------------------------------------------
# Default behavior:
# - Raspberry Pi: /opt/ai_assistant/visual_assistant_v1.db
# - WSL / Dev: override with environment variable VA_DB_PATH

DB_ENABLED = True

DB_PATH = os.getenv(
    "VA_DB_PATH",
    f"{BASE_DIR}/visual_assistant_v1.db"
)

# --------------------------------------------------
# Application metadata
# --------------------------------------------------
APP_VERSION = "1.0.0"

# Optional reference to model table (can be NULL)
DEFAULT_MODEL_ID = None

# Device notes (useful for DB audits)
DEVICE_NOTES = os.getenv("VA_DEVICE_NOTES", "Pi5")

# Spoken language code stored in DB
LANGUAGE_CODE = os.getenv("VA_LANG", "en")

