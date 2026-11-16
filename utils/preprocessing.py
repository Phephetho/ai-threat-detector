import os
from typing import Tuple

MAX_TEXT_SIZE = 1 * 1024 * 1024
MAX_IMAGE_SIZE = 10 * 1024 * 1024
MAX_AUDIO_SIZE = 50 * 1024 * 1024
MAX_VIDEO_SIZE = 100 * 1024 * 1024

SUPPORTED_TEXT_TYPES = {".txt", ".eml"}
SUPPORTED_IMAGE_TYPES = {".jpg", ".jpeg", ".png", ".webp"}
SUPPORTED_AUDIO_TYPES = {".wav", ".mp3", ".flac", ".m4a"}
SUPPORTED_VIDEO_TYPES = {".mp4", ".avi", ".mov", ".mkv"}


def validate_email_text(text: str) -> Tuple[bool, str]:
    if not text or not text.strip():
        return False, "Email text is empty."
    if len(text.encode("utf-8")) > MAX_TEXT_SIZE:
        return False, f"Email text exceeds {MAX_TEXT_SIZE // (1024 * 1024)} MB limit."
    if len(text.strip()) < 10:
        return False, "Email text is too short to analyse reliably."
    return True, "Valid."


def validate_image(file_name: str, file_size: int) -> Tuple[bool, str]:
    ext = os.path.splitext(file_name)[1].lower()
    if ext not in SUPPORTED_IMAGE_TYPES:
        return False, f"Unsupported image type: {ext}."
    if file_size > MAX_IMAGE_SIZE:
        return False, f"Image exceeds {MAX_IMAGE_SIZE // (1024 * 1024)} MB limit."
    return True, "Valid."


def validate_audio(file_name: str, file_size: int) -> Tuple[bool, str]:
    ext = os.path.splitext(file_name)[1].lower()
    if ext not in SUPPORTED_AUDIO_TYPES:
        return False, f"Unsupported audio type: {ext}."
    if file_size > MAX_AUDIO_SIZE:
        return False, f"Audio exceeds {MAX_AUDIO_SIZE // (1024 * 1024)} MB limit."
    return True, "Valid."


def validate_video(file_name: str, file_size: int) -> Tuple[bool, str]:
    ext = os.path.splitext(file_name)[1].lower()
    if ext not in SUPPORTED_VIDEO_TYPES:
        return False, f"Unsupported video type: {ext}."
    if file_size > MAX_VIDEO_SIZE:
        return False, f"Video exceeds {MAX_VIDEO_SIZE // (1024 * 1024)} MB limit."
    return True, "Valid."


def format_confidence(value: float) -> str:
    if value is None:
        return "N/A"
    return f"{value * 100:.1f}%"


def format_inference_time(seconds: float) -> str:
    if seconds is None:
        return "N/A"
    if seconds < 1:
        return f"{seconds * 1000:.0f} ms"
    return f"{seconds:.2f} s"