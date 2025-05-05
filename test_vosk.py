from test_microphone import VoiceInput
vi = VoiceInput("C:/Users/sethr/Chessboard-Attempt2-current/vosk-model-small-en-us-0.15/vosk-model-small-en-us-0.15", device=17)
user_speech = vi.listen()
print(f"You said: {user_speech}")