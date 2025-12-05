import os
import subprocess
import argparse

VIDEO_EXTENSIONS = (".mp4", ".mkv", ".mov", ".m4v")


def is_video_file(filename: str) -> bool:
    return filename.lower().endswith(VIDEO_EXTENSIONS)


def get_black_output_path(input_path: str) -> str:
    """
    For 'video.mp4' → 'video_black.mp4'
    For 'something_black.mp4' we still keep it 'something_black.mp4' (idempotent).
    """
    directory, filename = os.path.split(input_path)
    name, ext = os.path.splitext(filename)

    if name.endswith("_black"):
        # Already a black version, don't rename further
        return input_path

    black_name = f"{name}_black{ext}"
    return os.path.join(directory, black_name)


def create_black_video(input_path: str, overwrite: bool = False) -> None:
    output_path = get_black_output_path(input_path)

    if os.path.abspath(input_path) == os.path.abspath(output_path):
        print(f"Skipping (already _black): {input_path}")
        return

    if os.path.exists(output_path) and not overwrite:
        print(f"Black version already exists, skipping: {output_path}")
        return

    print(f"\nSource video : {input_path}")
    print(f"Black output : {output_path}")

    # ⚡ Faster: use only audio from input, create synthetic black video
    cmd = [
        "ffmpeg",
        "-y" if overwrite else "-n",
        "-i", input_path,                       # input: we only use audio
        "-f", "lavfi", "-i", "color=black:s=426x240:r=25",  # synthetic black video
        "-map", "1:v",                          # video from color source
        "-map", "0:a",                          # audio from original
        "-shortest",                            # stop when audio ends
        "-c:v", "libx264",
        "-c:a", "copy",
        output_path,
    ]

    try:
        subprocess.run(cmd, check=True)
        print("  ✔ Black-screen video created")
    except subprocess.CalledProcessError as e:
        print("  ✖ ffmpeg failed:", e)


def process_directory(directory: str, overwrite: bool = False, recursive: bool = False) -> None:
    if recursive:
        for root, _, files in os.walk(directory):
            for fname in files:
                if is_video_file(fname):
                    full_path = os.path.join(root, fname)
                    # Don't process already-black files again
                    if fname.endswith("_black.mp4") or fname.endswith("_black.mkv") or fname.endswith("_black.mov") or fname.endswith("_black.m4v"):
                        continue
                    create_black_video(full_path, overwrite=overwrite)
    else:
        for fname in os.listdir(directory):
            full_path = os.path.join(directory, fname)
            if os.path.isfile(full_path) and is_video_file(fname):
                if fname.endswith("_black.mp4") or fname.endswith("_black.mkv") or fname.endswith("_black.mov") or fname.endswith("_black.m4v"):
                    continue
                create_black_video(full_path, overwrite=overwrite)


def main():
    parser = argparse.ArgumentParser(
        description="Create black-screen versions (audio only, black video) for all videos in a directory."
    )
    parser.add_argument(
        "directory",
        help="Directory containing video files"
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing _black files if they exist"
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Process directories recursively"
    )

    args = parser.parse_args()

    directory = os.path.abspath(args.directory)
    if not os.path.isdir(directory):
        print("Not a directory:", directory)
        return

    print("Processing directory:", directory)
    process_directory(directory, overwrite=args.overwrite, recursive=args.recursive)


if __name__ == "__main__":
    main()