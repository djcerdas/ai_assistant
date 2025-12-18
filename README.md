AI VISUAL ASSISTANT FOR VISUALLY IMPAIRED USERS (RASPBERRY PI 5)
=======================================================================

OVERVIEW
--------
This project is a production-grade, offline AI visual assistant designed to support
visually impaired users by detecting objects in their environment and providing
real-time spoken feedback.

The system runs entirely on a Raspberry Pi 5, without any cloud dependency, using:
- YOLOv8 for computer vision
- Piper for offline text-to-speech

It demonstrates a complete Edge AI pipeline running locally on embedded hardware.

-----------------------------------------------------------------------

PURPOSE AND SCOPE
-----------------

Purpose:
- Assist visually impaired users by announcing nearby objects such as people,
  chairs, or obstacles.
- Provide real-time situational awareness through audio feedback.
- Serve as a foundation for assistive embedded devices (smart cane, wearable aid).
- Demonstrate an offline, privacy-preserving Edge AI solution.

Scope:
- Object detection using YOLOv8.
- Offline speech synthesis using Piper (English).
- Smart anti-repetition logic with cooldown.
- SQLite-based local persistence of detections and speech events.
- Frame capture with timestamps for debugging and traceability.
- Automatic startup using systemd.
- Raspberry Pi 5 with libcamera / Picamera2.

Out of scope:
- No cloud services.
- No facial recognition.
- No internet required at runtime.
- No remote telemetry.

-----------------------------------------------------------------------

SYSTEM FLOW (LINEAR DESCRIPTION)
--------------------------------
1. Camera frames are captured using libcamera via Picamera2.
2. Frames are processed by a YOLOv8 object detection model.
3. Detection results are evaluated by a decision logic layer implementing:
   - Anti-repeat rules
   - Cooldown timing
4. Relevant detections are converted into speech using offline Piper TTS.
5. Audio feedback is played through a speaker or headphones.
6. All detections and speech events are stored locally in SQLite.
7. An optional observer process can monitor events in real time.

-----------------------------------------------------------------------

HARDWARE COMPONENTS
-------------------

Core components:
- Raspberry Pi 5 (Raspberry Pi OS 64-bit).
- Raspberry Pi Camera Module 3 (Sony IMX708).
- Official Raspberry Pi camera ribbon cable.

Audio:
- Wired USB speaker managed through ALSA.

Power and storage:
- Official Raspberry Pi 5 USB-C power supply (5V / 5A recommended).
- microSD card (64 GB recommended).

Optional but recommended:
- Raspberry Pi case.
- Passive or active cooling (heatsink or fan).

-----------------------------------------------------------------------

SOFTWARE STACK
--------------
- Raspberry Pi OS (64-bit, Bookworm recommended).
- Python 3.
- libcamera and Picamera2.
- Ultralytics YOLOv8.
- Piper offline text-to-speech.
- ALSA audio system.
- SQLite (local persistence).
- systemd (service management).

-----------------------------------------------------------------------

PROJECT STRUCTURE (FIXED PRODUCTION PATH)
-----------------------------------------

/opt/ai_assistant/
├── main.py
├── config.py
├── camera.py
├── vision.py
├── dedupe.py
├── logger_setup.py
├── tts_piper.py
├── va_db.py
├── framework/
│   └── observer.py
├── models/
│   ├── yolov8n.pt
│   └── piper/
│       ├── voice.onnx
│       └── voice.onnx.json
├── tools/
│   └── piper_cli/
├── logs/
├── captures/
├── visual_assistant_v1.db
├── requirements.txt
└── .venv/

-----------------------------------------------------------------------

INSTALLATION (PRODUCTION – SINGLE CORRECT PATH)
-----------------------------------------------

Step 0: Confirm camera operation
--------------------------------
Commands:
```
rpicam-hello
rpicam-still -o /tmp/frame.jpg
```

-----------------------------------------------------------------------

Step 1: System preparation
--------------------------
Commands:
```
sudo apt update
sudo apt install -y   python3   python3-venv   python3-pip   python3-picamera2   python3-opencv   ffmpeg   alsa-utils   pulseaudio   libatlas-base-dev   git
```

