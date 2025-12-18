djcerdas@DaVo:~$ sudo apt install sqlite3
[sudo] password for djcerdas:
djcerdas@DaVo:~$ sqlite3 visual_assistant_v1.db
SQLite version 3.45.1 2024-01-30 16:01:20
Enter ".help" for usage hints.
sqlite> .read VAv1_DB_SQLitev3.sql
wal
sqlite> .tables
app_error       detection       model           spoken_message
audio_event     frame_event     run_session
sqlite> SELECT * FROM model;
1|YOLOv8-nano|0.1-int8|TFLite|/opt/va/models/yolov8n-int8.tflite
sqlite> .schema model
CREATE TABLE model (
  id            INTEGER PRIMARY KEY,            -- Unique numeric ID (auto-incremented by SQLite)
  model_name    TEXT NOT NULL,                  -- Name of the ML model (e.g., "YOLOv8-nano")
  model_version TEXT NOT NULL,                  -- Version of the model (e.g., "0.1-int8")
  model_format  TEXT NOT NULL,                  -- Format type (e.g., "TFLite" or "ONNX")
  file_path     TEXT NOT NULL,                  -- Local filesystem path to the model file on the device
  UNIQUE(model_name, model_version, model_format) -- Prevent duplicate entries of the same model
);
sqlite>
sqlite> .exit
djcerdas@DaVo:~$