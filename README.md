# Media-Converter

A small interactive CLI tool for converting video, audio, and image files. Point it
at a single file or a whole folder, and it walks you through picking an output
format per media type, then converts everything and prints a summary.

## Features

- Convert a single file or batch-convert an entire folder
- Handles video, audio, and image files in the same run (a mixed folder is split
  out by type, and you're prompted for each type it finds)
- Video can be converted to another video format or extracted straight to audio
- Files already in the target format are copied as-is instead of being re-encoded
- Animated GIF/WebP images are converted frame-by-frame, not flattened to a still
- Output filenames are deduped automatically (`name (1).ext`, `name (2).ext`, ...)
  so existing files are never overwritten
- Ends with a summary: converted / copied / skipped / failed counts, with the
  filenames for each

## Supported formats

| Type  | Extensions |
|-------|------------|
| Video | mp4, mov, avi, mkv, webm |
| Audio | mp3, wav, m4a, flac, ogg |
| Image | png, jpg, jpeg, webp, bmp, gif, tiff |

## Requirements

- Python 3.9+
- [ffmpeg](https://ffmpeg.org/) available on your `PATH` (used by `moviepy` for
  video/audio conversion)
- Python packages: `moviepy`, `pillow`

Install the Python dependencies with:

```
pip install moviepy pillow
```

## Usage

```
python -m media_converter
```

You'll be prompted for:

1. **Target path** — a single file, or a folder to batch-convert
2. **Output folder** — press Enter to use a `Converted Media` folder created next
   to the target
3. **Output format(s)** — one prompt per media type found (e.g. choose "Video →
   Audio" and an output extension, or just an image/audio extension)

Converted files land in the output folder; the run ends with a summary of what
was converted, copied, skipped, or failed.

## Project layout

```
media_converter/
  __main__.py      entry point (python -m media_converter)
  cli.py           interactive prompts
  batch.py         orchestrates single-file and folder conversions
  converters.py    the actual video/audio/image conversion logic
  media_types.py   extension → media type detection
  paths.py         unique filename/folder helpers
  report.py        tracks and prints the end-of-run summary
```
