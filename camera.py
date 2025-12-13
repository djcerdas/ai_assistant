from picamera2 import Picamera2
from config import FRAME_WIDTH, FRAME_HEIGHT


def open_camera():
    """Initialize and start the Raspberry Pi camera using Picamera2."""
    picam2 = Picamera2()

    # Use RGB888 so frames are directly compatible with ML models (no color conversion needed)
    cfg = picam2.create_video_configuration(
        main={"size": (FRAME_WIDTH, FRAME_HEIGHT), "format": "RGB888"}
    )

    picam2.configure(cfg)
    picam2.start()
    return picam2


def get_frame(picam2):
    """Capture and return the current camera frame as an RGB NumPy array."""
    return picam2.capture_array()
