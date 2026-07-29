import shutil
from pathlib import Path

from moviepy.editor import VideoFileClip, AudioFileClip
from PIL import Image, ImageSequence

from .media_types import audio_codec_for_ext
from .paths import get_unique_file_path


class NoAudioTrackError(Exception):
    pass


def copy_same_format(src: Path, dest: Path):
    """If src and dest share an extension, copy src to dest (deduping the name)
    and return the final path used. Returns None if the extensions differ."""
    if src.suffix.lower() != dest.suffix.lower():
        return None

    if dest.exists():
        dest = get_unique_file_path(dest)
    shutil.copy2(src, dest)
    return dest


def convert_video_to_video(src: Path, dest: Path):
    clip = VideoFileClip(str(src))
    audio_present = clip.audio is not None
    if dest.suffix.lower() == ".webm":
        clip.write_videofile(str(dest), codec="libvpx-vp9", audio_codec="libopus" if audio_present else None)
    else:
        clip.write_videofile(str(dest), codec="libx264", audio_codec="aac" if audio_present else None)
    clip.close()


def convert_video_to_audio(src: Path, dest: Path):
    clip = VideoFileClip(str(src))
    if clip.audio is None:
        clip.close()
        raise NoAudioTrackError(src.name)
    codec = audio_codec_for_ext(dest.suffix.lower())
    clip.audio.write_audiofile(str(dest), codec=codec)
    clip.close()


def convert_audio_to_audio(src: Path, dest: Path):
    clip = AudioFileClip(str(src))
    codec = audio_codec_for_ext(dest.suffix.lower())
    clip.write_audiofile(str(dest), codec=codec)
    clip.close()


def convert_image_to_image(src: Path, dest: Path):
    img = Image.open(src)
    is_animated = getattr(img, "n_frames", 1) > 1

    if is_animated:
        frames = [frame.convert("RGB") if dest.suffix.lower() in {".jpg", ".jpeg"} else frame.copy()
                  for frame in ImageSequence.Iterator(img)]
        frames[0].save(dest, save_all=True, append_images=frames[1:], loop=img.info.get("loop", 0),
                        duration=img.info.get("duration", 100))
    else:
        if dest.suffix.lower() in {".jpg", ".jpeg"} and img.mode != "RGB":
            img = img.convert("RGB")
        img.save(dest)

    img.close()
