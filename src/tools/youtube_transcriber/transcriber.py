import re
import os
from typing import Optional
from pydantic import BaseModel
import yt_dlp

# --- Setup ---

# Create directories
os.makedirs("captions", exist_ok=True)


# --- Pydantic Models ---
class VideoRequest(BaseModel):
    video_url: str
    language_code: Optional[str] = None


class TranscriptResponse(BaseModel):
    video_id: str
    transcript: str
    transcript_file: Optional[str] = None


# --- Helper Functions ---
def extract_video_id(url: str) -> str:
    """Extract video ID from various YouTube URL formats."""
    patterns = [
        r"(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})",
        r"youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})",
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    raise ValueError("Invalid YouTube URL format")


def download_captions_srt(
    video_url: str, language_code: str = "en", output_dir: str = "captions"
):
    """Downloads the best available .srt caption file."""
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

            # Fallback check
            for file in os.listdir(output_dir):
                if file.startswith(video_id) and file.endswith(".srt"):
                    return os.path.join(output_dir, file)

            return None

    except Exception as e:
        print(f"Error downloading captions: {e}")
        return None


async def get_transcript(video_url: str, language_code: Optional[str] = "en"):
    """
    Get transcript from YouTube video using captions only.
    """
    try:
        video_id = extract_video_id(video_url)
    except ValueError as e:
        raise RuntimeError(str(e))

    # Download captions
    language = language_code or "en"
    caption_file = download_captions_srt(video_url, language)

    if not caption_file or not os.path.exists(caption_file):
        raise RuntimeError(f"No captions available for language: {language}")

    # Read SRT file
    with open(caption_file, "r", encoding="utf-8") as f:
        transcript_text = f.read()

    return transcript_text


__all__ = ["get_transcript"]
