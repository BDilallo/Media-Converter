import shutil
from pathlib import Path
from moviepy.editor import VideoFileClip, AudioFileClip
from PIL import Image

VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
AUDIO_EXTS = {".mp3", ".wav", ".m4a", ".flac", ".ogg"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tiff"}

summary = {
    "converted": 0,
    "copied": 0,
    "skipped": 0,
    "failed": 0
}

correct_format_files = []
failed_files = []
skipped_files = []


def get_target():
    while True:
        target = input("Enter target file or folder path: ").strip()
        if not target:
            print("Please enter a valid path")
            continue

        target_path = Path(target)
        if not target_path.exists():
            print("That path does not exist. Try again.")
            continue

        return target_path


def get_output_folder(default_dir):
    out = input(f"Enter output folder (press Enter for default): ").strip()
    if not out:
        return default_dir, False

    out_path = Path(out)
    while not out_path.exists() or not out_path.is_dir():
        retry = input("Invalid folder. Re-enter path or press Enter to skip: ").strip()
        if not retry:
            return default_dir, False
        out_path = Path(retry)
    return out_path, True


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
        ".ogg": "libvorbis"
    }.get(ext, "aac")


def copy_same_format(src: Path, dest: Path):
    if src.suffix.lower() == dest.suffix.lower():
        if dest.exists(): dest = get_unique_file_path(dest)
        shutil.copy2(src, dest)
        summary["copied"] += 1
        correct_format_files.append(dest.name)
        print(f"Copied (already correct format): {src.name}")
        return True
    return False


def convert_video_to_video(src: Path, dest: Path):
    clip = VideoFileClip(str(src))
    audio_present = clip.audio is not None
    if dest.suffix.lower() == ".webm":
       clip.write_videofile(str(dest), codec="libvpx-vp9", audio_codec="libopus" if audio_present else None) 
    else: clip.write_videofile(str(dest), codec="libx264", audio_codec="aac" if audio_present else None)
    clip.close()
    summary["converted"] += 1


def convert_video_to_audio(src: Path, dest: Path):
    clip = VideoFileClip(str(src))
    if clip.audio is None:
        clip.close()
        summary["skipped"] += 1
        skipped_files.append(src.name)
        print(f"Skipped (no audio): {src.name}")
        return
    codec = audio_codec_for_ext(dest.suffix.lower())
    clip.audio.write_audiofile(str(dest), codec=codec)
    clip.close()
    summary["converted"] += 1

def convert_audio_to_audio(src: Path, dest: Path):
    clip = AudioFileClip(str(src))
    codec = audio_codec_for_ext(dest.suffix.lower())
    clip.write_audiofile(str(dest), codec=codec)
    clip.close()
    summary["converted"] += 1

def convert_image_to_image(src: Path, dest: Path):
    img = Image.open(src)
    if dest.suffix.lower() in {".jpg", ".jpeg"} and img.mode != "RGB":
        img = img.convert("RGB")
    img.save(dest)
    img.close()
    summary["converted"] += 1

def convert_single_file(src: Path, out_dir: Path):
    ftype = detect_type(src)
    if not ftype:
        print(f"Skipped (unsupported type): {src.name}")
        summary["skipped"] += 1
        skipped_files.append(src.name)
        return

    print(f"Detected file type: {ftype.upper()}")

    try:
        if ftype == "video":
            choice = choose_conversion_for_video()
            if choice == "1":
                dest_ext = choose_extension(ftype)
                dest = get_unique_file_path(out_dir / f"{src.stem}.{dest_ext}")
                if copy_same_format(src, dest):
                    return
                convert_video_to_video(src, dest)

            else:
                dest_ext = choose_extension("audio")
                dest = get_unique_file_path(out_dir / f"{src.stem}.{dest_ext}")
                if copy_same_format(src, dest):
                    return
                convert_video_to_audio(src, dest)

        elif ftype == "audio":
            dest_ext = choose_extension(ftype)
            dest = get_unique_file_path(out_dir / f"{src.stem}.{dest_ext}")
            if copy_same_format(src, dest):
                return
            convert_audio_to_audio(src, dest)

        elif ftype == "image":
            dest_ext = choose_extension(ftype)
            dest = get_unique_file_path(out_dir / f"{src.stem}.{dest_ext}")
            if copy_same_format(src, dest):
                return
            convert_image_to_image(src, dest)

    except Exception as e:
        print(f"Failed to convert {src.name}: {e}")
        summary["failed"] += 1
        failed_files.append(src.name)


def convert_folder(folder: Path, out_dir: Path):
    files = [f for f in folder.iterdir() if f.is_file()]
    types = {"video": [], "audio": [], "image": []}

    for f in files:
        ftype = detect_type(f)
        if ftype:
            types[ftype].append(f)
        else:
            skipped_files.append(f.name)
            print(f"Skipped (unsupported type): {f.name}")
            summary["skipped"] += 1

    non_empty = {k: v for k, v in types.items() if v}

    if len(non_empty) == 1:
        ftype = list(non_empty.keys())[0]
        print(f"Folder contains only {ftype} files.")
        convert_all_same_type(ftype, non_empty[ftype], out_dir)

    else:
        print("Folder contains multiple file types.")
        for ftype, flist in non_empty.items():

            print(f"\n{ftype.upper()} files found: {len(flist)}")

            if ftype == "video":
                choice = choose_conversion_for_video()
                if choice == "1":
                    dest_ext = choose_extension(ftype)
                    for f in flist:
                        dest = get_unique_file_path(out_dir / f"{f.stem}.{dest_ext}")
                        if copy_same_format(f, dest):
                            continue
                        convert_video_to_video(f, dest)
                else:
                    dest_ext = choose_extension("audio")
                    for f in flist:
                        dest = get_unique_file_path(out_dir / f"{f.stem}.{dest_ext}")
                        if copy_same_format(f, dest):
                            continue
                        convert_video_to_audio(f, dest)

            elif ftype == "audio":
                dest_ext = choose_extension(ftype)
                for f in flist:
                    dest = get_unique_file_path(out_dir / f"{f.stem}.{dest_ext}")
                    if copy_same_format(f, dest):
                        continue
                    convert_audio_to_audio(f, dest)

            elif ftype == "image":
                dest_ext = choose_extension(ftype)
                for f in flist:
                    dest = get_unique_file_path(out_dir / f"{f.stem}.{dest_ext}")
                    if copy_same_format(f, dest):
                        continue
                    convert_image_to_image(f, dest)

