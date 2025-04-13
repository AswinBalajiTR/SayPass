# test.py
import sounddevice as sd
import soundfile as sf
import numpy as np
from resemblyzer import VoiceEncoder, preprocess_wav
from scipy.spatial.distance import cosine
import whisper

SAMPLE_RATE = 16000
DURATION = 5
THRESHOLD = 0.80 # tighter for security
REQUIRED_MATCHES = 2  # out of 3

# Record test audio
input("🎤 Press Enter to record test voice...")
audio = sd.rec(int(SAMPLE_RATE * DURATION), samplerate=SAMPLE_RATE, channels=1)
sd.wait()
sf.write("test_voice.wav", audio, SAMPLE_RATE)
print("✅ Test voice recorded.")

# Encode test
encoder = VoiceEncoder()
test_embed = encoder.embed_utterance(preprocess_wav("test_voice.wav"))

# Load enrolled embeddings
enrolled = np.load("my_voice_embeddings.npy")

# Compare with all enrolled samples
matches = []
for i, ref_embed in enumerate(enrolled):
    sim = 1 - cosine(test_embed, ref_embed)
    print(f"🧠 Similarity with sample {i+1}: {sim:.3f}")
    matches.append(sim > THRESHOLD)

# Transcribe prompt
whisper_model = whisper.load_model("base")
spoken = whisper_model.transcribe("test_voice.wav")["text"].strip().lower()
with open("password_prompt.txt", "r") as f:
    expected = f.read().strip().lower()

print(f"🗣️ You said: {spoken}")
print(f"🔐 Expected: {expected}")

# Final Decision
if sum(matches) >= REQUIRED_MATCHES:
    if len(set(spoken.split()) & set(expected.split())) >= 2:
        print("✅ Access granted — Verified speaker and prompt 🎉")
    else:
        print("⚠️ Prompt mismatch — Access denied.")
else:
    print("❌ Voice mismatch — Access denied.")
