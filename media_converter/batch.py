from pathlib import Path

from .cli import choose_conversion_for_video, choose_extension
from .converters import (
    NoAudioTrackError,
    convert_audio_to_audio,
    convert_image_to_image,
    convert_video_to_audio,
    convert_video_to_video,
    copy_same_format,
)
from .media_types import detect_type
from .paths import get_unique_file_path
from .report import Report


def _run_conversion(src: Path, dest: Path, convert_fn, report: Report):
    copied_dest = copy_same_format(src, dest)
    if copied_dest is not None:
        print(f"Copied (already correct format): {src.name}")
        report.record_copied(copied_dest.name)
        return

    try:
        convert_fn(src, dest)
        report.record_converted()
    except NoAudioTrackError:
        print(f"Skipped (no audio): {src.name}")
        report.record_skipped(src.name)
    except Exception as e:
        print(f"Failed: {src.name} - {e}")
        report.record_failed(src.name)


def convert_single_file(src: Path, out_dir: Path, report: Report):
    ftype = detect_type(src)
    if not ftype:
        print(f"Skipped (unsupported type): {src.name}")
        report.record_skipped(src.name)
        return

    print(f"Detected file type: {ftype.upper()}")
    convert_all_same_type(ftype, [src], out_dir, report)


def convert_folder(folder: Path, out_dir: Path, report: Report):
    files = [f for f in folder.iterdir() if f.is_file()]
    types = {"video": [], "audio": [], "image": []}

    for f in files:
        ftype = detect_type(f)
        if ftype:
            types[ftype].append(f)
        else:
            print(f"Skipped (unsupported type): {f.name}")
            report.record_skipped(f.name)

    non_empty = {k: v for k, v in types.items() if v}

    if not non_empty:
        print("No supported files found.")
        return

    if len(non_empty) == 1:
        ftype = next(iter(non_empty))
        print(f"Folder contains only {ftype} files.")
    else:
        print("Folder contains multiple file types.")

    for ftype, flist in non_empty.items():
        if len(non_empty) > 1:
            print(f"\n{ftype.upper()} files found: {len(flist)}")
        convert_all_same_type(ftype, flist, out_dir, report)


def convert_all_same_type(ftype: str, files, out_dir: Path, report: Report):
    if ftype == "video":
        choice = choose_conversion_for_video()
        if choice == "1":
            convert_fn = convert_video_to_video
            dest_ext = choose_extension("video")
        else:
            convert_fn = convert_video_to_audio
            dest_ext = choose_extension("audio")
    elif ftype == "audio":
        convert_fn = convert_audio_to_audio
        dest_ext = choose_extension("audio")
    elif ftype == "image":
        convert_fn = convert_image_to_image
        dest_ext = choose_extension("image")
    else:
        return

    for f in files:
        dest = get_unique_file_path(out_dir / f"{f.stem}.{dest_ext}")
        _run_conversion(f, dest, convert_fn, report)
