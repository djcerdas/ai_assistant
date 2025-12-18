# va_services/runtime.py
from typing import Optional

from va_core.db import Database
from va_core.config import APP_VERSION, DEFAULT_MODEL_ID, DEVICE_NOTES
from va_core.logging_config import get_logger

logger = get_logger(__name__)

class VisualAssistantApplication:
    """
    Representa el bucle principal del asistente, inspirado en el UML:
    - start()
    - stop()
    - runSingleCycle()
    """

    def __init__(self, db: Optional[Database] = None) -> None:
        self.db = db or Database()
        self.is_running: bool = False
        self.main_loop_interval_ms: int = 1000   # 1 segundo (puedes cambiarlo)
        self.current_session_id: Optional[int] = None
        self._frame_counter: int = 0

    def start(self) -> None:
        """Crea la sesión en la BD y marca el asistente como 'en ejecución'."""
        if self.is_running:
            logger.info("El asistente ya está en ejecución.")
            return

        self.current_session_id = self.db.create_run_session(
            app_version=APP_VERSION,
            model_id=DEFAULT_MODEL_ID,
            device_notes=DEVICE_NOTES,
        )
        self._frame_counter = 0
        self.is_running = True
        logger.info("Asistente iniciado con session_id=%s", self.current_session_id)

    def stop(self) -> None:
        """Detiene el asistente y cierra la sesión en la BD."""
        if not self.is_running:
            logger.info("El asistente ya estaba detenido.")
            return

        if self.current_session_id is not None:
            self.db.finish_run_session(self.current_session_id)

        logger.info("Asistente detenido.")
        self.is_running = False
        self.current_session_id = None

    def run_single_cycle(self) -> Optional[int]:
        """
        Simula un ciclo:
          - Procesa un 'frame'
          - Registra un frame_event en la BD
        En el futuro aquí vas a integrar:
          - CameraDevice
          - ObjectDetectionEngine
          - SceneDescriptionRules
          - SpeechSynthesisEngine
        """
        if not self.is_running or self.current_session_id is None:
            return None

        self._frame_counter += 1

        # Por ahora es un demo: detect_ms=0, objects_found=0
        frame_id = self.db.insert_frame_event(
            session_id=self.current_session_id,
            frame_number=self._frame_counter,
            detect_ms=0,
            objects_found=0,
        )

        logger.debug("Ciclo ejecutado: frame #%s -> id=%s", self._frame_counter, frame_id)
        return frame_id

