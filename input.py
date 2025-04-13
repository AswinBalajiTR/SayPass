# input.py
import sounddevice as sd
import soundfile as sf
import numpy as np

fs = 16000

text_para = """
Hello! I’m reading this passage to help train a voice recognition system.
Every sound I produce, from soft whispers to clear and crisp words, helps the model learn my unique vocal signature.
I speak naturally, using low and high tones, short and long words, and a variety of expressions.
"""

def record_audio(filename):
    input(f"\nPress ENTER to start recording '{filename}', and speak when ready.")
    print("Recording... Press ENTER again to stop.")
    recording = []

    def callback(indata, frames, time, status):
        recording.append(indata.copy())

    stream = sd.InputStream(callback=callback, samplerate=fs, channels=1)
    stream.start()
    input()
    stream.stop()

    audio = np.concatenate(recording, axis=0)
    sf.write(filename, audio, fs)
    print(f"✅ Saved: {filename}\n")

print("🗣️ Please read the following aloud when prompted:\n")
print(text_para)

# Record training voices
record_audio("voice_train1.wav")
record_audio("voice_train2.wav")

# Record password/prompt voice
print("🔐 Please speak your secret phrase (password-like)")
record_audio("voice_prompt.wav")

import whisper

# === Transcribe the prompt
print("🧠 Transcribing your passphrase...")
model = whisper.load_model("base")
result = model.transcribe("voice_prompt.wav")
prompt_text = result["text"].strip().lower()

with open("password_prompt.txt", "w") as f:
    f.write(prompt_text)

print(f"🔐 Prompt saved: '{prompt_text}' to 'password_prompt.txt'")

