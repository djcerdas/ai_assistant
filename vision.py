# vision.py
from ultralytics import YOLO

# Load YOLOv8 model once at startup to avoid reloading on every frame
model = YOLO("/opt/ai_assistant/models/yolov8n.pt")


def detect(frame, return_raw: bool = False):
    """
    Run object detection on a single video frame.

    return_raw = False (default):
        Returns a list of labels (backwards compatible with your old code):
            ["person", "chair", ...]

    return_raw = True:
        Returns a list of dicts with label + confidence + bbox (for DB logging):
            [
              {"label": "person", "conf": 0.91, "box_x": 12, "box_y": 34, "box_w": 120, "box_h": 220},
              ...
            ]
    """
    results = model(frame, verbose=False)

    # Backwards compatible mode (your current code expects this)
    if not return_raw:
        detections = []
        for r in results:
            for box in r.boxes:
                label = model.names[int(box.cls)]
                detections.append(label)
        return detections

    # Raw mode (for DB): include confidence and bounding box
    raw = []
    for r in results:
        for box in r.boxes:
            label = model.names[int(box.cls)]

            # confidence is 0..1 and matches DB constraint (confidence_0_1 BETWEEN 0.0 AND 1.0)
            conf = float(box.conf[0]) if box.conf is not None else 0.0

            # Bounding box in xywh (center x/y, width, height)
            xywh = box.xywh[0].tolist()  # [x_center, y_center, w, h]
            x_c, y_c, w, h = [float(v) for v in xywh]

            # Convert to top-left x,y plus width/height (integers)
            x = int(x_c - (w / 2))
            y = int(y_c - (h / 2))

            raw.append(
                {
                    "label": label,
                    "conf": conf,
                    "box_x": x,
                    "box_y": y,
                    "box_w": int(w),
                    "box_h": int(h),
                }
            )

    return raw

