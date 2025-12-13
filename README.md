AI VISUAL ASSISTANT FOR VISUALLY IMPAIRED USERS (RASPBERRY PI 5)

OVERVIEW
This project is a prototype of an AI-powered visual assistant designed to help visually impaired users by detecting objects in their environment and providing spoken feedback in real time. The system runs fully offline on a Raspberry Pi 5, using computer vision (YOLOv8) and offline text-to-speech (Piper). 

PURPOSE AND SCOPE
Purpose:
- Assist visually impaired users by announcing nearby objects such as people, chairs, or obstacles.
- Serve as a foundation for a smart cane or wearable assistive device.
- Demonstrate a complete Edge AI pipeline running locally on embedded hardware.

Scope:
- Object detection using YOLOv8.
- Offline speech synthesis using Piper (English).
- Smart anti-repetition logic with cooldown.
- Frame capture with timestamps for debugging and evidence.
- Automatic startup using systemd.
- Raspberry Pi 5 with libcamera (Picamera2).

Out of scope:
- No cloud dependency.
- No facial recognition.
- No internet required at runtime.

SYSTEM FLOW (LINEAR DESCRIPTION)
Camera input is captured using libcamera via Picamera2, frames are processed by a YOLO-based object detection model, detection results are evaluated by a decision logic layer implementing anti-repeat and cooldown rules, relevant events are converted to speech using offline Piper text-to-speech, and audio feedback is delivered through a speaker or headphones.

HARDWARE COMPONENTS 
Core components:
- Raspberry Pi 5 running Raspberry Pi OS 64-bit.
- Raspberry Pi Camera Module 3 (Sony IMX708 sensor) connected via CSI ribbon cable.
- Official Raspberry Pi camera ribbon cable.

Audio:
- Wired speaker using USB, managed through ALSA.

Power and storage:
- Official Raspberry Pi 5 USB-C power supply (5V / 5A recommended).
- microSD card, 64 GB recommended.

Optional but recommended:
- Raspberry Pi case.
- Passive or active cooling (heatsink or fan).

SOFTWARE STACK
- Raspberry Pi OS (64-bit).
- Python 3.
- Picamera2 and libcamera.
- Ultralytics YOLOv8.
- Piper offline text-to-speech.
- ALSA audio system.
- systemd for service management.

PROJECT STRUCTURE (FIXED PATH)
/opt/ai_assistant/
- src: application source code (main.py, camera.py, vision.py, dedupe.py, tts_piper.py, logger_setup.py, config.py)
- models: YOLO model and Piper voice models
- tools: Piper CLI binary
- logs: runtime logs
- captures: saved frames with timestamps
- venv: Python virtual environment

Step 0: Confirm camera works 
Run these to confirm the camera module is detected and working.
Commands:
- rpicam-hello
- rpicam-still -o /tmp/frame.jpg

Step 1: System preparation
Install required system packages including Python, Picamera2, FFmpeg, ALSA utilities, and numerical libraries.
Commands:
- sudo apt update
- sudo apt install -y python3 python3-venv python3-pip python3-picamera2 ffmpeg alsa-utils libatlas-base-dev

Step 2: Create project directory under /opt
Commands:
- sudo mkdir -p /opt/ai_assistant
- sudo chown -R $USER:$USER /opt/ai_assistant

Step 3: Create Python virtual environment (Picamera2 is system-installed)
Important: The virtual environment must be created with system-site-packages enabled so Picamera2 is available.
Commands:
- python3 -m venv --system-site-packages /opt/ai_assistant/venv
- source /opt/ai_assistant/venv/bin/activate

Step 4: Install Python dependencies
Commands:
- pip install --upgrade pip
- pip install ultralytics loguru opencv-python numpy

Step 5: Create required folders
Commands:
- mkdir -p /opt/ai_assistant/src /opt/ai_assistant/models /opt/ai_assistant/models/piper /opt/ai_assistant/tools /opt/ai_assistant/logs /opt/ai_assistant/captures

Step 6: Download YOLO model (yolov8n.pt) into /opt/ai_assistant/models
Commands:
- python - <<'PY'
from ultralytics import YOLO
YOLO("yolov8n.pt")
PY
- mv yolov8n.pt /opt/ai_assistant/models/yolov8n.pt

