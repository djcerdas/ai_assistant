# va_domain/models.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class ModelMetadata:
    id: int
    model_name: str
    model_version: str
    model_format: str
    file_path: str

@dataclass
class RunSession:
    id: int
    start_time_utc: str
    end_time_utc: Optional[str]
    app_version: str
    model_id: Optional[int]
    device_notes: Optional[str]

@dataclass
class FrameEvent:
    id: int
    session_id: int
    frame_number: int
    captured_at_utc: str
    detect_ms: int
    objects_found: int

