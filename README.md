# MediaDownloader-API

This is a list of APIs to download videos from various platforms.

#### Supported Platforms

- YouTube
- Instagram

# How to build

First install the dependence by running:

```commandline
pip install -r requirements.txt
```

Then just run the application by:

```commandline
python app.py  
```

# Using the API

## Routes

#### GET

Index route `/` to check the server health

#### POST

`/Download` to download a YouTube or Instagram video

Payload structure:

```json
{
    "url":,             # The url for the video to download
    "ext":,             # (OPTIONAL) The desired file extension (default: mp4) 
    "audio_only":       # Boolean value for downloading audio only or with the video
}
```

# Future Work

- Support TikTok
- Support X (Formerly Twitter)
- Support Reddit
- Support Spotify
- Make a Telegram bot
- Replace spaces in file names with underscores
- Download by searching for a video
- Download video with no audio
- Implement resolution for caching
- Download playlists
- Create an interface

---

# Credits

- For YouTube: [pytube](https://github.com/pytube/pytube)
- For Instagram: [instaloader](https://github.com/instaloader/instaloader)
