import queue
import sounddevice as sd
import time
import json
from vosk import Model, KaldiRecognizer

class VoiceInput:
    def __init__(self, model_path, device=None, samplerate=None, timeout=5):
        self.q = queue.Queue()
        self.device = device
        self.timeout = timeout  # Set timeout duration (in seconds)

        start_time = time.time()
        self.model = Model(model_path)
        end_time = time.time()
        # print(f"Model loaded in {end_time - start_time:.4f} seconds")

        if samplerate is None:
            device_info = sd.query_devices(self.device, "input")
            self.samplerate = int(device_info["default_samplerate"])
        else:
            self.samplerate = samplerate

        self.recognizer = KaldiRecognizer(self.model, self.samplerate)

    def _callback(self, indata, frames, time, status):
        """Capture audio input."""
        if status:
            print(status)
        self.q.put(bytes(indata))

    def listen(self):
        """Capture and return user speech as text, handling silence."""
        with sd.RawInputStream(samplerate=self.samplerate, blocksize=8000,
                               device=self.device, dtype="int16",
                               channels=1, callback=self._callback):
            print("Listening... Speak now!")

            start_time = time.time()

            while True:
                data = self.q.get()
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get("text", "")

                    if text:
                        return text  # Return text when speech is detected
                    
                # Check for timeout
                if time.time() - start_time > self.timeout:
                    print("No speech detected, continuing to listen...")
                    start_time = time.time()  # Reset timeout

# Example usage
if __name__ == "__main__":
    vi = VoiceInput("C:/Users/sethr/Chessboard-Attempt2-current/vosk-model-small-en-us-0.15/vosk-model-small-en-us-0.15", device=17)
    user_speech = vi.listen()
    print(f"You said: {user_speech}")