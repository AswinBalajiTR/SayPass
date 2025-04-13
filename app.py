from flask import Flask, render_template, request, jsonify, redirect, url_for
import numpy as np
import os
import whisper
from scipy.spatial.distance import cosine
from resemblyzer import VoiceEncoder, preprocess_wav
import glob
import librosa  # Import librosa
import soundfile as sf  # Import soundfile

app = Flask(__name__)

# Configuration
SAMPLE_RATE = 16000
DURATION = 5
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if 'audio_train1' not in request.files or 'audio_train2' not in request.files or 'audio_prompt' not in request.files:
            return jsonify({'success': False, 'message': 'Error: Missing audio files.'})

        try:
            audio_train1_file = request.files['audio_train1']
            audio_train2_file = request.files['audio_train2']
            audio_prompt_file = request.files['audio_prompt']

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

            encoder = VoiceEncoder()
            embeddings = []
            for audio in [audio_train1, audio_train2]:
                temp_wav = "temp_audio.wav"
                sf.write(temp_wav, audio, sr1)
                wav = preprocess_wav(temp_wav)
                embed = encoder.embed_utterance(wav)
                embeddings.append(embed)
                os.remove(temp_wav)

            embeddings = np.array(embeddings)
            np.save(EMBEDDINGS_FILE, embeddings)
            print(f"✅ Saved {len(embeddings)} voice embeddings to '{EMBEDDINGS_FILE}'")

            whisper_model = whisper.load_model("base")
            temp_prompt_wav = "temp_prompt_audio.wav"
            sf.write(temp_prompt_wav, audio_prompt, sr_prompt)
            result = whisper_model.transcribe(temp_prompt_wav)
            prompt_text = result["text"].strip().lower()
            os.remove(temp_prompt_wav)

            with open(PROMPT_FILE, "w") as f:
                f.write(prompt_text)

            print(f"🔐 Prompt saved: '{prompt_text}' to '{PROMPT_FILE}'")

            return jsonify({'success': True, 'message': 'Voice registration successful!', 'redirect': '/authenticate'})

        except Exception as e:
            print(f"Error during registration: {e}")
            return jsonify({'success': False, 'message': f'Registration failed: {str(e)}'})

        finally:
            # Clean up temporary files
            for temp_file in [temp_train1, temp_train2, temp_prompt]:
                if os.path.exists(temp_file):
                    os.remove(temp_file)

    return render_template('register.html')

@app.route('/authenticate', methods=['GET', 'POST'])
def authenticate():
    if request.method == 'POST':
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

            encoder = VoiceEncoder()
            temp_test_wav = "temp_test_audio.wav"
            sf.write(temp_test_wav, audio_test, sr_test)
            test_embed = encoder.embed_utterance(preprocess_wav(temp_test_wav))
            os.remove(temp_test_wav)

            try:
                enrolled = np.load(EMBEDDINGS_FILE)
            except FileNotFoundError:
                return jsonify({'success': False, 'message': 'Error: Enrolled voice data not found. Please register first.'})

            matches = []
            for i, ref_embed in enumerate(enrolled):
                sim = 1 - cosine(test_embed, ref_embed)
                print(f"🧠 Similarity with sample {i+1}: {sim:.3f}")
                matches.append(sim > THRESHOLD)

            whisper_model = whisper.load_model("base")
            temp_spoken_wav = "temp_spoken_audio.wav"
            sf.write(temp_spoken_wav, audio_test, sr_test)
            spoken = whisper_model.transcribe(temp_spoken_wav)["text"].strip().lower()
            os.remove(temp_spoken_wav)

            try:
                with open(PROMPT_FILE, "r") as f:
                    expected = f.read().strip().lower()
            except FileNotFoundError:
                return jsonify({'success': False, 'message': 'Error: Expected prompt not found.'})

            print(f"🗣️ You said: {spoken}")
            print(f"🔐 Expected: {expected}")

            voice_match = sum(matches) >= REQUIRED_MATCHES
            prompt_match = len(set(spoken.split()) & set(expected.split())) >= 2

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
            # Clean up temporary test file
            if os.path.exists(temp_test):
                os.remove(temp_test)

    return render_template('authenticate.html')

@app.route('/authenticate_page')
def authenticate_page():
    return render_template('authenticate.html')

if __name__ == '__main__':
    app.run(debug=True)