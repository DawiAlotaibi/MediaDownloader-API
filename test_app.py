import pytest
from app import app
import os

DOWNLOAD_FOLDER = "downloads"  # the teardown_function removes any file in this dir. if you want to change it you need
# to either change the dir in app.py or add a way to pass it as an argument. For now this works as needed.


def setup_function(function):
    app.config['TESTING'] = True
    app.testing = True
    app.test_client()


def teardown_function(function):
    # Delete any downloaded files after each test to ensure a clean state
    for filename in os.listdir(DOWNLOAD_FOLDER):
        os.remove(os.path.join(DOWNLOAD_FOLDER, filename))


def test_download_video_with_audio():
    # need to check if the video file exists in the downloads folder and if it has video and audio.

    data = {
        "url": "https://music.youtube.com/watch?v=4UnU3r0M3zg&si=PKJgV7NDPVCygGIj",
        "audio_only": "False",
        "ext": "mp4"
    }
    response = app.test_client().post('/download', json=data)
    assert response.status_code == 200
    json_response = response.get_json()
    assert json_response["status"] == "success"


def test_download_audio_only_mp4():
    # need to check if the video file exists in the downloads folder and if it has audio only.

    data = {
        "url": "https://music.youtube.com/watch?v=4UnU3r0M3zg&si=PKJgV7NDPVCygGIj",
        "audio_only": "True",
        "ext": "mp4"
    }
    response = app.test_client().post('/download', json=data)
    assert response.status_code == 200
    json_response = response.get_json()
    assert json_response["status"] == "success"


def test_download_audio_only_mp3():
    # need to check if the video file exists in the downloads folder and if it has audio only and is mp3.

    data = {
        "url": "https://music.youtube.com/watch?v=4UnU3r0M3zg&si=PKJgV7NDPVCygGIj",
        "audio_only": "True",
        "ext": "mp3"
    }
    response = app.test_client().post('/download', json=data)
    assert response.status_code == 200
    json_response = response.get_json()
    assert json_response["status"] == "success"


def test_wrong_extension_without_audio():
    data = {
        "url": "https://music.youtube.com/watch?v=4UnU3r0M3zg&si=PKJgV7NDPVCygGIj",
        "ext": "mp3"
    }
    response = app.test_client().post('/download', json=data)
    assert response.status_code == 500
    json_response = response.get_json()
    assert json_response["status"] == "error"
    assert "mp3 extension requires audio_only to be True" in json_response["Wrong extension or missing parameters"]


def test_serve_video():
    data = {
        "url": "https://music.youtube.com/watch?v=4UnU3r0M3zg&si=PKJgV7NDPVCygGIj",
        "audio_only": "False",
        "ext": "mp4"
    }
    response = app.test_client().post('/download', json=data)
    assert response.status_code == 200
    json_response = response.get_json()
    assert json_response["status"] == "success"
    video_filename = json_response["filename"]
    response = app.test_client().get(f'/videos/{video_filename}')
    assert response.status_code == 200


if __name__ == '__main__':
    pytest.main()
