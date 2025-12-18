# va_core/db.py
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

from .config import DB_PATH
from .logging_config import get_logger

logger = get_logger(__name__)

class Database:
    """Pequeño wrapper para la base de datos Visual Assistant V1 (SQLite 3)."""

    def __init__(self, db_path: Path | str = DB_PATH) -> None:
        self.db_path = Path(db_path)

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    # ========== RUN_SESSION ==========

    def create_run_session(
        self,
        app_version: str,
        model_id: Optional[int] = None,
        device_notes: Optional[str] = None,
    ) -> int:
        """Crea un registro en run_session cuando el asistente se inicia."""
        conn = self._connect()
        try:
            cur = conn.cursor()
            now_utc = datetime.now(timezone.utc).isoformat()

            cur.execute(
                """
                INSERT INTO run_session(
                    start_time_utc, app_version, model_id, device_notes
                )
                VALUES (?, ?, ?, ?)
                """,
                (now_utc, app_version, model_id, device_notes),
            )
            session_id = cur.lastrowid
            conn.commit()
            logger.info("Nueva run_session creada con id=%s", session_id)
            return session_id
        finally:
            conn.close()

    def finish_run_session(self, session_id: int) -> None:
        """Marca el fin de una run_session."""
        conn = self._connect()
        try:
            cur = conn.cursor()
            now_utc = datetime.now(timezone.utc).isoformat()
            cur.execute(
                "UPDATE run_session SET end_time_utc=? WHERE id=?",
                (now_utc, session_id),
            )
            conn.commit()
            logger.info("run_session id=%s finalizada", session_id)
        finally:
            conn.close()

    # ========== FRAME_EVENT ==========

    def insert_frame_event(
        self,
        session_id: int,
        frame_number: int,
        detect_ms: int,
        objects_found: int,
    ) -> int:
        """
        Inserta un frame_event mínimo, enlazado con la sesión.
        Tabla según VAv1_DB_SQLitev3.sql:
          id, session_id, frame_number, captured_at_utc, detect_ms, objects_found
        """
        conn = self._connect()
        try:
            cur = conn.cursor()
            now_utc = datetime.now(timezone.utc).isoformat()
            cur.execute(
                """
                INSERT INTO frame_event(
                    session_id, frame_number, captured_at_utc, detect_ms, objects_found
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (session_id, frame_number, now_utc, detect_ms, objects_found),
            )
            frame_id = cur.lastrowid
            conn.commit()
            logger.debug(
                "frame_event insertado (session_id=%s, frame_number=%s, id=%s)",
                session_id,
                frame_number,
                frame_id,
            )
            return frame_id
        finally:
            conn.close()