Step 7: Install Piper TTS (offline, aarch64)
Commands:
- cd /opt/ai_assistant/tools
- wget https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_linux_aarch64.tar.gz
- tar -xzf piper_linux_aarch64.tar.gz
- mv piper piper_cli
- chmod +x /opt/ai_assistant/tools/piper_cli/piper

Step 8: Download English voice model (Lessac, low)
Commands:
- cd /opt/ai_assistant/models/piper
- wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/low/en_US-lessac-low.onnx -O voice.onnx
- wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/low/en_US-lessac-low.onnx.json -O voice.onnx.json

Step 9: Piper audio test (must work before continuing)
Commands:
- echo "Hello. Piper text to speech is working." | /opt/ai_assistant/tools/piper_cli/piper --model /opt/ai_assistant/models/piper/voice.onnx --config /opt/ai_assistant/models/piper/voice.onnx.json --output_file /tmp/piper_test.wav
- aplay -q /tmp/piper_test.wav

Step 10: User permissions (critical)
Add the user to video, audio, render, input, and plugdev groups, then reboot.
Commands:
- sudo usermod -aG video,audio,render,input,plugdev $USER
- sudo reboot

Step 11: Manual run (development / validation mode)
Important: Do not run manual mode while the systemd service is running. Only one process can own the camera.
Commands:
- cd /opt/ai_assistant/src
- source /opt/ai_assistant/venv/bin/activate
- python main.py

Logs:
- tail -f /opt/ai_assistant/logs/assistant.log

SYSTEMD SERVICE (PRODUCTION MODE)
The assistant is designed to run as a systemd service. The service must run as a non-root user, set PYTHONPATH explicitly, wait for audio initialization, ensure only one camera owner exists, and restart automatically on failure.

Create the service file:
- sudo vi /etc/systemd/system/ai_assistant.service

Service file content:
[Unit]
Description=AI Assistant (YOLO + Piper TTS)
After=multi-user.target sound.target
Wants=sound.target

[Service]
Type=simple
User=djadmin
Group=djadmin
WorkingDirectory=/opt/ai_assistant/src
Environment=PYTHONUNBUFFERED=1
Environment=PYTHONPATH=/opt/ai_assistant/src
Environment=HOME=/home/djadmin
ExecStartPre=/bin/sleep 5
ExecStartPre=-/usr/bin/pkill -f "python main.py"
ExecStart=/opt/ai_assistant/venv/bin/python /opt/ai_assistant/src/main.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target

Enable and start the service:
- sudo systemctl daemon-reload
- sudo systemctl enable ai_assistant
- sudo systemctl start ai_assistant

Restart and status:
- sudo systemctl restart ai_assistant
- sudo systemctl status ai_assistant --no-pager

Service logs:
- journalctl -u ai_assistant -f

Important usage rule:
- If the service is running, do not execute python main.py manually.
- If you need to run manually for testing, stop the service first:
  - sudo systemctl stop ai_assistant

ANTI-REPETITION LOGIC
Each detected object is spoken a maximum of two times. After reaching this limit, a cooldown of ten minutes is enforced. Logging continues even when speech is suppressed. This behavior prevents audio overload and improves usability for visually impaired users.

RUNNING THE APPLICATION (SUMMARY)
Manual mode:
- sudo systemctl stop ai_assistant
- cd /opt/ai_assistant/src
- source /opt/ai_assistant/venv/bin/activate
- python main.py

Production mode (systemd):
- sudo systemctl start ai_assistant
- journalctl -u ai_assistant -f

FUTURE IMPROVEMENTS
- Natural spoken phrases such as "Person ahead".
- Closest-object prioritization.
- Distance-based alerts.
- Beep plus voice user experience.
- GPIO button integration.
- Model optimization using TFLite or INT8.

LICENSE
MIT License
Copyright (c) 2025 David Cerdas Pérez
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files to deal in the software without restriction, including the rights to use, copy, modify, merge, publish, distribute, sublicense, and sell copies of the software.

The software is provided "as is", without warranty of any kind, express or implied.

DEVELOPER
Developed and maintained by David Cerdas Pérez as an Edge AI assistive solution using Raspberry Pi 5, computer vision, and offline speech synthesis.
