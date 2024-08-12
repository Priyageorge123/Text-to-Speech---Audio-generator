from flask import Flask, request, jsonify
from pydub import AudioSegment
from io import BytesIO
import requests

app = Flask(__name__)

TTS_URL = "https://dfki-3109.dfki.de/tts/run/predict"
FILE_BASE_URL = "https://dfki-3109.dfki.de/tts/file="
MAX_CHAR_LIMIT = 100  # Define a reasonable character limit for each TTS request

def split_text(text, max_length):
    """
    Split the text into smaller parts each not exceeding max_length characters.
    This function ensures that words are not split.
    """
    words = text.split()
    current_segment = []
    current_length = 0

    for word in words:
        if current_length + len(word) + 1 > max_length:
            yield ' '.join(current_segment)
            current_segment = [word]
            current_length = len(word) + 1
        else:
            current_segment.append(word)
            current_length += len(word) + 1

    if current_segment:
        yield ' '.join(current_segment)

def process_sentence(language, sentence):
    response = requests.post(TTS_URL, json={"data": [language, sentence]})
    if response.status_code == 200:
        response_json = response.json()
        try:
            audio_url = FILE_BASE_URL + response_json['data'][0]['name']
            audio_response = requests.get(audio_url)
            if audio_response.status_code == 200:
                return AudioSegment.from_wav(BytesIO(audio_response.content))
        except KeyError as e:
            print(f"Unexpected response structure: {response_json}")
    return None

@app.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    data = request.get_json()
    text = data.get("text", "")
    language = data.get("language", "de")  # Default to German if not specified

    sentences = text.split('.')
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]

    audio_segments = []
    for sentence in sentences:
        for segment in split_text(sentence, MAX_CHAR_LIMIT):
            audio_segment = process_sentence(language, segment)
            if audio_segment:
                audio_segments.append(audio_segment)
                audio_segments.append(AudioSegment.silent(duration=350))  # 0.35 seconds between segments
        audio_segments.append(AudioSegment.silent(duration=350))  # 0.35 seconds between sentences

    if audio_segments:
        combined_audio = sum(audio_segments)
        combined_audio.export("output.mp3", format="mp3")
        return jsonify({"audio_file": "output.mp3"})
    else:
        return jsonify({"error": "Unable to generate audio"}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=False)
