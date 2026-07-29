from pathlib import Path

VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
AUDIO_EXTS = {".mp3", ".wav", ".m4a", ".flac", ".ogg"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tiff"}


def detect_type(file_path: Path):
    ext = file_path.suffix.lower()
    if ext in VIDEO_EXTS:
        return "video"
    if ext in AUDIO_EXTS:
        return "audio"
    if ext in IMAGE_EXTS:
        return "image"
    return None


def audio_codec_for_ext(ext: str):
    return {
        ".mp3": "libmp3lame",
        ".wav": "pcm_s16le",
        ".m4a": "aac",
        ".flac": "flac",
        ".ogg": "libvorbis",
    }.get(ext, "aac")
