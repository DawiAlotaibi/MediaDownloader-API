from flask import Flask, request, send_from_directory, jsonify
from pytube import YouTube
import os
from flask import Response, stream_with_context

app = Flask(__name__)
DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)


# TODO: Download playlists
# TODO: Handle when 404?
# TODO: Download by searching for a video
# TODO: Download video with no audio
# TODO: Add logging for debugging
@app.route('/download', methods=['POST'])
def download():
    url = request.json.get('url')
    extension = request.json.get('ext')
    audio_only = request.json.get('audio_only')
    if not url:
        return jsonify({"error": "URL is required"}), 400
    if not extension:
        extension = "mp4"
    if not audio_only or audio_only.lower() == "false":
        audio_only = False

    try:
        if extension == "mp3" and not audio_only:
            return jsonify({"status": "error", "Wrong extension or missing parameters": f"{extension} extension "
                                                                                        f"requires audio_only to be "
                                                                                        f"True"}), 500
        elif not audio_only:
            yt = YouTube(url)
            video_stream = yt.streams.filter(progressive=True, file_extension=extension).first()
            video_stream.download(DOWNLOAD_FOLDER)
            video_filename = video_stream.default_filename
            return jsonify({"status": "success", "filename": video_filename})

        elif audio_only:
            yt = YouTube(url)
            video_stream = yt.streams.filter(only_audio=audio_only, file_extension="mp4").first()
            video_filename = video_stream.default_filename.split(".")[0] + f".{extension}"
            video_stream.download(output_path=DOWNLOAD_FOLDER, filename=video_filename)
            return jsonify({"status": "success", "filename": video_filename})

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/videos/<filename>', methods=['GET'])
def serve_video(filename):
    def generate():
        with open(os.path.join(DOWNLOAD_FOLDER, filename), "rb") as f:
            while True:
                chunk = f.read(4096)  # read 4 KB at a time
                if not chunk:
                    break
                yield chunk
    return Response(stream_with_context(generate()), content_type="video/mp4")



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
