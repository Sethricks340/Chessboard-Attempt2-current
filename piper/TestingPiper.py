import subprocess
import simpleaudio as sa
import os
import time

class Piper_Speak:
    def __init__(self):

        # print("initializing piper...")
        #canidates:
        self.model_file = r"C:\Users\sethr\Chessboard-Attempt2-current\piper\Voices\Phoenix Male GB\en_GB-northern_english_male-medium.onnx"
        # self.model_file = r"C:\Users\sethr\Chessboard-Attempt2-current\piper\Voices\Phoenix Female GB\en_GB-southern_english_female-low.onnx"
        # self.model_file = r"C:\Users\sethr\Chessboard-Attempt2-current\piper\Voices\Phoenix Male US\en_US-hfc_male-medium.onnx"
        # self.model_file = r"C:\Users\sethr\Chessboard-Attempt2-current\piper\Voices\Phoenix Female US\en_US-hfc_female-medium.onnx"

        self.output_file = r"C:\Users\sethr\Chessboard-Attempt2-current\piper\testing.wav"

        self.piper_file = r"C:\Users\sethr\Chessboard-Attempt2-current\piper\piper.exe"

    def Speak(self, text):
        # Step 1: Generate the audio file with Piper
        command = f'echo "{text}" | {self.piper_file} --model "{self.model_file}" --output_file "{self.output_file}"'
        subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # Step 2: Play the generated audio
        wave_obj = sa.WaveObject.from_wave_file(self.output_file)
        wave_obj.play().wait_done()