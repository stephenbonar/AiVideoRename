# AiVideoRename

A script for renaming video files based on date taken and an AI caption.

## Overview

This Python script renames video files by appending:
1. Date taken from video metadata (in YYYYMMDD format)
2. AI-generated caption in PascalCase

The resulting format is: `OriginalName_YYYYMMDD_AiCaption.ext`

## Features

- **Pure Python**: Uses only Python standard library, no external dependencies required
- **Date Extraction**: Extracts creation date from file metadata
- **AI Captioning**: Generates captions based on filename (placeholder for future AI integration)
- **PascalCase Formatting**: Converts captions to PascalCase (e.g., "MyVacationVideo")
- **Batch Processing**: Process single files or entire directories
- **Recursive Mode**: Optionally process subdirectories
- **Dry Run**: Preview changes before applying them
- **Smart Skipping**: Automatically skips already-renamed files
- **Multiple Formats**: Supports common video formats (mp4, avi, mov, mkv, flv, wmv, m4v, mpg, mpeg, 3gp, webm)

## Installation

No installation required! Just download `aivideorename.py` and make it executable:

```bash
chmod +x aivideorename.py
```

## Usage

### Basic Usage

Rename a single video file:
```bash
python3 aivideorename.py video.mp4
```

Rename all videos in a directory:
```bash
python3 aivideorename.py /path/to/videos/
```

### Advanced Options

Process directories recursively:
```bash
python3 aivideorename.py /path/to/videos/ -r
```

Preview changes without renaming (dry run):
```bash
python3 aivideorename.py video.mp4 --dry-run
```

Show help:
```bash
python3 aivideorename.py --help
```

## Examples

### Example 1: Single File
```bash
$ python3 aivideorename.py my_vacation.mp4

Renamed: my_vacation.mp4
     to: my_vacation_20251109_MyVacation.mp4
```

### Example 2: Directory with Dry Run
```bash
$ python3 aivideorename.py ~/Videos/ --dry-run

Found 3 video file(s)

Would rename: /home/user/Videos/summer_beach.mp4
         to: /home/user/Videos/summer_beach_20251109_SummerBeach.mp4

Would rename: /home/user/Videos/birthday_party.mov
         to: /home/user/Videos/birthday_party_20251109_BirthdayParty.mov

Would rename: /home/user/Videos/concert2023.avi
         to: /home/user/Videos/concert2023_20251109_Concert2023.avi

==================================================
Successfully renamed: 3
Failed: 0
```

### Example 3: Recursive Processing
```bash
$ python3 aivideorename.py ~/Videos/ -r

Found 5 video file(s)

Renamed: /home/user/Videos/vacation.mp4
     to: /home/user/Videos/vacation_20251109_Vacation.mp4

Renamed: /home/user/Videos/2023/NewYear.mov
     to: /home/user/Videos/2023/NewYear_20251109_NewYear.mov

Skipping (already renamed): /home/user/Videos/trip_20241015_FamilyTrip.mp4

==================================================
Successfully renamed: 5
Failed: 0
```

## File Naming Convention

The script follows this naming pattern:
```
OriginalName_YYYYMMDD_AiCaption.ext
```

Where:
- **OriginalName**: The original filename (without extension)
- **YYYYMMDD**: Date in format YYYYMMDD (e.g., 20251109 for November 9, 2025)
- **AiCaption**: AI-generated caption in PascalCase
- **ext**: Original file extension

Components are separated by underscores (`_`).

## Caption Generation

The current implementation uses a placeholder caption generator that:
1. Extracts the original filename
2. Preserves camelCase/PascalCase word boundaries
3. Converts underscores, hyphens, and dots to spaces
4. Normalizes to PascalCase format

**Future Enhancement**: This can be extended to use actual AI models (like CLIP or video analysis models) to generate descriptive captions based on video content.

## Date Extraction

The script currently uses file modification time as the creation date. For videos with embedded metadata, this can be enhanced with:
- FFmpeg integration for reading video metadata
- Exif data parsing for videos that support it
- Custom date extraction based on video format

## Requirements

- Python 3.6 or higher
- No external dependencies (pure Python standard library)

## License

See LICENSE file for details.

## Contributing

Contributions are welcome! Areas for enhancement:
- Integration with actual AI models for caption generation
- Enhanced metadata extraction using video-specific libraries
- Support for custom date/caption formats
- Batch undo functionality
- Configuration file support
