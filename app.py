from flask import Flask, request, send_from_directory, jsonify
from pytube import YouTube
import os

app = Flask(__name__)
DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)


@app.route('/download', methods=['POST'])
def download():
    url = request.json.get('url')
    if not url:
        return jsonify({"error": "URL is required"}), 400

    try:
        yt = YouTube(url)
        video_stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
        video_stream.download(DOWNLOAD_FOLDER)
        video_filename = video_stream.default_filename
        return jsonify({"status": "success", "filename": video_filename})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/videos/<filename>', methods=['GET'])
def serve_video(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename)


@app.route('/videos/<filename>', methods=['DELETE'])
def delete_video(filename):
    # Ensure the file exists before attempting deletion
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({"status": "success", "message": f"{filename} deleted successfully"})
    else:
        return jsonify({"error": f"{filename} not found"}), 404


if __name__ == '__main__':
    app.run(debug=True)