-----------------------------------------------------------------------

Step 2: Create application directory
------------------------------------
Commands:
```
sudo mkdir -p /opt/ai_assistant
sudo chown -R $USER:$USER /opt/ai_assistant
```

Clone or copy the project files into:
```
/opt/ai_assistant
```

-----------------------------------------------------------------------

Step 3: Create Python virtual environment
-----------------------------------------
Commands:
```
cd /opt/ai_assistant
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
```

-----------------------------------------------------------------------

Step 4: Install Python dependencies
-----------------------------------
Commands:
```
pip install -r requirements.txt
```

-----------------------------------------------------------------------

Step 5: Create required directories
-----------------------------------
Commands:
```
mkdir -p   /opt/ai_assistant/models/piper   /opt/ai_assistant/tools   /opt/ai_assistant/logs   /opt/ai_assistant/captures
```

-----------------------------------------------------------------------

Step 6: Download YOLO model
---------------------------
Commands:
```
python - <<'PY'
from ultralytics import YOLO
YOLO("yolov8n.pt")
PY

mv yolov8n.pt /opt/ai_assistant/models/yolov8n.pt
```

-----------------------------------------------------------------------

Step 7: Install Piper TTS
-------------------------
Commands:
```
cd /opt/ai_assistant/tools
wget https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_linux_aarch64.tar.gz
tar -xzf piper_linux_aarch64.tar.gz
mv piper piper_cli
chmod +x /opt/ai_assistant/tools/piper_cli/piper
```

-----------------------------------------------------------------------

Step 8: Download English voice model
------------------------------------
Commands:
```
cd /opt/ai_assistant/models/piper

wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/low/en_US-lessac-low.onnx   -O voice.onnx

wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/low/en_US-lessac-low.onnx.json   -O voice.onnx.json
```

-----------------------------------------------------------------------

Step 9: Test Piper audio
------------------------
Commands:
```
echo "Hello. Piper text to speech is working." | /opt/ai_assistant/tools/piper_cli/piper   --model /opt/ai_assistant/models/piper/voice.onnx   --config /opt/ai_assistant/models/piper/voice.onnx.json   --output_file /tmp/piper_test.wav

aplay -q /tmp/piper_test.wav
```

-----------------------------------------------------------------------

Step 10: User permissions
-------------------------
Commands:
```
sudo usermod -aG video,audio,render,input,plugdev $USER
sudo reboot
```

-----------------------------------------------------------------------

MANUAL RUN (VALIDATION)
-----------------------
Commands:
```
cd /opt/ai_assistant
source .venv/bin/activate
python main.py
```

Logs:
```
tail -f /opt/ai_assistant/logs/assistant.log
```

-----------------------------------------------------------------------

FRAMEWORK OBSERVER (OPTIONAL)
-----------------------------
Commands:
```
cd /opt/ai_assistant
source .venv/bin/activate
python framework/observer.py
```

-----------------------------------------------------------------------

SYSTEMD SERVICE (PRODUCTION MODE)
---------------------------------

Service file location:
```
/etc/systemd/system/ai_assistant.service
```

Service content:
```
[Unit]
Description=AI Visual Assistant (YOLO + Piper)
After=multi-user.target sound.target
Wants=sound.target

[Service]
Type=simple
User=pi
Group=pi
WorkingDirectory=/opt/ai_assistant
Environment=PYTHONUNBUFFERED=1
ExecStartPre=/bin/sleep 5
ExecStart=/opt/ai_assistant/.venv/bin/python /opt/ai_assistant/main.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```
sudo systemctl daemon-reload
sudo systemctl enable ai_assistant
sudo systemctl start ai_assistant
```

View service logs:
```
journalctl -u ai_assistant -f
```

-----------------------------------------------------------------------

LICENSE
-------
MIT License
Copyright (c) 2025
David Cerdas Pérez

-----------------------------------------------------------------------

DEVELOPER
---------
Developed and maintained by David Cerdas Pérez as an Edge AI assistive solution
using Raspberry Pi 5, computer vision, and offline speech synthesis.
