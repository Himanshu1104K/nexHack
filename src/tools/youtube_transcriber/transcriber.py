# Minimal caption-only transcription using yt_dlp
import os
import re
from typing import Optional

import yt_dlp


os.makedirs("captions", exist_ok=True)


def _download_captions_srt(
    video_url: str,
    language_code: str = "en",
    output_dir: str = "captions",
) -> Optional[str]:
    """Download the best available .srt caption file for the given video.

    Returns the absolute path to the downloaded file or None if not available."""
    os.makedirs(output_dir, exist_ok=True)
    output_template = os.path.join(output_dir, "%(id)s.%(lang)s.%(ext)s")
    ydl_opts = {
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": [language_code],
        "subtitlesformat": "srt",
        "skip_download": True,
        "outtmpl": output_template,
        "quiet": True,
        "no_warnings": True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            video_id = info.get("id")
            if not video_id:
                return None
            expected_file = os.path.join(output_dir, f"{video_id}.{language_code}.srt")
            if os.path.exists(expected_file):
                return expected_file
            # Fallback: pick first SRT we find for the video
            for file in os.listdir(output_dir):
                if file.startswith(video_id) and file.endswith(".srt"):
                    return os.path.join(output_dir, file)
    except Exception:
        pass  # Silent fail – we'll fall back to Whisper.
    return None


def get_transcript(video_url: str, language_code: str | None = "en") -> str:
    """Return the transcript for a YouTube video using only YouTube captions.

    If captions are missing for the requested language, a RuntimeError is raised."""
    caption_path = _download_captions_srt(video_url, language_code or "en")
    if caption_path and os.path.exists(caption_path):
        with open(caption_path, "r", encoding="utf-8") as fp:
            return fp.read()
    raise RuntimeError("Captions not available for this video.")


__all__ = ["get_transcript"]
