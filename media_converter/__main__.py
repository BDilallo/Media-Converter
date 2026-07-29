from .batch import convert_folder, convert_single_file
from .cli import get_output_folder, get_target
from .paths import get_unique_output_folder
from .report import Report


def main():
    target = get_target()

    if target.is_file():
        default_out = target.parent / "Converted Media"
    else:
        default_out = target / "Converted Media"

    out_dir, is_custom = get_output_folder(default_out)
    if not is_custom:
        out_dir = get_unique_output_folder(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    report = Report()

    if target.is_file():
        convert_single_file(target, out_dir, report)
    elif target.is_dir():
        convert_folder(target, out_dir, report)
    else:
        print("Target is neither a file nor folder.")
        report.record_failed(str(target))

    report.print()


if __name__ == "__main__":
    main()