def convert_all_same_type(ftype, files, out_dir):
    if ftype == "video":
        choice = choose_conversion_for_video()

        if choice == "1":
            dest_ext = choose_extension(ftype)
            for f in files:
                dest = get_unique_file_path(out_dir / f"{f.stem}.{dest_ext}")
                if copy_same_format(f, dest):
                    continue
                try:
                    convert_video_to_video(f, dest)
                except Exception as e:
                    print(f"Failed: {f.name} - {e}")
                    summary["failed"] += 1
                    failed_files.append(f.name)

        else:
            dest_ext = choose_extension("audio")
            for f in files:
                dest = get_unique_file_path(out_dir / f"{f.stem}.{dest_ext}")
                if copy_same_format(f, dest):
                    continue
                try:
                    convert_video_to_audio(f, dest)
                except Exception as e:
                    print(f"Failed: {f.name} - {e}")
                    summary["failed"] += 1
                    failed_files.append(f.name)

    elif ftype == "audio":
        dest_ext = choose_extension(ftype)
        for f in files:
            dest = get_unique_file_path(out_dir / f"{f.stem}.{dest_ext}")
            if copy_same_format(f, dest):
                continue
            try:
                convert_audio_to_audio(f, dest)
            except Exception as e:
                print(f"Failed: {f.name} - {e}")
                summary["failed"] += 1
                failed_files.append(f.name)

    elif ftype == "image":
        dest_ext = choose_extension(ftype)
        for f in files:
            dest = get_unique_file_path(out_dir / f"{f.stem}.{dest_ext}")
            if copy_same_format(f, dest):
                continue
            try:
                convert_image_to_image(f, dest)
            except Exception as e:
                print(f"Failed: {f.name} - {e}")
                summary["failed"] += 1
                failed_files.append(f.name)

def choose_conversion_for_video():
    while True:
        print("Video conversion options:")
        print("1) Video → Video")
        print("2) Video → Audio")
        choice = input("Choose (1/2): ").strip()
        if choice in ("1", "2"):
            return choice
        print("Invalid Selection")

def choose_extension(ftype):
    if ftype == "video":
        while True:
            dest_ext = input("Enter video extension of output (mp4, mov, avi, mkv, webm): ").strip().lower()
            if dest_ext in ("mp4", "mov", "avi", "mkv", "webm"):
                return dest_ext
            print("Invalid Selection")
    elif ftype == "audio":
        while True:
            dest_ext = input("Enter audio extension of output (mp3, wav, m4a, flac, ogg): ").strip().lower()
            if dest_ext in ("mp3", "wav", "m4a", "flac", "ogg"):
                return dest_ext
            print("Invalid Selection")
    elif ftype == "image":
        while True:
            dest_ext = input("Enter image extension of output (png, jpg, jpeg, bmp, gif, tiff): ").strip().lower()
            if dest_ext in ("png", "jpg", "jpeg", "webp", "bmp", "gif", "tiff"):
                return dest_ext
            print("Invalid Selection")


def print_summary():
    print("\n==== SUMMARY ====")
    print(f"Converted: {summary['converted']}")
    print(f"Copied (already correct format): {summary['copied']}")
    if summary["copied"] > 0:
        print("  - Files already correct format:")
        for f in correct_format_files:
            print(f"    • {f}")

    print(f"Skipped: {summary['skipped']}")
    if summary["skipped"] > 0:
        print("  - Skipped files:")
        for f in skipped_files:
            print(f"    • {f}")
    print(f"Failed: {summary['failed']}")
    if summary["failed"] > 0:
        print("  - Failed files:")
        for f in failed_files:
            print(f"    • {f}")

    print("=================")

def get_unique_output_folder(base_dir: Path) -> Path:
    if not base_dir.exists():
        return base_dir

    i = 1
    while True:
        candidate = base_dir.parent / f"{base_dir.name} ({i})"
        if not candidate.exists():
            return candidate
        i += 1

def get_unique_file_path(dest: Path) -> Path:
    if not dest.exists():
        return dest

    i = 1
    while True:
        candidate = dest.parent / f"{dest.stem} ({i}){dest.suffix}"
        if not candidate.exists():
            return candidate
        i += 1

def main():
    target = get_target()

    if target.is_file():
        default_out = target.parent / "Converted Media"
    else:
        default_out = target / "Converted Media"

    out_dir, choice = get_output_folder(default_out)
    if not choice: out_dir = get_unique_output_folder(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if target.is_file():
        convert_single_file(target, out_dir)

    elif target.is_dir():
        convert_folder(target, out_dir)
    else:
        print("Target is neither a file nor folder.")
        summary["failed"] += 1

    print_summary()

if __name__ == "__main__":
    main()
