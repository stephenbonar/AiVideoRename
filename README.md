# AiVideoRename

A script for renaming video files based on date taken and an AI caption.

## Overview

This Python script renames video files by appending:

1. Date taken from video metadata (in YYYYMMDD format)
2. AI-generated caption in PascalCase

The resulting format is: `YYYYMMDD_AiCaption_OriginalName.ext`

## Features

- **Pure Python**: Uses only Python standard library, no external dependencies required
- **Date Extraction**: Extracts creation date from file metadata
- **AI Captioning**: Generates captions based on video content
- **Batch Processing**: Process single files or entire directories
- **Recursive Mode**: Optionally process subdirectories
- **Dry Run**: Preview changes before applying them
- **Smart Skipping**: Automatically skips already-renamed files
- **Multiple Formats**: Supports common video formats (mp4, avi, mov, mkv, flv, wmv, m4v, mpg, mpeg, 3gp, webm)

# Installation

1. Download the latest release of the script and extract it from the zip file.
2. Install the Python dependencies for the script using pip. 
Use a Python virtual environment in the extracted script's directory if you'd like, installing the dependencies in the virtual environment and activating it:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install hachoir opencv-python pillow torch torchvision transformers
```

NOTE: if you decide to go the virtual environment route, do not forget to activate the environment each time you run the script.

3. Initialize the script by running the following command:

```bash
python3 aivideorename.py --init
```

This downloads the AI models locally and caches them in your user profile.
The models get cached in ~/.cache/huggingface.
You only need to use the --init parameter once.
The next time you run the script, it will use the AI models locally.

## Usage

Rename a single video file:

```bash
python3 aivideorename.py video.mp4
```

Rename all videos in a directory:

```bash
python3 aivideorename.py /path/to/videos/
```

Process directories recursively:

```bash
python3 aivideorename.py /path/to/videos/ --recursive
```

Preview changes without renaming (dry run):

```bash
python3 aivideorename.py video.mp4 --dry-run
```

Prompt for confirmation before each rename:

```bash
python3 aivideorename.py video.mp4 --confirm
```

Show help:

```bash
python3 aivideorename.py --help
```