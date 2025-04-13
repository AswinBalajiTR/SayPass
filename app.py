from flask import Flask, render_template, request, jsonify, redirect, url_for
import numpy as np
import os
import whisper
from scipy.spatial.distance import cosine
from resemblyzer import VoiceEncoder, preprocess_wav
import librosa
import soundfile as sf

app = Flask(__name__)

# Configuration
SAMPLE_RATE = 16000
THRESHOLD = 0.80
REQUIRED_MATCHES = 2

# Ensure necessary files exist (or will be created)
EMBEDDINGS_FILE = "my_voice_embeddings.npy"
PROMPT_FILE = "password_prompt.txt"

if not os.path.exists(PROMPT_FILE):
    with open(PROMPT_FILE, "w") as f:
        f.write("")
if not os.path.exists(EMBEDDINGS_FILE):
    np.save(EMBEDDINGS_FILE, np.array([]))

# Load Whisper model and VoiceEncoder once at startup
whisper_model = whisper.load_model("base")
encoder = VoiceEncoder()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        print("Files received:", request.files)  # Debugging line
        if 'audio_train1' not in request.files or 'audio_train2' not in request.files or 'prompt' not in request.files:
            return jsonify({'success': False, 'message': 'Error: Missing audio files.'})

        try:
            audio_train1_file = request.files['audio_train1']
            audio_train2_file = request.files['audio_train2']
            audio_prompt_file = request.files['prompt']

            temp_train1 = "temp_train1.webm"
            temp_train2 = "temp_train2.webm"
            temp_prompt = "temp_prompt.webm"

            audio_train1_file.save(temp_train1)
            audio_train2_file.save(temp_train2)
            audio_prompt_file.save(temp_prompt)

            try:
                audio_train1, sr1 = librosa.load(temp_train1, sr=SAMPLE_RATE)
                audio_train2, sr2 = librosa.load(temp_train2, sr=SAMPLE_RATE)
                audio_prompt, sr_prompt = librosa.load(temp_prompt, sr=SAMPLE_RATE)
            except Exception as e:
                return jsonify({'success': False, 'message': f'Error loading audio files: {str(e)}'})

            embeddings = []
            for audio in [audio_train1, audio_train2]:
                temp_wav = "temp_audio.wav"
                sf.write(temp_wav, audio, sr1)
                wav = preprocess_wav(temp_wav)
                embed = encoder.embed_utterance(wav)
                embeddings.append(embed.tolist())

            embeddings = np.array(embeddings)
            np.save(EMBEDDINGS_FILE, embeddings)
            print(f"✅ Saved {len(embeddings)} voice embeddings to '{EMBEDDINGS_FILE}'")

            prompt_temp_wav = "temp_prompt_audio.wav"
            sf.write(prompt_temp_wav, audio_prompt, sr_prompt)
            result = whisper_model.transcribe(prompt_temp_wav)
            prompt_text = result["text"].strip().lower()
            os.remove(prompt_temp_wav)

            with open(PROMPT_FILE, "w") as f:
                f.write(prompt_text)

            print(f"🔐 Prompt saved: '{prompt_text}' to '{PROMPT_FILE}'")

            return jsonify({'success': True, 'message': 'Voice registration successful!', 'redirect': '/authenticate_page'})

        except Exception as e:
            print(f"Error during registration: {e}")
            return jsonify({'success': False, 'message': f'Registration failed: {str(e)}'})

        finally:
            for temp_file in [temp_train1, temp_train2, temp_prompt]:
                if os.path.exists(temp_file):
                    os.remove(temp_file)

    return render_template('register.html')

@app.route('/authenticate_page')
def authenticate_page():
    return render_template('authenticate.html')

@app.route('/authenticate', methods=['POST'])
def authenticate():
    if 'audio_test' not in request.files:
        return jsonify({'success': False, 'message': 'Error: Missing test audio file.'})

    try:
        audio_test_file = request.files['audio_test']
        temp_test = "temp_test.webm"
        audio_test_file.save(temp_test)

        try:
            audio_test, sr_test = librosa.load(temp_test, sr=SAMPLE_RATE)
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error loading test audio: {str(e)}'})

        temp_test_wav = "temp_test_audio.wav"
        sf.write(temp_test_wav, audio_test, sr_test)
        test_embed = encoder.embed_utterance(preprocess_wav(temp_test_wav))
        os.remove(temp_test_wav)

        try:
            enrolled = np.load(EMBEDDINGS_FILE)
            if enrolled.ndim == 1:
                enrolled = np.array([enrolled])
        except FileNotFoundError:
            return jsonify({'success': False, 'message': 'Error: Enrolled voice data not found. Please register first.'})

        matches = []
        for i, ref_embed in enumerate(enrolled):
            if ref_embed.shape == test_embed.shape:
                sim = 1 - cosine(test_embed, ref_embed)
                print(f"🧠 Similarity with sample {i+1}: {sim:.3f}")
                matches.append(sim > THRESHOLD)
            else:
                print(f"⚠️ Shape mismatch between test and enrolled embedding {i+1}")

        spoken_temp_wav = "temp_spoken_audio.wav"
        sf.write(spoken_temp_wav, audio_test, sr_test)
        spoken = whisper_model.transcribe(spoken_temp_wav)["text"].strip().lower()
        os.remove(spoken_temp_wav)

        try:
            with open(PROMPT_FILE, "r") as f:
                expected = f.read().strip().lower()
        except FileNotFoundError:
            return jsonify({'success': False, 'message': 'Error: Expected prompt not found.'})

        print(f"🗣️ You said: {spoken}")
        print(f"🔐 Expected: {expected}")

        voice_match = sum(matches) >= REQUIRED_MATCHES
        prompt_match = expected in spoken

        if voice_match and prompt_match:
            result_message = "✅ Access granted — Verified speaker and prompt 🎉"
            success = True
        else:
            result_message = "❌ Access denied."
            success = False

        return jsonify({'success': success, 'message': result_message})

    except Exception as e:
        print(f"Error during authentication: {e}")
        return jsonify({'success': False, 'message': f'Authentication failed: {str(e)}'})

    finally:
        if os.path.exists("temp_test.webm"):
            os.remove("temp_test.webm")

if __name__ == '__main__':
    app.run(debug=True)