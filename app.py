import os
import whisper
import ffmpeg
from flask import Flask, request, render_template_string
from googletrans import Translator
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load Whisper model
model = whisper.load_model("base")
translator = Translator()

# HTML Template
HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Translate Video to English</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <h2>Upload Video to Translate</h2>
    <form method="post" enctype="multipart/form-data">
        <input type="file" name="video">
        <button type="submit">Translate</button>
    </form>
    {% if translated_text %}
    <h3>Translated Text:</h3>
    <p>{{ translated_text }}</p>
    {% endif %}
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    translated_text = None

    if request.method == 'POST':
        video = request.files['video']
        if not video:
            return "No video uploaded", 400

        filename = secure_filename(video.filename)
        video_path = os.path.join(UPLOAD_FOLDER, filename)
        video.save(video_path)

        # Convert video to audio
        audio_path = os.path.splitext(video_path)[0] + '.mp3'
        ffmpeg.input(video_path).output(audio_path).run(overwrite_output=True)

        # Transcribe using Whisper
        result = model.transcribe(audio_path)
        original_text = result['text']

        # Translate to English
        translated = translator.translate(original_text, dest='en')
        translated_text = translated.text

    return render_template_string(HTML, translated_text=translated_text)

if __name__ == '__main__':
    app.run(debug=True)
