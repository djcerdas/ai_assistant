import sys
import time
import sqlite3
from pathlib import Path

# --- add project root to PYTHONPATH ---
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
# -------------------------------------

from config import DB_PATH


def main():
    print(f"[observer] using DB_PATH={DB_PATH}")
    last_det_id = 0
    last_msg_id = 0

    while True:
        con = sqlite3.connect(DB_PATH, timeout=30)
        try:
            cur = con.cursor()

            cur.execute(
                "SELECT id, object_label, confidence_0_1 "
                "FROM detection WHERE id > ? ORDER BY id ASC LIMIT 20",
                (last_det_id,)
            )
            rows = cur.fetchall()
            for rid, label, conf in rows:
                print(f"[DETECTION] id={rid} label={label} conf={conf}")
                last_det_id = max(last_det_id, rid)

            cur.execute(
                "SELECT id, text_content, language_code "
                "FROM spoken_message WHERE id > ? ORDER BY id ASC LIMIT 20",
                (last_msg_id,)
            )
            rows = cur.fetchall()
            for rid, text, lang in rows:
                print(f"[SPOKEN] id={rid} lang={lang} text={text}")
                last_msg_id = max(last_msg_id, rid)

        finally:
            con.close()

        time.sleep(1.0)


if __name__ == "__main__":
    main()

