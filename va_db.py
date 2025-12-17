import sqlite3
from datetime import datetime, timezone
from config import DB_PATH, LANGUAGE_CODE

def _utc_iso():
    return datetime.now(timezone.utc).isoformat()

class VADatabase:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    def _connect(self):
        con = sqlite3.connect(self.db_path, timeout=30)
        con.execute("PRAGMA foreign_keys = ON;")
        return con

    def create_session(self, app_version: str, model_id, device_notes: str | None) -> int:
        con = self._connect()
        try:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO run_session(start_time_utc, app_version, model_id, device_notes) VALUES(?,?,?,?)",
                (_utc_iso(), app_version, model_id, device_notes),
            )
            con.commit()
            return cur.lastrowid
        finally:
            con.close()

    def end_session(self, session_id: int):
        con = self._connect()
        try:
            con.execute("UPDATE run_session SET end_time_utc=? WHERE id=?", (_utc_iso(), session_id))
            con.commit()
        finally:
            con.close()

    def insert_frame_event(self, session_id: int, frame_number: int, detect_ms: int, objects_found: int) -> int:
        con = self._connect()
        try:
            cur = con.cursor()
            cur.execute(
                """INSERT INTO frame_event(session_id, frame_number, captured_at_utc, detect_ms, objects_found)
                   VALUES(?,?,?,?,?)""",
                (session_id, frame_number, _utc_iso(), int(detect_ms), int(objects_found)),
            )
            con.commit()
            return cur.lastrowid
        finally:
            con.close()

    def insert_detection(self, session_id: int, frame_id: int, label: str, confidence: float,
                         box_x=None, box_y=None, box_w=None, box_h=None):
        con = self._connect()
        try:
            con.execute(
                """INSERT INTO detection(session_id, frame_id, object_label, confidence_0_1, box_x, box_y, box_w, box_h)
                   VALUES(?,?,?,?,?,?,?,?)""",
                (session_id, frame_id, label, float(confidence), box_x, box_y, box_w, box_h),
            )
            con.commit()
        finally:
            con.close()

    def insert_spoken_message(self, session_id: int, frame_id: int | None, text: str) -> int:
        con = self._connect()
        try:
            cur = con.cursor()
            cur.execute(
                """INSERT INTO spoken_message(session_id, frame_id, text_content, language_code, created_at_utc)
                   VALUES(?,?,?,?,?)""",
                (session_id, frame_id, text, LANGUAGE_CODE, _utc_iso()),
            )
            con.commit()
            return cur.lastrowid
        finally:
            con.close()

    def start_audio_event(self, session_id: int, message_id: int, output_device: str | None = None) -> int:
        con = self._connect()
        try:
            cur = con.cursor()
            cur.execute(
                """INSERT INTO audio_event(session_id, message_id, started_at_utc, was_successful, output_device)
                   VALUES(?,?,?,?,?)""",
                (session_id, message_id, _utc_iso(), 1, output_device),
            )
            con.commit()
            return cur.lastrowid
        finally:
            con.close()

    def finish_audio_event(self, audio_event_id: int, was_successful: int = 1, error_text: str | None = None):
        con = self._connect()
        try:
            con.execute(
                "UPDATE audio_event SET ended_at_utc=?, was_successful=?, error_text=? WHERE id=?",
                (_utc_iso(), int(was_successful), error_text, audio_event_id),
            )
            con.commit()
        finally:
            con.close()

    def log_error(self, session_id: int, component: str, severity: str, short: str, details: str | None = None):
        con = self._connect()
        try:
            con.execute(
                """INSERT INTO app_error(session_id, happened_at_utc, component_name, severity, short_message, long_details)
                   VALUES(?,?,?,?,?,?)""",
                (session_id, _utc_iso(), component, severity, short, details),
            )
            con.commit()
        finally:
            con.close()

