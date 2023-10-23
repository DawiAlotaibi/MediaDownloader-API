from flask import Flask, request, send_from_directory, jsonify
from pytube import YouTube
import os
from flask import Response, stream_with_context

app = Flask(__name__)
DOWNLOAD_FOLDER = "downloads"

# TODO: Download playlists
# TODO: Handle when 404?
# TODO: Download by searching for a video
# TODO: Download video with no audio
# TODO: Add logging for debugging
# TODO: Add other platforms
# TODO: Implement resolution for caching
# TODO: Add documentation for route usage (params, etc)


@app.route('/', methods=['GET'])
def index():
    return 'API works! Make sure to use POST request on /download path', 200


@app.route('/download', methods=['POST'])
def download():

    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)

    try:
        url = request.json.get('url')
        extension = request.json.get('ext')
        audio_only = request.json.get('audio_only')

        if not url:
            return jsonify({"error": "URL is required"}), 400
        if not extension:
            extension = "mp4"
        if extension == "mp3" and not audio_only:
            return jsonify({"status": "error", "Wrong extension or missing parameters": f"{extension} extension "
                                                                                        f"requires audio_only to be "
                                                                                        f"True"}), 500

        yt = YouTube(url)
        # Append v or a respectively if its an audio or video file
        if audio_only:
            video_stream = yt.streams.filter(
                only_audio=audio_only, file_extension="mp4").first()
            video_filename = f'a-{video_stream.default_filename.split(".")[0]}.{extension}'
        else:
            video_stream = yt.streams.filter(progressive=True,
                                             file_extension=extension).first()
            video_filename = f'v-{video_stream.default_filename.split(".")[0]}.{extension}'

        if check_cache(video_filename):
            return send_from_directory(DOWNLOAD_FOLDER, video_filename)
        else:
            video_stream.download(
                filename=f'{DOWNLOAD_FOLDER}/{video_filename}')
            return send_from_directory(DOWNLOAD_FOLDER, video_filename)

    except UnboundLocalError:
        return 'ERROR: Make sure to supply the correct parameters', 500
    except Exception as e:
        print(e)
        return 'ERROR: Make sure to supply the correct parameters', 500


def check_cache(filename):
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        print(f'File {filename} found in cache')
        return True
    else:
        print(f'File {filename} not found, proceed to download')
        return False


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
