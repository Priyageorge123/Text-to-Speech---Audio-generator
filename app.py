from flask import Flask, request, jsonify, send_from_directory
import requests
from pydub import AudioSegment
from io import BytesIO
import os

app = Flask(__name__)

TTS_URL = "https://dfki-3109.dfki.de/tts/run/predict"
FILE_BASE_URL = "https://dfki-3109.dfki.de/tts/file="
OUTPUT_DIR = "audio_files"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

@app.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    data = request.get_json()
    text = data.get('text', '')

    # Split the text into sentences
    sentences = text.split('.')
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]

    # Process each sentence
    audio_segments = []
    for sentence in sentences:
        audio_segment = process_sentence(sentence)
        if audio_segment:
            audio_segments.append(audio_segment)

    # Concatenate all audio segments
    if audio_segments:
        combined = sum(audio_segments[1:], audio_segments[0])
        output_path = os.path.join(OUTPUT_DIR, "output.mp3")
        combined.export(output_path, format="mp3")
        return jsonify({"audio_file": "output.mp3"})
    else:
        return jsonify({"error": "Failed to generate audio for the given text"}), 500

def process_sentence(sentence):
    response = requests.post(TTS_URL, json={"data": ["de", sentence]})
    if response.status_code == 200:
        response_json = response.json()
        try:
            audio_url = FILE_BASE_URL + response_json['data'][0]['name']
            audio_response = requests.get(audio_url)
            if audio_response.status_code == 200:
                return AudioSegment.from_wav(BytesIO(audio_response.content))
        except (KeyError, IndexError) as e:
            print(f"Unexpected response structure: {response_json}")
    return None

@app.route('/audio/<filename>', methods=['GET'])
def get_audio_file(filename):
    return send_from_directory(OUTPUT_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True)
