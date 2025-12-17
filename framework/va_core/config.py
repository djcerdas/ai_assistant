# va_core/config.py
from pathlib import Path

# Ruta a la base de datos SQLite (la que generaste con VAv1_DB_SQLitev3.sql)
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "visual_assistant_v1.db"

APP_VERSION = "1.0.0"
DEFAULT_MODEL_ID = 1      # Asumimos que el modelo YOLOv8-nano tiene id=1 en la tabla model
DEVICE_NOTES = "Dev laptop demo / Raspberry Pi target"

