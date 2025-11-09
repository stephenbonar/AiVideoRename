#!/usr/bin/env python3
#
# Copyright (C) 2025 Stephen Bonar
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""
AiVideoRename - A script for renaming video files based on date taken and AI
caption.

This script renames video files by appending:
1. Date taken from video metadata (YYYYMMDD format)
2. AI-generated caption in PascalCase

Format: OriginalName_YYYYMMDD_AiCaption.ext
"""

import os
import sys
import argparse
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
import cv2
from PIL import Image
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration

MODEL_NAME = "Salesforce/blip-image-captioning-base"
TOKENS_TO_SKIP = {
    'a', 'an', 'the', 'in', 'on', 'at', 'of', 'and', 'or', 'is',
    'are', 'was', 'were', 'with', 'to', 'for', 'around', 'that'
}
VIDEO_EXTENSIONS = {
    '.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv',
    '.m4v', '.mpg', '.mpeg', '.3gp', '.webm'
}
PROGRAM_NAME = "AI Video Renamer"
PROGRAM_VERSION = "v1.0.0"
PROGRAM_COPYRIGHT = "Copyright (C) 2025 Stephen Bonar"


def extract_creation_date(path: str) -> Optional[str]:
    """
    Extract creation date from video metadata using hachoir.

    Args:
        path: Path to the video file

    Returns:
        Date string in YYYYMMDD format, or None if not found
    """
    try:
        # Create a hachoir parser for the video file so we can extract metadata.
        parser = createParser(path)
        if not parser:
            raise Exception("Unable to parse file")
        
        metadata = extractMetadata(parser)
        if metadata:
            # Unlike photos, videos don't have date taken, so we use creation
            # date or date instead.
            date = metadata.get('creation_date') or metadata.get('date')

            if date:
                return date.strftime('%Y%m%d')
            else:
                print(
                    f"{path} does not contain date, skipping", file=sys.stderr
                )
                return None
    except Exception as e:
        print(f"Error extracting date from {path}: {e}", file=sys.stderr)
        return None


def generate_ai_caption(
    path: str, use_online: bool = False
) -> Optional[str]:
    """
    Generate an AI caption for the video by inspecting a frame.

    Args:
        path: Path to the video file
        use_online: If True, load models from HuggingFace online;
            else use local files

    Returns:
        AI-generated caption, or None if generation fails
    """
    try:
        # Open the video file using OpenCV so we can read the first frame.
        capture = cv2.VideoCapture(path)

        # Capture the first frame of the video so we can generate a caption.
        # This returns a tuple where success indicates if the read was 
        # successful and frame is the actual image data.
        success, frame = capture.read()

        # Release handles to the video file as we're done with it.
        capture.release()

        if not success or frame is None:
            raise Exception("Could not read frame from video")

        # OpenCV uses BGR format so we need to convert it to RGB for PIL.
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Now we convert to a PIL image so it can be captioned by the AI model.
        pil_image = Image.fromarray(frame_rgb)

        # Establishes the device to run the model on, either the GPU or CPU. GPU
        # is preferred if available as GPUs are much faster for AI and learning. 
        device = "cuda" if torch.cuda.is_available() else "cpu"

        # NOTE: On first run, take out the local_files_only=True to download the
        # model. This will download to ~/.cache/huggingface
        #
        # Loads a pre-trained BLIP image captioning processor from the Hugging
        # Face model hub.
        processor = BlipProcessor.from_pretrained(
            MODEL_NAME,
            local_files_only=not use_online,
            use_fast=True,
        )

        # Loads a pre-trained BLIP image captioning model from the Hugging Face
        # model hub and moves it to the selected device.
        model = BlipForConditionalGeneration.from_pretrained(MODEL_NAME).to(
            device
        )

        # Prepare the image for the model by preprocessing it and converting it
        # into PyTorch tensors, then moving the tensors to the selected device.
        tensors = processor(pil_image, return_tensors="pt").to(device)

        with torch.no_grad():
            # Obtain the batch of token IDs from the model by unpacking the 
            # tensors and passing them as key-value pairs to the model's 
            # generate method so we can generate a caption from the token ids.
            token_id_batch = model.generate(**tensors)

        # Obtains the full caption string by decoding the first set of token IDs
        # in the batch (there is only 1 batch) and skipping any special tokens 
        # like <pad> or <end>. This gives us a human-readable caption. That 
        # said, we will want to clean up the caption in the following lines to
        # make it more suitable for a filename.
        caption = processor.decode(token_id_batch[0], skip_special_tokens=True)

        return caption.lower()
    except Exception as e:
        print(
            f"Error generating caption for {path}: {e}",
            file=sys.stderr,
        )
        return None


def generate_filename(path: str, date: str, caption: str) -> str:
    """
    Generate new filename based on original name, date, and caption.

    Args:
        path: Original file path
        date: Date string in YYYYMMDD format
        caption: AI caption in lowercase

    Returns:
        New filename with format: OriginalName_YYYYMMDD_Caption.ext
    """
    path_obj = Path(path)
    original_name = path_obj.stem
    extension = path_obj.suffix
    new_name = f"{original_name}_{date}_{caption}{extension}"
    return new_name


def is_already_renamed(filename: str) -> bool:
    """
    Check if a file has already been renamed by this script.

    A renamed file should have format: Name_YYYYMMDD_Caption.ext

    Args:
        filename: Name of the file (without directory)

    Returns:
        True if file appears to be already renamed, False otherwise
    """
    stem = Path(filename).stem
    pattern = r'.*_\d{8}_[A-Z][a-zA-Z0-9]*$'
    return bool(re.match(pattern, stem))


def rename_video(
    path: str,
    dry_run: bool = False,
    use_online: bool = False,
    confirm: bool = False,
) -> bool:
    """
    Rename a video file with date and AI caption.

    Args:
        path: Path to the video file
        dry_run: If True, only show what would be done without renaming
        use_online: If True, load models from HuggingFace online
        confirm: If True, prompt for confirmation before renaming

    Returns:
        True if successful, False otherwise
    """
    if not os.path.exists(path):
        print(
            f"Error: File not found: {path}",
            file=sys.stderr,
        )
        return False

    # We don't want to rename files that are already in the correct format.
    filename = os.path.basename(path)
    if is_already_renamed(filename):
        print(f"Skipping (already renamed): {path}")
        return True

    # Extract the creation date so we can append it to the filename.
    date_str = extract_creation_date(path)
    if not date_str:
        print(
            f"Error: Could not extract date for {path}",
            file=sys.stderr,
        )
        return False

    # Generate the AI caption so we can append it to the filename.
    full_caption = generate_ai_caption(path, use_online=use_online)
    if not full_caption:
        print(
            f"Error: Could not generate caption for {path}",
            file=sys.stderr,
        )
        return False

    # Remove unwanted tokens and convert to PascalCase so the caption doesn't
    # make the filename too long.
    caption = ""
    caption_tokens = full_caption.split()
    for token in caption_tokens:
        if token not in TOKENS_TO_SKIP:
            caption += token.capitalize()

    # Generate a new path using the new filename so we can rename the file.
    directory = os.path.dirname(path)
    new_filename = generate_filename(path, date_str, caption)
    new_path = os.path.join(directory if directory else ".", new_filename)

    # Skip the file if it already exists to avoid overwriting unnecessarily.
    if os.path.exists(new_path) and new_path != path:
        print(
            f"File already exists, skipping: {new_path}",
            file=sys.stderr,
        )
        return False
    
    print(f"Renaming {filename} to {new_filename}", end="")

    if dry_run:
        print(" (dry-run)")
    else:
        if confirm:
            response = input(" Proceed? [y/n]: ").strip().lower()
            if response != "y":
                print("Skipped.")
                return False
        else:
            print()

        try:
            os.rename(path, new_path)
        except Exception as e:
            print(
                f"Error renaming {path}: {e}",
                file=sys.stderr,
            )
            return False

    return True


def is_video_file(filename: str) -> bool:
    """
    Check if a file is a video file based on extension.

    Args:
        filename: Name of the file

    Returns:
        True if file is a video, False otherwise
    """
    
    ext = Path(filename).suffix.lower()
    return ext in VIDEO_EXTENSIONS


def process_directory(
    directory: str,
    recursive: bool = False,
    dry_run: bool = False,
    use_online: bool = False,
    confirm: bool = False,
) -> Dict[str, int]:
    """
    Process all video files in a directory.

    Args:
        directory: Directory path to process
        recursive: If True, process subdirectories recursively
        dry_run: If True, only show what would be done
        use_online: If True, load models from HuggingFace online
        confirm: If True, prompt for confirmation before renaming

    Returns:
        Dictionary with 'success' and 'failed' counts
    """
    results = {"success": 0, "failed": 0}

    if not os.path.isdir(directory):
        print(
            f"Error: Not a directory: {directory}",
            file=sys.stderr,
        )
        return results

    # Obtain a list of video files from the directory so we can rename each one.
    if recursive:
        video_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if is_video_file(file):
                    video_files.append(os.path.join(root, file))
    else:
        video_files = [
            os.path.join(directory, f)
            for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f))
            and is_video_file(f)
        ]

    if not video_files:
        print(f"No video files found in {directory}")
        return results

    print(f"Found {len(video_files)} video file(s)")
    print()

    for video_file in video_files:
        if rename_video(video_file, dry_run, use_online, confirm):
            results["success"] += 1
        else:
            results["failed"] += 1

    return results


def main():
    """Main entry point for the script."""

    parser = argparse.ArgumentParser(
        description="Rename video files with date taken and AI caption",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  %(prog)s video.mp4            # Rename single video file\n"
            "  %(prog)s /path/to/videos/     # Rename all videos in directory\n"
            "  %(prog)s /path/to/videos/ -r  # Rename videos recursively\n"
            "  %(prog)s video.mp4 --dry-run  # Show what would be done\n"
            "  %(prog)s video.mp4 --init     # Run AI models in online mode\n"
        ),
    )
    parser.add_argument(
        "path",
        nargs="?",
        help="Path to video file or directory",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Process directories recursively",
    )
    parser.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        help="Show what would be done without actually renaming",
    )
    parser.add_argument(
        "-i",
        "--init",
        action="store_true",
        help="Run AI models in online mode (download from HuggingFace)",
    )
    parser.add_argument(
        "-v", "--version",
        action="store_true",
        help="Print version information and exit"
    )
    parser.add_argument(
        "-c",
        "--confirm",
        action="store_true",
        help="Prompt for confirmation before renaming each file",
    )
    args = parser.parse_args()

    if args.version:
        print(f"{PROGRAM_NAME} {PROGRAM_VERSION}")
        print(PROGRAM_COPYRIGHT)
        sys.exit(0)

    if not args.path:
        print("Error: Path argument is required.", file=sys.stderr)
        parser.print_usage(sys.stderr)
        sys.exit(1)

    # Exit the script if the path doesn't exist as there is nothing to do.
    if not os.path.exists(args.path):
        print(
            f"Error: Path not found: {args.path}",
            file=sys.stderr,
        )
        sys.exit(1)

    if os.path.isfile(args.path):
        # Make sure the file is a video before attempting to rename it as we
        # don't want to rename other types of files.
        if not is_video_file(args.path):
            print(
                f"Error: Not a video file: {args.path}",
                file=sys.stderr,
            )
            sys.exit(1)

        # We're only renaming a single video as the specified path was a file.
        success = rename_video(
            args.path,
            args.dry_run,
            use_online=args.init,
            confirm=args.confirm,
        )

        sys.exit(0 if success else 1)
    elif os.path.isdir(args.path):
        # Since the specified path is a directory, we will rename all video 
        # files in that directory.
        results = process_directory(
            args.path,
            args.recursive,
            args.dry_run,
            use_online=args.init,
            confirm=args.confirm,
        )

        print("=" * 50)
        print(f"Successfully renamed: {results['success']}")
        print(f"Failed: {results['failed']}")

        sys.exit(0 if results["failed"] == 0 else 1)
    else:
        print(
            f"Error: Invalid path: {args.path}",
            file=sys.stderr,
        )
        sys.exit(1)

if __name__ == '__main__':
    main()
