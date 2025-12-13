# ==========================
# Global configuration file
# ==========================
# Centralized configuration used across the AI assistant to ensure
# consistent paths, camera settings, and runtime behavior.

# Base installation directory (must remain constant)
BASE_DIR = "/opt/ai_assistant"

# --------------------------
# Paths
# --------------------------
# Directory locations used by the application
MODELS_DIR = f"{BASE_DIR}/models"
LOG_DIR = f"{BASE_DIR}/logs"
CAPTURE_DIR = f"{BASE_DIR}/captures"

# --------------------------
# Models
# --------------------------
# YOLO object detection model path
MODEL_PATH = f"{MODELS_DIR}/yolov8n.pt"

# --------------------------
# Camera configuration
# --------------------------
# Fixed resolution used for performance and stability
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# --------------------------
# Detection / performance
# --------------------------
# Run inference every N frames to improve FPS on embedded hardware
INFER_EVERY_N_FRAMES = 3
CONF_THRES = 0.35

# --------------------------
# Anti-repeat logic
# --------------------------
# Limit repeated speech for the same detected object
MAX_REPEAT = 2
COOLDOWN_SECONDS = 600  # 10 minutes
