import speech_recognition as sr
import threading
import time

# Global variables shared across modules
current_command = "stop"
is_listening = True

def listen_for_commands():
    global current_command, is_listening
    recognizer = sr.Recognizer()
    
    # Adjust thresholds for background noise sensitivity
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True

    while is_listening:
        try:
            with sr.Microphone() as source:
                print("\n[Voice Control] Listening for command (forward, backward, left, right, stop)...")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)

            text = recognizer.recognize_google(audio).lower()
            print(f"[Voice Control] Heard: '{text}'")

            if "forward" in text or "go" in text or "drive" in text:
                current_command = "forward"
            elif "backward" in text or "reverse" in text or "back" in text:
                current_command = "backward"
            elif "left" in text:
                current_command = "left"
            elif "right" in text:
                current_command = "right"
            elif "stop" in text or "brake" in text:
                current_command = "stop"
            else:
                print("[Voice Control] Unrecognized command.")

        except sr.WaitTimeoutError:
            pass  # Listening timed out waiting for phrase, retry loop
        except sr.UnknownValueError:
            pass  # Speech was unintelligible
        except Exception as e:
            print(f"[Voice Control] Error: {e}")
            time.sleep(1)

def start_voice_thread():
    thread = threading.Thread(target=listen_for_commands, daemon=True)
    thread.start()
    return thread