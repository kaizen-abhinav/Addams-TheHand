# Robotic Hand Control System

This project demonstrates a multi-modal robotic hand control system using an Arduino, servos, OpenCV/Mediapipe for hand tracking, and audio-reactive control. In the future, we plan to integrate EMG control using a BioAmp Biscute module for more intuitive finger movement.

![Project Banner](images/project_banner.jpg)

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Hardware Setup](#hardware-setup)
- [Software Setup](#software-setup)
- [Usage Instructions](#usage-instructions)
- [Code Structure](#code-structure)
- [Demo](#demo)
- [Future Plans](#future-plans)
- [Known Issues](#known-issues)
- [License](#license)

## Overview

The system controls a robotic hand with five servos:
- **2 MG995 Servos** (for thumb and index finger)
- **3 MG90S Servos** (for middle, ring, and pinky)

The control software runs in two modes:
1. **Hand Mode:**  
   Uses OpenCV and Mediapipe to detect hand landmarks and trigger a servo sweep (0° to 180°) when a finger is raised. When no hand is detected, the servos return to a default position (90°).

2. **Audio Mode:**  
   Uses PyAudio to capture audio amplitude and map that value to servo positions (quiet → 90°, loud → 180°). A real-time audio waveform is visualized in the OpenCV window.

## Features

- **Individual Finger Sweep:**  
  Each finger’s corresponding servo sweeps from 0° to 180° every time a finger is raised (transition from "down" to "up").

- **Default Reset:**  
  If the hand is not detected, all servos reset to their default position (set at 90°).

- **Audio-Reactive Control:**  
  In audio mode, all servos react uniformly to the captured audio level, with a waveform visualization for feedback.

- **Mode Switching & Quit Functionality:**  
  Easily switch between hand and audio control modes, and quit the program via keyboard commands.

## Hardware Setup

### Components

- **Arduino Uno**
- **2 × MG995 Servos** (for robust movement)
- **3 × MG90S Servos** (for lighter finger actuation)
- **XL4015E1 Step-down Converter**  
  - Converts a 12V 5A supply to a regulated 5V supply.
- **60W 12V 5A Power Supply**
- **Breadboard and Jumper Wires**
- **Webcam** (for hand tracking)
- **Microphone** (for audio input)
- *(Future)* **BioAmp Biscute** for EMG control

### Wiring Diagram

All servos share a common 5V power supply (from the XL4015 module) and ground. Signal wires are connected to specific Arduino digital pins as follows:

- **Servo 1 (MG995, Thumb):** Arduino Pin **9**
- **Servo 2 (MG995, Index):** Arduino Pin **10**
- **Servo 3 (MG90S, Middle):** Arduino Pin **11**
- **Servo 4 (MG90S, Ring):** Arduino Pin **6**
- **Servo 5 (MG90S, Pinky):** Arduino Pin **5**

![Wiring Diagram](images/wiring_diagram.jpg)

## Software Setup

### Arduino Code

The Arduino sketch listens for serial commands in the format:

The main script is provided in hand_audio_control.py.

Usage Instructions
Arduino:

Open the Arduino IDE.
Load and upload the provided Arduino code.
Verify wiring and connections.
Python:

Ensure the required libraries are installed.
Update the serial port in hand_audio_control.py (e.g., 'COM3' for Windows or '/dev/ttyACM0' for Linux/Mac).
Run the Python script:
bash
Copy
Edit
python hand_audio_control.py
Control Commands:

Press 'h' to switch to hand mode.
Press 'a' to switch to audio mode.
Press 'q' or ESC to quit.
Operation:

Hand Mode:
When a finger is raised (transition from "not raised" to "raised"), the corresponding servo sweeps from 0° to 180°. If no hand is detected, all servos reset to 90°.
Audio Mode:
All servos move in unison based on the audio amplitude, with a visual waveform displayed.
Code Structure
bash
Copy
Edit
/RoboticHandControl
│
├── arduino
│   └── RoboticHandControl.ino     # Arduino sketch
│
├── images
│   ├── project_banner.jpg         # Banner image for the README
│   ├── wiring_diagram.jpg         # Wiring diagram image
│   └── opencv_window.jpg          # Sample screenshot of the OpenCV window
│
├── hand_audio_control.py          # Main Python script for hand/audio control
│
└── README.md                      # This README file
Demo
Insert a demo video or animated GIF here that shows the hand mode, audio mode, and servo sweeps in action.


Future Plans
EMG Control with BioAmp Biscute:
Integrate a BioAmp Biscute module to capture EMG signals for muscle-based control of the robotic hand.

Enhanced Calibration:
Improve mapping functions and calibrate individual finger movements for more precise control.

Additional Gestures and Modes:
Experiment with gesture recognition for advanced functionalities and interactive controls.

Known Issues
Finger Sweep Triggering:
Finger detection uses a simple heuristic. Fine-tuning may be needed in different lighting conditions or hand orientations.

Audio Mode Sensitivity:
Audio amplitude normalization might need adjustments based on microphone sensitivity and ambient noise.

License
This project is licensed under the MIT License. See the LICENSE file for details.

yaml
Copy
Edit
