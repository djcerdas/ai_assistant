import time

from camera import open_camera, get_frame
from vision import detect
from dedupe import DedupeSpeaker
from tts_piper import speak
from logger_setup import log_detected, log_spoken
from va_db import VADatabase
from config import (
    INFER_EVERY_N_FRAMES, CONF_THRES,
    DB_ENABLED, APP_VERSION, DEFAULT_MODEL_ID, DEVICE_NOTES
)


def main():
    db = VADatabase() if DB_ENABLED else None
    session_id = None

    if db:
        session_id = db.create_session(APP_VERSION, DEFAULT_MODEL_ID, DEVICE_NOTES)

    dedupe = DedupeSpeaker()
    picam2 = open_camera()

    frame_number = 0

    try:
        while True:
            frame = get_frame(picam2)
            frame_number += 1

            # performance: run inference every N frames
            if frame_number % INFER_EVERY_N_FRAMES != 0:
                continue

            t0 = time.time()

            # raw detections (label/conf/bbox) for DB
            raw = detect(frame, return_raw=True)

            # filter by confidence threshold
            raw = [d for d in raw if float(d.get("conf", 0.0)) >= CONF_THRES]

            detect_ms = int((time.time() - t0) * 1000)
            labels = [d["label"] for d in raw]

            log_detected(labels)

            frame_id = None
            if db and session_id is not None:
                frame_id = db.insert_frame_event(
                    session_id=session_id,
                    frame_number=frame_number,
                    detect_ms=detect_ms,
                    objects_found=len(raw)
                )
                for d in raw:
                    db.insert_detection(
                        session_id=session_id,
                        frame_id=frame_id,
                        label=d["label"],
                        confidence=float(d["conf"]),
                        box_x=d.get("box_x"),
                        box_y=d.get("box_y"),
                        box_w=d.get("box_w"),
                        box_h=d.get("box_h"),
                    )

            # speak logic (anti-repeat)
            current = set(labels)
            for label in current:
                if not dedupe.should_speak(label, current):
                    continue

                text = label  # minimal: speak label only (keep behavior simple)
                message_id = None
                audio_event_id = None

                if db and session_id is not None:
                    message_id = db.insert_spoken_message(session_id, frame_id, text)
                    audio_event_id = db.start_audio_event(session_id, message_id, output_device="USB Speaker")

                try:
                    speak(text)
                    dedupe.mark_spoken(label)
                    log_spoken(label)
                    if db and audio_event_id is not None:
                        db.finish_audio_event(audio_event_id, was_successful=1)
                except Exception as e:
                    if db and audio_event_id is not None:
                        db.finish_audio_event(audio_event_id, was_successful=0, error_text=str(e))
                    if db and session_id is not None:
                        db.log_error(session_id, "TTS", "ERROR", "TTS failed", str(e))

            time.sleep(0.01)

    except KeyboardInterrupt:
        pass
    except Exception as e:
        if db and session_id is not None:
            db.log_error(session_id, "RUNTIME", "ERROR", "Main loop crashed", str(e))
        raise
    finally:
        try:
            picam2.stop()
        except Exception:
            pass

        if db and session_id is not None:
            db.end_session(session_id)


if __name__ == "__main__":
    main()

