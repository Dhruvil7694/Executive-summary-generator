from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from summarizer import summarize_pdf  # Import the summarize_pdf function

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads/'
AUDIO_FOLDER = 'audio/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['AUDIO_FOLDER'] = AUDIO_FOLDER

# Ensure upload and audio directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AUDIO_FOLDER, exist_ok=True)


@app.route('/test', methods=['GET'])
def test():
    return jsonify({'message': 'Server is running!'})


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Save and process the uploaded file
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # Generate summary and other details
        result = summarize_pdf(file_path)

        # Move the generated audio file to the AUDIO_FOLDER
        audio_file_name = os.path.basename(result['audio_path'])
        new_audio_path = os.path.join(app.config['AUDIO_FOLDER'], audio_file_name)
        os.rename(result['audio_path'], new_audio_path)

        # Update audio path in the result
        result['audio_path'] = f"/audio/{audio_file_name}"

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/audio/<filename>', methods=['GET'])
def download_audio(filename):
    return send_from_directory(app.config['AUDIO_FOLDER'], filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
