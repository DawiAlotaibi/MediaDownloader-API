import pathlib

from flask import Flask, request, send_from_directory, jsonify
import instaloader
from pytube import YouTube
import os
from flask import Response, stream_with_context

app = Flask(__name__)
DOWNLOAD_FOLDER = "downloads"


# TODO: Handle when 404?
# TODO: Add documentation for route usage (params, etc)


@app.route('/', methods=['GET'])
def index():
    return 'API works! Make sure to use POST request on /download path', 200


@app.route('/download', methods=['POST'])
def download():
    global returnFile
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)

    try:
        url = request.json.get('url')
        extension = request.json.get('ext')
        audio_only = request.json.get('audio_only')

        if not url:
            return jsonify({"error": "URL is required"}), 400
        if "instagram" in url:
            shortcode = url.split('p/')[1].strip('/ ')
            L = instaloader.Instaloader(dirname_pattern=DOWNLOAD_FOLDER + '/' + shortcode)
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            L.download_post(post, shortcode)
            dir = os.listdir(path=DOWNLOAD_FOLDER + '/' + shortcode)
            returnFile = ""
            for file in dir:
                if pathlib.Path(file).suffix == ".mp4":
                    returnFile = file
            return send_from_directory(DOWNLOAD_FOLDER + '/' + shortcode, returnFile)
        elif "youtube" in url:
            if not extension:
                extension = "mp4"
            if extension == "mp3" and not audio_only:
                return jsonify({"status": "error", "Wrong extension or missing parameters": f"{extension} extension "
                                                                                            f"requires audio_only to be "
                                                                                            f"True"}), 500

            yt = YouTube(url)
            # Append v or a respectively if its an audio or video file
            if audio_only:
                video_streams = yt.streams.filter(only_audio=True).order_by('abr').desc()
                video_stream = video_streams.first()  # This should be the highest bitrate stream
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


@app.route('/delete/<filename>', methods=['DELETE'])
def delete_video(filename):
    if request.headers["Authorization"].split(" ")[1] == os.environ.get('TOKEN'):
        file_path = os.path.join(DOWNLOAD_FOLDER, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({"status": "success", "message": f"{filename} deleted successfully"})
        else:
            return jsonify({"error": f"{filename} not found"}), 404
    else:
        return jsonify({"UNAUTHORIZED": f"You are not authorized"}), 401

