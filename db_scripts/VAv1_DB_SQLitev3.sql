/* ============================================================
   VISUAL ASSISTANT V1 — EDGE DATABASE (SQLite 3, 4NF)
   ------------------------------------------------------------
   Hardware : Raspberry Pi 5 (4 GB)
   Flow     : Detect → Describe → Speak
   Scope    : Edge-only with object-level analysis
   Language : English

   =============================================================
   ENTITIES (4NF)
   -------------------------------------------------------------
   1. model          → Local ML model metadata
   2. run_session    → App lifecycle (start / stop)
   3. frame_event    → Each processed frame (timing + count)
   4. detection      → Each object detected in a frame
   5. spoken_message → Text generated to describe detections
   6. audio_event    → Audio playback result
   7. app_error      → Centralized error log
   ============================================================ */

PRAGMA journal_mode = WAL;
PRAGMA synchronous  = NORMAL;
PRAGMA foreign_keys = ON;
PRAGMA temp_store   = MEMORY;

/* -----------------------------
   1) Model used by the system
   ----------------------------- */
CREATE TABLE IF NOT EXISTS model (
  id            INTEGER PRIMARY KEY,            -- Unique numeric ID (auto-incremented by SQLite)
  model_name    TEXT NOT NULL,                  -- Name of the ML model (e.g., "YOLOv8-nano")
  model_version TEXT NOT NULL,                  -- Version of the model (e.g., "0.1-int8")
  model_format  TEXT NOT NULL,                  -- Format type (e.g., "TFLite" or "ONNX")
  file_path     TEXT NOT NULL,                  -- Local filesystem path to the model file on the device
  UNIQUE(model_name, model_version, model_format) -- Prevent duplicate entries of the same model
);

/* ---------------------------------
   2) One row each time the app runs
   --------------------------------- */
CREATE TABLE IF NOT EXISTS run_session (
  id             INTEGER PRIMARY KEY,
  start_time_utc TEXT NOT NULL,   -- ISO 8601 UTC
  end_time_utc   TEXT,            -- filled when app stops
  app_version    TEXT NOT NULL,   -- e.g., "1.0.0"
  model_id       INTEGER REFERENCES model(id)
                     ON UPDATE CASCADE ON DELETE SET NULL,
  device_notes   TEXT             -- e.g., "Pi5, Cam OK, Speaker OK"
);

/* -----------------------------------------------
   3) DETECT → Each processed frame
   ----------------------------------------------- */
CREATE TABLE IF NOT EXISTS frame_event (
  id              INTEGER PRIMARY KEY,
  session_id      INTEGER NOT NULL REFERENCES run_session(id) ON DELETE CASCADE,
  frame_number    INTEGER NOT NULL,       -- sequential per session
  captured_at_utc TEXT    NOT NULL,
  detect_ms       INTEGER NOT NULL,       -- inference time
  objects_found   INTEGER DEFAULT 0,      -- count of detections
  UNIQUE(session_id, frame_number)
);
CREATE INDEX IF NOT EXISTS ix_frame_event_time
  ON frame_event(session_id, captured_at_utc);

/* --------------------------------------------------
   4) DETECT → Each object detected in that frame
   -------------------------------------------------- */
CREATE TABLE IF NOT EXISTS detection (
  id             INTEGER PRIMARY KEY,
  session_id     INTEGER NOT NULL REFERENCES run_session(id) ON DELETE CASCADE,
  frame_id       INTEGER NOT NULL REFERENCES frame_event(id) ON DELETE CASCADE,
  object_label   TEXT    NOT NULL,    -- e.g., "person"
  confidence_0_1 REAL    NOT NULL CHECK(confidence_0_1 BETWEEN 0.0 AND 1.0),
  box_x          INTEGER,
  box_y          INTEGER,
  box_w          INTEGER,
  box_h          INTEGER
);
CREATE INDEX IF NOT EXISTS ix_detection_frame
  ON detection(frame_id);
CREATE INDEX IF NOT EXISTS ix_detection_label
  ON detection(object_label);

/* -----------------------------------------------
   5) DESCRIBE → Message generated for the user
   ----------------------------------------------- */
CREATE TABLE IF NOT EXISTS spoken_message (
  id             INTEGER PRIMARY KEY,
  session_id     INTEGER NOT NULL REFERENCES run_session(id) ON DELETE CASCADE,
  frame_id       INTEGER REFERENCES frame_event(id) ON DELETE SET NULL,
  text_content   TEXT    NOT NULL,   -- e.g., "Person ahead"
  language_code  TEXT    NOT NULL DEFAULT 'es',
  created_at_utc TEXT    NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_message_time
  ON spoken_message(session_id, created_at_utc);

/* -----------------------------------------------
   6) SPEAK → Audio playback outcome
   ----------------------------------------------- */
CREATE TABLE IF NOT EXISTS audio_event (
  id             INTEGER PRIMARY KEY,
  session_id     INTEGER NOT NULL REFERENCES run_session(id)    ON DELETE CASCADE,
  message_id     INTEGER NOT NULL REFERENCES spoken_message(id) ON DELETE CASCADE,
  started_at_utc TEXT    NOT NULL,
  ended_at_utc   TEXT,
  was_successful INTEGER NOT NULL DEFAULT 1 CHECK(was_successful IN (0,1)),
  error_text     TEXT,                   -- only if failed
  output_device  TEXT                    -- e.g., "USB Speaker"
);
CREATE INDEX IF NOT EXISTS ix_audio_event_time
  ON audio_event(session_id, started_at_utc);

/* --------------------------------------------
   7) SUPPORT → Error log for any component
   -------------------------------------------- */
CREATE TABLE IF NOT EXISTS app_error (
  id              INTEGER PRIMARY KEY,
  session_id      INTEGER NOT NULL REFERENCES run_session(id) ON DELETE CASCADE,
  happened_at_utc TEXT    NOT NULL,
  component_name  TEXT    NOT NULL,   -- "CAMERA","DETECTOR","TTS","IO"
  severity        TEXT    NOT NULL CHECK(severity IN ('INFO','WARN','ERROR')),
  short_message   TEXT    NOT NULL,
  long_details    TEXT
);
CREATE INDEX IF NOT EXISTS ix_error_time
  ON app_error(session_id, happened_at_utc);
CREATE INDEX IF NOT EXISTS ix_error_severity
  ON app_error(severity);

/* -----------------------------------
   Seed: minimal model metadata, to test the db.
   ----------------------------------- */
INSERT OR IGNORE INTO model(model_name, model_version, model_format, file_path)
VALUES ('YOLOv8-nano', '0.1-int8', 'TFLite', '/opt/va/models/yolov8n-int8.tflite');
