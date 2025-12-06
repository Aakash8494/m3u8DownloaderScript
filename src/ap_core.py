# ap_core.py
import os
import subprocess
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

# ---------- URL + path helpers ----------

def parse_url_parts(any_url: str):
    """
    Works for:
      /courses/<date>/<slug>/<resolution>.m3u8
      /<course-slug>/<video-slug>/240p.m3u8
    Returns: (folder_name, video_name)
    """
    path = urlparse(any_url).path
    parts = path.strip("/").split("/")

    if "courses" in parts and len(parts) >= 4:
        folder_name = parts[1]   # date, e.g. 2022-01-28
        video_name = parts[2]    # slug, e.g. nu13-video-1-xxxxxxx
    elif len(parts) >= 2:
        folder_name = parts[-3] if len(parts) >= 3 else "videos"
        video_name = parts[-2]
    else:
        folder_name = "videos"
        video_name = parts[-1].split(".")[0]

    return folder_name, video_name


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


# ---------- Download 240p from m3u8 ----------

def download_with_ffmpeg(playlist_url: str, mp4_path: str) -> bool:
    """HLS → MP4 via ffmpeg, stream copy."""
    print(f"    Downloading via ffmpeg → {mp4_path}")
    cmd = [
        "ffmpeg", "-y",
        "-loglevel", "warning",
        "-i", playlist_url,
        "-c", "copy",
        mp4_path,
    ]
    try:
        subprocess.run(cmd, check=True)
        print(f"    ✔ Created: {mp4_path}")
        return True
    except subprocess.CalledProcessError as e:
        print("    ffmpeg failed:", e)
        return False


# ---------- Black-screen creation (reusable) ----------

def get_black_output_path(input_path: str) -> str:
    directory, filename = os.path.split(input_path)
    name, ext = os.path.splitext(filename)

    # Output goes into a new "black" subfolder
    black_folder = os.path.join(directory, "black")
    os.makedirs(black_folder, exist_ok=True)

    if name.endswith("_black"):
        return os.path.join(black_folder, filename)

    black_name = f"{name}_black{ext}"
    return os.path.join(black_folder, black_name)


def create_black_video(
    input_path: str,
    overwrite: bool = False,
    use_gpu: bool = False,
) -> None:
    """
    Turn one video into black-screen + original audio.
    Can be called from downloader OR from a standalone CLI.
    """
    output_path = get_black_output_path(input_path)

    if os.path.abspath(input_path) == os.path.abspath(output_path):
        print(f"Skipping (already _black): {input_path}")
        return

    if os.path.exists(output_path) and not overwrite:
        print(f"Black version exists, skipping: {output_path}")
        return

    print(f"\nSource : {input_path}")
    print(f"Black  : {output_path}")

    codec = "libx264"
    preset = "ultrafast"

    if use_gpu:
        # best-effort NVENC check (safe to ignore if fails)
        try:
            subprocess.run(
                ["ffmpeg", "-h", "encoder=h264_nvenc"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )
            codec = "h264_nvenc"
            preset = "fast"
            print("    Using GPU encoder h264_nvenc")
        except Exception:
            print("    h264_nvenc not available, falling back to libx264")

    cmd = [
        "ffmpeg",
        "-y",
        "-loglevel", "error",
        "-i", input_path,
        "-f", "lavfi", "-i", "color=black:s=426x240:r=25",
        "-map", "1:v",
        "-map", "0:a",
        "-shortest",
        "-c:v", codec,
        "-preset", preset,
        "-c:a", "copy",
        output_path,
    ]

    try:
        subprocess.run(cmd, check=True)
        print("  ✔ Black-screen video created")
    except subprocess.CalledProcessError as e:
        print("  ✖ ffmpeg failed:", e)


# ---------- Generic parallel helper ----------

def run_in_parallel(func, items, max_workers: int = 2):
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {ex.submit(func, item): item for item in items}
        for f in as_completed(futures):
            try:
                f.result()
            except Exception as e:
                print(f"❌ Error processing {futures[f]}: {e}")