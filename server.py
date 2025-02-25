from flask import Flask, request, jsonify, send_from_directory, render_template
import os
import qrcode
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'txt'}

# Function to check if file type is allowed


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = datetime.now().strftime('%Y%m%d%H%M%S') + '_' + file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 200
    return jsonify({'error': 'Invalid file type'}), 400


@app.route('/api/files', methods=['GET'])
def list_files():
    files = []
    for filename in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        upload_time = datetime.fromtimestamp(
            os.path.getctime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
        files.append({'name': filename, 'upload_time': upload_time})
    return jsonify(files)


@app.route('/api/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({'message': 'File deleted'}), 200
    return jsonify({'error': 'File not found'}), 404


@app.route('/uploads/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route('/api/qrcode', methods=['GET'])
def generate_qr():
    upload_url = request.host_url + 'upload'
    qr = qrcode.make(upload_url)
    qr_path = os.path.join('static', 'qrcode.png')
    qr.save(qr_path)
    return jsonify({'qr_code': qr_path})


if __name__ == '__main__':
    app.run(debug=True)
