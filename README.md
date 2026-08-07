# Voice-Automated Autonomous Driving Simulation

This project is a lightweight autonomous driving agent for a simulator, enhanced with real-time voice control. It uses a trained Keras/TensorFlow deep learning model to predict steering angles from camera images, while running a parallel microservice to listen for specific vocal commands. This allows the user to manually override the autonomous system to stop, resume, or force directional turns using just their voice.

## What the Project Does

The system utilizes a dual-process architecture to prevent the deep learning driving model from bottlenecking the speech recognition engine:

1. **The Autonomous Engine (`drive.py`):** Receives telemetry data (speed, camera images) from the simulator via Socket.IO, preprocesses the images, predicts the steering angle using a loaded neural network, and computes throttle.
2. **The Voice Controller (`voice_controller.py`):** Runs in a separate terminal, continuously listening for specific keywords (Stop, Start, Left, Right) using Google Speech Recognition.
3. **The UDP Bridge:** When a voice command is recognized, the voice controller instantly sends a UDP network packet to the autonomous engine to override the throttle and steering values in real time.

## Project Files

- `Udacity Car Sim` - [https://github.com/udacity/self-driving-car-sim](https://github.com/udacity/self-driving-car-sim)
- `drive.py` - Main server script that loads the model, receives simulator telemetry, listens for UDP voice overrides, and sends driving commands back to the simulator.
- `voice_controller.py` - The independent voice-listening microservice that captures microphone input, filters for specific keywords, and transmits overrides to `drive.py`.
- `model.h5` - Pretrained Keras model used for inference.
- `requirements.txt` - Python dependencies required to run the project.
- `Training Data Drive Link` - [https://drive.google.com/file/d/1RjGounrgGelA2gwDLPSdO-lz11vN8pOx/view?usp=sharing](https://drive.google.com/file/d/1RjGounrgGelA2gwDLPSdO-lz11vN8pOx/view?usp=sharing)

## Supported Voice Commands

The voice controller uses strict keyword filtering to ignore background noise and only act on specific triggers:

*   **"Stop"** (or "Brake"): Overrides the model, applies full negative throttle (-1.0), and halts the car.
*   **"Start"** (or "Forward", "Go", "Resume"): Releases manual overrides and hands control back to the autonomous neural network.
*   **"Left":** Forces the car to steer hard left (Steering Angle: -1.0).
*   **"Right":** Forces the car to steer hard right (Steering Angle: 1.0).

## Requirements

This project depends on:

- Python 3
- TensorFlow / Keras
- Flask & Flask-SocketIO
- Eventlet
- NumPy
- OpenCV & Pillow
- h5py
- SpeechRecognition
- PyAudio

## Setup

1. Create and activate a Python virtual environment.
2. Install the required dependencies:

```bash
pip install -r requirements.txt
pip install SpeechRecognition pyaudio
