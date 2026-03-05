# black_videos_cli.py
# -*- coding: utf-8 -*-
"""
USAGE EXAMPLES:
---------------
1. Process current directory:
   python black_videos_cli.py

2. Process a specific directory:
   python black_videos_cli.py "D:/Path/To/Media"

3. Process current directory and all subfolders (recursive):
   python black_videos_cli.py --recursive

4. Use GPU acceleration and more threads:
   python black_videos_cli.py --use-gpu --workers 8

5. Overwrite existing black videos:
   python black_videos_cli.py --overwrite

Note: Requires 'ap_core' module and 'ffmpeg' installed in system PATH.
"""
import os
import sys
import shutil
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

# Attempt to import ap_core; handle error if missing
try:
    from ap_core import (
        create_black_video,
        create_black_video_from_audio,
    )
except ImportError:
    print("❌ Error: 'ap_core' module not found.")
    print("   Make sure ap_core.py is in the same folder as this script.")
    sys.exit(1)

VIDEO_EXTENSIONS = (".mp4", ".mkv", ".mov", ".m4v")
AUDIO_AS_VIDEO_EXTENSIONS = (".opus", ".m4a", ".mp3", ".wav")


def check_dependencies():
    """Checks if ffmpeg is available in the system PATH."""
    if shutil.which("ffmpeg") is None:
        print("❌ Error: 'ffmpeg' is not recognized.")
        print("   [WinError 2] usually means ffmpeg is missing from your system PATH.")
        print("   Please install FFmpeg and add it to your PATH environment variable.")
        sys.exit(1)


def is_video_file(name: str) -> bool:
    return name.lower().endswith(VIDEO_EXTENSIONS)


def is_audio_as_video(name: str) -> bool:
    return name.lower().endswith(AUDIO_AS_VIDEO_EXTENSIONS)


def collect_files(directory: str, recursive: bool):
    tasks = []

    # Walk returns a generator, so we iterate
    if recursive:
        for root, _, files in os.walk(directory):
            for f in files:
                if (
                    (is_video_file(f) or is_audio_as_video(f))
                    and "_black" not in f
                ):
                    # Force absolute path and normalize separators
                    tasks.append(os.path.normpath(os.path.abspath(os.path.join(root, f))))
    else:
        for f in os.listdir(directory):
            full = os.path.join(directory, f)
            if (
                os.path.isfile(full)
                and (is_video_file(f) or is_audio_as_video(f))
                and "_black" not in f
            ):
                tasks.append(os.path.normpath(os.path.abspath(full)))

    return tasks


def main():
    parser = argparse.ArgumentParser(
        description="Create black-screen videos from video files and audio files."
    )
    
    parser.add_argument(
        "directory", 
        nargs='?', 
        default='.', 
        help="The directory to process (defaults to current directory if not specified)"
    )
    parser.add_argument("--recursive", action="store_true", help="Search subdirectories recursively")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing _black files")
    parser.add_argument("--workers", type=int, default=4, help="Number of concurrent threads (default: 4)")
    parser.add_argument("--use-gpu", action="store_true", help="Enable GPU acceleration if supported")

    args = parser.parse_args()
    
    # 1. Check for FFmpeg first to avoid WinError 2
    check_dependencies()

    # 2. robust directory handling
    target_dir = os.path.abspath(args.directory)

    if not os.path.isdir(target_dir):
        print(f"❌ Not a directory: {target_dir}")
        return

    print(f"📂 Processing directory: {target_dir}")
    files = collect_files(target_dir, args.recursive)
    print(f"🔍 Found {len(files)} media file(s).")

    def worker(path: str):
        try:
            # Double check file existence before processing
            if not os.path.exists(path):
                print(f"⚠️ Skipped (Not Found): {path}")
                return

            if is_video_file(path):
                create_black_video(
                    path,
                    overwrite=args.overwrite,
                    use_gpu=args.use_gpu,
                )
            elif is_audio_as_video(path):
                create_black_video_from_audio(
                    path,
                    overwrite=args.overwrite,
                    use_gpu=args.use_gpu,
                )
        except Exception as e:
            # Print the full path to debug specific file issues
            print(f"⚠️ Error processing file:\n   Path: {path}\n   Error: {e}")

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(worker, p) for p in files]
        for f in as_completed(futures):
            # Calling result() ensures any errors raised in the thread are caught/handled
            try:
                f.result()
            except Exception as e:
                 print(f"⚠️ Thread Error: {e}")

    print("\n🎯 Done creating black videos.")


if __name__ == "__main__":
    main()