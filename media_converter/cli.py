from pathlib import Path


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
    out = input("Enter output folder (press Enter for default): ").strip()
    if not out:
        return default_dir, False

    out_path = Path(out)
    while not out_path.exists() or not out_path.is_dir():
        retry = input("Invalid folder. Re-enter path or press Enter to skip: ").strip()
        if not retry:
            return default_dir, False
        out_path = Path(retry)
    return out_path, True


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
            dest_ext = input("Enter image extension of output (png, jpg, jpeg, webp, bmp, gif, tiff): ").strip().lower()
            if dest_ext in ("png", "jpg", "jpeg", "webp", "bmp", "gif", "tiff"):
                return dest_ext
            print("Invalid Selection")
