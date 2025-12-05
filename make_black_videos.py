import os
import subprocess
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

VIDEO_EXTENSIONS = (".mp4", ".mkv", ".mov", ".m4v")


# ---------- Utility checks ----------

def check_binary_exists(name: str) -> bool:
    """Return True if a binary (ffmpeg/ffprobe) is available on PATH."""
    try:
        subprocess.run(
            [name, "-version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def has_audio_stream(path: str, has_ffprobe: bool) -> bool:
    """
    Check if the file has at least one audio stream using ffprobe.
    If ffprobe is not available, assume True (skip this check).
    """
    if not has_ffprobe:
        return True  # Can't check, so don't block processing

    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "a",
        "-show_entries", "stream=index",
        "-of", "csv=p=0",
        path,
    ]
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=True,
        )
        return bool(result.stdout.strip())
    except subprocess.CalledProcessError:
        # ffprobe failed → treat as no audio
        return False


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


# ---------- Core conversion ----------

def create_black_video(
    input_path: str,
    overwrite: bool,
    codec: str,
    fallback_codec: str,
    has_ffprobe: bool,
    dry_run: bool = False,
) -> None:
    output_path = get_black_output_path(input_path)

    if os.path.abspath(input_path) == os.path.abspath(output_path):
        print(f"Skipping (already _black name): {input_path}")
        return

    if os.path.exists(output_path) and not overwrite:
        print(f"Black version exists, skipping: {output_path}")
        return

    if not os.path.isfile(input_path):
        print(f"Not a file, skipping: {input_path}")
        return

    # Ensure file has audio (if ffprobe is available)
    if not has_audio_stream(input_path, has_ffprobe):
        print(f"No audio stream found, skipping: {input_path}")
        return

    print(f"\n🎬 Source : {input_path}")
    print(f"🖤 Output : {output_path}")

    if dry_run:
        print("   (dry run: not converting)")
        return

    def run_ffmpeg(use_codec: str) -> bool:
        cmd = [
            "ffmpeg",
            "-y" if overwrite else "-n",
            "-loglevel", "error",
            "-i", input_path,                        # input: we only use audio
            "-f", "lavfi", "-i", "color=black:s=426x240:r=25",  # synthetic black video
            "-map", "1:v",                           # video from color source
            "-map", "0:a",                           # audio from original
            "-shortest",                             # stop when audio ends
            "-c:v", use_codec,
            "-preset", "ultrafast" if use_codec == "libx264" else "fast",
            "-c:a", "copy",
            output_path,
        ]
        try:
            subprocess.run(cmd, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
        except FileNotFoundError:
            print("⚠️ ffmpeg not found. Please install ffmpeg and ensure it's on PATH.")
            return False

    # First try the chosen codec (e.g. h264_nvenc if GPU)
    if run_ffmpeg(codec):
        print("   ✔ Done")
        return

    # If GPU codec fails, fall back to CPU libx264
    if codec != fallback_codec:
        print(f"   ⚠️ {codec} failed, falling back to {fallback_codec} …")
        if run_ffmpeg(fallback_codec):
            print("   ✔ Done (fallback)")
            return

    print(f"   ✖ FAILED: {input_path}")


# ---------- Directory traversal + parallelism ----------

def collect_video_files(directory: str, recursive: bool) -> list[str]:
    tasks = []

    if recursive:
        for root, _, files in os.walk(directory):
            for fname in files:
                if is_video_file(fname) and "_black" not in fname:
                    tasks.append(os.path.join(root, fname))
    else:
        for fname in os.listdir(directory):
            full_path = os.path.join(directory, fname)
            if os.path.isfile(full_path) and is_video_file(fname) and "_black" not in fname:
                tasks.append(full_path)

    return tasks


def process_directory(
    directory: str,
    overwrite: bool,
    recursive: bool,
    workers: int,
    use_gpu: bool,
    dry_run: bool,
):
    has_ffmpeg = check_binary_exists("ffmpeg")
    has_ffprobe = check_binary_exists("ffprobe")

    if not has_ffmpeg:
        print("❌ ffmpeg is not installed or not on PATH. Aborting.")
        return

    if not has_ffprobe:
        print("⚠️ ffprobe not found. Audio-stream checks will be skipped.")

    # Decide codec
    codec = "libx264"
    fallback_codec = "libx264"

    if use_gpu:
        # Try to see if h264_nvenc seems available (best-effort)
        print("🔎 Checking for h264_nvenc support …")
        test_cmd = ["ffmpeg", "-h", "encoder=h264_nvenc"]
        try:
            subprocess.run(
                test_cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )
            codec = "h264_nvenc"
            fallback_codec = "libx264"
            print("✅ h264_nvenc available. Using GPU for video encoding.")
        except subprocess.CalledProcessError:
            print("⚠️ h264_nvenc not available. Falling back to libx264.")
        except FileNotFoundError:
            # Already handled by has_ffmpeg, but keep safe
            print("⚠️ ffmpeg not found during NVENC check. Using libx264.")

    tasks = collect_video_files(directory, recursive)
    print(f"\n🧾 Total files to convert: {len(tasks)}")

    if not tasks:
        print("No matching video files found. Nothing to do.")
        return

    if dry_run:
        for path in tasks:
            print(f"DRY RUN → would convert: {path}")
        return

    workers = max(1, workers)
    print(f"⚙️ Using {workers} worker(s)")

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(
                create_black_video,
                path,
                overwrite,
                codec,
                fallback_codec,
                has_ffprobe,
                dry_run,
            ): path
            for path in tasks
        }
        for future in as_completed(futures):
            _ = futures[future]
            try:
                future.result()
            except KeyboardInterrupt:
                print("\n🛑 Interrupted by user.")
                raise
            except Exception as e:
                print(f"⚠️ Unexpected error: {e}")


# ---------- CLI ----------

def main():
    parser = argparse.ArgumentParser(
        description="Create black-screen versions (audio only, synthetic black video) for all videos in a directory."
    )
    parser.add_argument(
        "directory",
        help="Directory containing video files",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing _black files if they exist",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Process directories recursively",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Number of videos to process in parallel (default: 4)",
    )
    parser.add_argument(
        "--use-gpu",
        action="store_true",
        help="Try to use h264_nvenc (GPU) for faster encoding, with fallback to libx264",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only list what would be converted, do not run ffmpeg",
    )

    args = parser.parse_args()

    directory = os.path.abspath(args.directory)
    if not os.path.isdir(directory):
        print("Not a directory:", directory)
        return

    print("\n📂 Processing directory:", directory)
    process_directory(
        directory=directory,
        overwrite=args.overwrite,
        recursive=args.recursive,
        workers=args.workers,
        use_gpu=args.use_gpu,
        dry_run=args.dry_run,
    )

    print("\n🎯 Done (or dry run complete).\n")


if __name__ == "__main__":
    main()