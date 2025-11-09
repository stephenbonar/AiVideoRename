#!/usr/bin/env python3
"""
AiVideoRename - A script for renaming video files based on date taken and AI caption.

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


def extract_creation_date(video_path: str) -> Optional[str]:
    """
    Extract creation date from video metadata.
    
    Args:
        video_path: Path to the video file
        
    Returns:
        Date string in YYYYMMDD format, or None if not found
    """
    try:
        # Try to get file creation/modification time as fallback
        stat = os.stat(video_path)
        # Use modification time as it's more reliable cross-platform
        timestamp = stat.st_mtime
        date_obj = datetime.fromtimestamp(timestamp)
        return date_obj.strftime('%Y%m%d')
    except Exception as e:
        print(f"Error extracting date from {video_path}: {e}", file=sys.stderr)
        return None


def generate_ai_caption(video_path: str) -> Optional[str]:
    """
    Generate an AI caption for the video.
    
    For now, this is a placeholder that extracts meaningful info from filename.
    Can be extended with actual AI models in the future.
    
    Args:
        video_path: Path to the video file
        
    Returns:
        AI-generated caption (preserving word boundaries), or None if generation fails
    """
    try:
        # Placeholder: Extract base name and create a simple caption
        # In a real implementation, this would use an AI model to analyze the video
        basename = Path(video_path).stem
        
        # First, preserve camelCase/PascalCase boundaries by adding spaces
        caption = re.sub(r'([a-z])([A-Z])', r'\1 \2', basename)
        # Also handle numbers
        caption = re.sub(r'([a-zA-Z])(\d)', r'\1 \2', caption)
        caption = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', caption)
        
        # Now replace underscores, hyphens, dots with spaces
        caption = re.sub(r'[_\-\.]', ' ', caption)
        caption = re.sub(r'\s+', ' ', caption).strip()
        
        # For now, return a generic caption based on file info
        # This is a placeholder for actual AI captioning
        if not caption:
            caption = "video file"
        
        return caption.lower()
    except Exception as e:
        print(f"Error generating caption for {video_path}: {e}", file=sys.stderr)
        return None


def to_pascal_case(text: str) -> str:
    """
    Convert text to PascalCase.
    
    Args:
        text: Input text
        
    Returns:
        Text in PascalCase format
    """
    # First, insert spaces before uppercase letters in camelCase/PascalCase
    # to preserve word boundaries
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    # Also handle numbers by adding space before them if preceded by letter
    text = re.sub(r'([a-zA-Z])(\d)', r'\1 \2', text)
    # And space after numbers if followed by letter
    text = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', text)
    
    # Split on spaces, underscores, hyphens
    words = re.split(r'[\s_\-]+', text)
    # Capitalize first letter of each word, keep rest lowercase
    pascal = ''.join(word.capitalize() for word in words if word)
    return pascal


def get_new_filename(original_path: str, date_str: str, caption: str) -> str:
    """
    Generate new filename based on original name, date, and caption.
    
    Args:
        original_path: Original file path
        date_str: Date string in YYYYMMDD format
        caption: AI caption in lowercase
        
    Returns:
        New filename with format: OriginalName_YYYYMMDD_AiCaptionPascal.ext
    """
    path_obj = Path(original_path)
    original_name = path_obj.stem
    extension = path_obj.suffix
    
    # Convert caption to PascalCase
    pascal_caption = to_pascal_case(caption)
    
    # Build new filename
    new_name = f"{original_name}_{date_str}_{pascal_caption}{extension}"
    
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
    # Check if filename matches pattern: *_YYYYMMDD_*
    # where YYYYMMDD is 8 digits followed by underscore and PascalCase text
    # PascalCase starts with uppercase letter and can contain letters/numbers
    pattern = r'.*_\d{8}_[A-Z][a-zA-Z0-9]*$'
    return bool(re.match(pattern, stem))


def rename_video(video_path: str, dry_run: bool = False) -> bool:
    """
    Rename a video file with date and AI caption.
    
    Args:
        video_path: Path to the video file
        dry_run: If True, only show what would be done without renaming
        
    Returns:
        True if successful, False otherwise
    """
    if not os.path.exists(video_path):
        print(f"Error: File not found: {video_path}", file=sys.stderr)
        return False
    
    # Check if file is already renamed
    filename = os.path.basename(video_path)
    if is_already_renamed(filename):
        print(f"Skipping (already renamed): {video_path}")
        return True
    
    # Extract date from metadata
    date_str = extract_creation_date(video_path)
    if not date_str:
        print(f"Warning: Could not extract date for {video_path}", file=sys.stderr)
        return False
    
    # Generate AI caption
    caption = generate_ai_caption(video_path)
    if not caption:
        print(f"Warning: Could not generate caption for {video_path}", file=sys.stderr)
        return False
    
    # Generate new filename
    directory = os.path.dirname(video_path)
    new_filename = get_new_filename(video_path, date_str, caption)
    new_path = os.path.join(directory if directory else '.', new_filename)
    
    # Check if file already exists
    if os.path.exists(new_path) and new_path != video_path:
        print(f"Error: Target file already exists: {new_path}", file=sys.stderr)
        return False
    
    if dry_run:
        print(f"Would rename: {video_path}")
        print(f"         to: {new_path}")
    else:
        try:
            os.rename(video_path, new_path)
            print(f"Renamed: {video_path}")
            print(f"     to: {new_path}")
        except Exception as e:
            print(f"Error renaming {video_path}: {e}", file=sys.stderr)
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
    video_extensions = {
        '.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', 
        '.m4v', '.mpg', '.mpeg', '.3gp', '.webm'
    }
    ext = Path(filename).suffix.lower()
    return ext in video_extensions


def process_directory(directory: str, recursive: bool = False, dry_run: bool = False) -> Dict[str, int]:
    """
    Process all video files in a directory.
    
    Args:
        directory: Directory path to process
        recursive: If True, process subdirectories recursively
        dry_run: If True, only show what would be done
        
    Returns:
        Dictionary with 'success' and 'failed' counts
    """
    results = {'success': 0, 'failed': 0}
    
    if not os.path.isdir(directory):
        print(f"Error: Not a directory: {directory}", file=sys.stderr)
        return results
    
    # Get list of video files
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
            if os.path.isfile(os.path.join(directory, f)) and is_video_file(f)
        ]
    
    if not video_files:
        print(f"No video files found in {directory}")
        return results
    
    print(f"Found {len(video_files)} video file(s)")
    print()
    
    for video_file in video_files:
        if rename_video(video_file, dry_run):
            results['success'] += 1
        else:
            results['failed'] += 1
        print()
    
    return results


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Rename video files with date taken and AI caption',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s video.mp4                    # Rename single video file
  %(prog)s /path/to/videos/             # Rename all videos in directory
  %(prog)s /path/to/videos/ -r          # Rename videos recursively
  %(prog)s video.mp4 --dry-run          # Show what would be done
        """
    )
    
    parser.add_argument(
        'path',
        help='Path to video file or directory'
    )
    
    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Process directories recursively'
    )
    
    parser.add_argument(
        '-n', '--dry-run',
        action='store_true',
        help='Show what would be done without actually renaming'
    )
    
    args = parser.parse_args()
    
    # Check if path exists
    if not os.path.exists(args.path):
        print(f"Error: Path not found: {args.path}", file=sys.stderr)
        sys.exit(1)
    
    # Process path
    if os.path.isfile(args.path):
        if not is_video_file(args.path):
            print(f"Error: Not a video file: {args.path}", file=sys.stderr)
            sys.exit(1)
        
        success = rename_video(args.path, args.dry_run)
        sys.exit(0 if success else 1)
    
    elif os.path.isdir(args.path):
        results = process_directory(args.path, args.recursive, args.dry_run)
        
        print("=" * 50)
        print(f"Successfully renamed: {results['success']}")
        print(f"Failed: {results['failed']}")
        
        sys.exit(0 if results['failed'] == 0 else 1)
    
    else:
        print(f"Error: Invalid path: {args.path}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
