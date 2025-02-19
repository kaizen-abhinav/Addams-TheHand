import cv2
import mediapipe as mp
import serial
import time
import numpy as np
import threading
import pyaudio

# ---------------------------
# Serial Setup
# ---------------------------
ser = serial.Serial('COM4', 9600, timeout=1)  # Adjust port as needed
time.sleep(2)  # Allow serial connection to establish

# ---------------------------
# Global Mode Variable & Quit Flag
# ---------------------------
mode = "hand"  # Modes: "hand" or "audio"
mode_lock = threading.Lock()
quit_flag = False

# ---------------------------
# Mediapipe Hand Setup
# ---------------------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

# ---------------------------
# Audio Setup (PyAudio)
# ---------------------------
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
audio_level = 0.0
audio_samples = np.zeros(CHUNK)

def audio_listener():
    global audio_level, audio_samples, quit_flag
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    while not quit_flag:
        try:
            data = stream.read(CHUNK, exception_on_overflow=False)
        except Exception:
            continue
        samples = np.frombuffer(data, dtype=np.int16).astype(np.float32)
        audio_samples = samples  # For waveform visualization
        rms = np.sqrt(np.mean(samples**2))
        audio_level = min(rms / 3000.0, 1.0)
    stream.stop_stream()
    stream.close()
    p.terminate()

audio_thread = threading.Thread(target=audio_listener, daemon=True)
audio_thread.start()

# ---------------------------
# Helper Functions
# ---------------------------
def send_servo_command(finger, angle):
    """Send command to Arduino."""
    command = f"{finger}:{angle}\n"
    ser.write(command.encode())
    print("Sent:", command.strip())

def sweep_finger(finger):
    """Sweep the servo for a given finger from 0° to 180°,
    then reset the sweeping flag for that finger."""
    for angle in range(0, 181, 10):
        send_servo_command(finger, angle)
        time.sleep(0.02)
    # Ensure it stays at 180 at the end of the sweep
    send_servo_command(finger, 180)
    sweeping[finger] = False  # Reset flag when done

def draw_audio_waveform(frame, samples):
    """Draw an audio waveform at the bottom of the frame."""
    h, w, _ = frame.shape
    waveform_height = 100
    overlay = np.zeros((waveform_height, w, 3), dtype=np.uint8)
    if np.max(np.abs(samples)) > 0:
        norm_samples = (samples / np.max(np.abs(samples))) * (waveform_height / 2 - 10)
    else:
        norm_samples = samples
    center_y = waveform_height // 2
    points = []
    step = max(1, len(norm_samples) // w)
    for i in range(0, len(norm_samples), step):
        x = int(i / len(norm_samples) * w)
        y = int(center_y - norm_samples[i])
        points.append((x, y))
    if len(points) > 1:
        cv2.polylines(overlay, [np.array(points)], False, (0, 255, 0), 2)
    frame[h - waveform_height:h, 0:w] = overlay
    return frame

# ---------------------------
# State Tracking for Fingers
# ---------------------------
# Finger keys: F1 (Thumb), F2 (Index), F3 (Middle), F4 (Ring), F5 (Pinky)
prev_finger_state = {'F1': False, 'F2': False, 'F3': False, 'F4': False, 'F5': False}
sweeping = {'F1': False, 'F2': False, 'F3': False, 'F4': False, 'F5': False}
default_position = 90  # Default reset position

# ---------------------------
# Main Loop
# ---------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('h'):
        with mode_lock:
            mode = "hand"
    elif key == ord('a'):
        with mode_lock:
            mode = "audio"
    elif key == ord('q') or key == 27:
        quit_flag = True
        break

    with mode_lock:
        current_mode = mode

    if current_mode == "hand":
        results = hands.process(frameRGB)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                landmarks = hand_landmarks.landmark
                h_frame, w_frame, _ = frame.shape

                def to_point(landmark):
                    return (int(landmark.x * w_frame), int(landmark.y * h_frame))

                # Simple heuristic: finger is "raised" if tip is above PIP joint.
                finger_state = {}
                # Thumb: using horizontal comparison (assuming right hand and mirror image)
                finger_state['F1'] = landmarks[4].x < landmarks[3].x
                # Index: tip (8) vs. PIP (6)
                finger_state['F2'] = landmarks[8].y < landmarks[6].y
                # Middle: tip (12) vs. PIP (10)
                finger_state['F3'] = landmarks[12].y < landmarks[10].y
                # Ring: tip (16) vs. PIP (14)
                finger_state['F4'] = landmarks[16].y < landmarks[14].y
                # Pinky: tip (20) vs. PIP (18)
                finger_state['F5'] = landmarks[20].y < landmarks[18].y

                # For each finger, if it transitions from "not raised" to "raised", trigger a sweep.
                for finger in ['F1', 'F2', 'F3', 'F4', 'F5']:
                    if finger_state[finger] and not prev_finger_state[finger]:
                        if not sweeping[finger]:
                            sweeping[finger] = True
                            threading.Thread(target=sweep_finger, args=(finger,), daemon=True).start()
                    prev_finger_state[finger] = finger_state[finger]

                status_text = "H Mode: " + " ".join([f"{k}:{'Up' if v else 'Down'}" for k, v in finger_state.items()])
        else:
            # No hand detected: reset all servos to default
            for finger in ['F1', 'F2', 'F3', 'F4', 'F5']:
                send_servo_command(finger, default_position)
            status_text = "H Mode: No hand detected - Resetting servos"
    elif current_mode == "audio":
        audio_servo_angle = int(90 + audio_level * 90)
        for finger in ['F1', 'F2', 'F3', 'F4', 'F5']:
            send_servo_command(finger, audio_servo_angle)
        status_text = f"A Mode: Audio Level {audio_level:.2f} -> Angle {audio_servo_angle}"
        frame = draw_audio_waveform(frame, audio_samples)

    cv2.putText(frame, f"Mode: {current_mode} (press 'h' for hand, 'a' for audio, 'q' to quit)", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
    cv2.putText(frame, status_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    cv2.imshow("Hand/Audio Control", frame)

cap.release()
cv2.destroyAllWindows()
ser.close()
