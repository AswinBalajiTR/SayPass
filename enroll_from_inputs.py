# enroll_from_inputs.py
from resemblyzer import VoiceEncoder, preprocess_wav
import numpy as np
import glob

encoder = VoiceEncoder()
voice_files = sorted(glob.glob("voice_train*.wav"))

embeddings = []
for vf in voice_files:
    wav = preprocess_wav(vf)
    embed = encoder.embed_utterance(wav)
    embeddings.append(embed)

embeddings = np.array(embeddings)
np.save("my_voice_embeddings.npy", embeddings)
print(f"✅ Saved {len(embeddings)} voice embeddings to 'my_voice_embeddings.npy'")
