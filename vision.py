from ultralytics import YOLO

# Load YOLOv8 model once at startup to avoid reloading on every frame
model = YOLO("/opt/ai_assistant/models/yolov8n.pt")


def detect(frame):
    """
    Run object detection on a single video frame and return detected labels.
    """
    results = model(frame, verbose=False)
    detections = []

    # Extract class labels from detected bounding boxes
    for r in results:
        for box in r.boxes:
            label = model.names[int(box.cls)]
            detections.append(label)

    return detections
