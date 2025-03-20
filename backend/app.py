from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import uuid
import json
import asyncio
import threading
from werkzeug.utils import secure_filename
from datetime import datetime
from main import DocumentProcessor  # Import DocumentProcessor class

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
RESULTS_FOLDER = 'results'
STATUS_FOLDER = 'status'  # Folder for tracking status
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULTS_FOLDER'] = RESULTS_FOLDER
app.config['STATUS_FOLDER'] = STATUS_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)
os.makedirs(STATUS_FOLDER, exist_ok=True)

processor = DocumentProcessor()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def update_status(file_id, stage, progress, message):
    """Update processing status"""
    status_file = os.path.join(app.config['STATUS_FOLDER'], f"{file_id}_status.json")
    status = {
        'stage': stage,
        'progress': progress,
        'message': message,
        'timestamp': datetime.now().isoformat()
    }
    with open(status_file, 'w') as f:
        json.dump(status, f)
    return status

@app.route('/api/test', methods=['GET'])
def test_server():
    """Test if the server is running properly."""
    return jsonify({'status': 'success', 'message': 'Server is running'}), 200

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle PDF uploads and process dynamically using DocumentProcessor."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only PDF files are allowed'}), 400

    file_id = str(uuid.uuid4())
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}_{filename}")
    
    update_status(file_id, 'upload', 0, 'Starting file upload')
    file.save(file_path)
    update_status(file_id, 'upload', 100, 'File upload completed')
    
    async def process_file():
        update_status(file_id, 'processing', 0, 'Extracting text from document')
        result = await processor.process_document(file_path)
        
        if 'error' in result:
            update_status(file_id, 'failed', 100, result['error'])
        else:
            report_file = os.path.join(app.config['RESULTS_FOLDER'], f"{file_id}.json")
            with open(report_file, 'w') as f:
                json.dump(result, f, indent=4)
            update_status(file_id, 'completed', 100, 'Analysis completed successfully')
    
    threading.Thread(target=asyncio.run, args=(process_file(),)).start()
    
    return jsonify({'status': 'processing', 'fileId': file_id, 'message': 'Processing started'}), 202

@app.route('/api/status/<file_id>', methods=['GET'])
def get_status(file_id):
    """Retrieve the processing status of an uploaded file."""
    status_file = os.path.join(app.config['STATUS_FOLDER'], f"{file_id}_status.json")
    result_file = os.path.join(app.config['RESULTS_FOLDER'], f"{file_id}.json")
    
    if not os.path.exists(status_file):
        return jsonify({'error': 'Invalid or expired file ID'}), 404
    
    with open(status_file, 'r') as f:
        status = json.load(f)
    
    if status['stage'] == 'completed' and os.path.exists(result_file):
        with open(result_file, 'r') as f:
            status['results'] = json.load(f)
    
    return jsonify(status)

@app.route('/api/download/<file_id>', methods=['GET'])
def download_results(file_id):
    """Download the processed results for a given file ID."""
    result_file = os.path.join(app.config['RESULTS_FOLDER'], f"{file_id}.json")
    if not os.path.exists(result_file):
        return jsonify({'error': 'Results not found'}), 404
    
    return send_from_directory(
        app.config['RESULTS_FOLDER'],
        f"{file_id}.json",
        as_attachment=True,
        download_name='cybersecurity_report.json'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)