from pathlib import Path


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
