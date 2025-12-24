# black_videos_cli.py
import os
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

from ap_core import (
    create_black_video,
    create_black_video_from_audio,
)

VIDEO_EXTENSIONS = (".mp4", ".mkv", ".mov", ".m4v")
AUDIO_AS_VIDEO_EXTENSIONS = (".opus", ".m4a", ".mp3", ".wav")


def is_video_file(name: str) -> bool:
    return name.lower().endswith(VIDEO_EXTENSIONS)


def is_audio_as_video(name: str) -> bool:
    return name.lower().endswith(AUDIO_AS_VIDEO_EXTENSIONS)


def collect_files(directory: str, recursive: bool):
    tasks = []

    if recursive:
        for root, _, files in os.walk(directory):
            for f in files:
                if (
                    (is_video_file(f) or is_audio_as_video(f))
                    and "_black" not in f
                ):
                    tasks.append(os.path.join(root, f))
    else:
        for f in os.listdir(directory):
            full = os.path.join(directory, f)
            if (
                os.path.isfile(full)
                and (is_video_file(f) or is_audio_as_video(f))
                and "_black" not in f
            ):
                tasks.append(full)

    return tasks


def main():
    parser = argparse.ArgumentParser(
        description="Create black-screen videos from video files and .opus audio files."
    )
    parser.add_argument("directory")
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--use-gpu", action="store_true")

    args = parser.parse_args()
    directory = os.path.abspath(args.directory)

    if not os.path.isdir(directory):
        print("❌ Not a directory:", directory)
        return

    files = collect_files(directory, args.recursive)
    print(f"Found {len(files)} media file(s).")

    def worker(path: str):
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

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(worker, p) for p in files]
        for f in as_completed(futures):
            f.result()

    print("\n🎯 Done creating black videos.")


if __name__ == "__main__":
    main()