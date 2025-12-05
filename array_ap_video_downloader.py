import os
import subprocess
import requests
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

# Root folder where everything goes
OUTPUT_ROOT = "output_videos"

# Resolutions to download for each URL
TARGET_RESOLUTIONS = ["240p"]

# Whether to also create a black-screen version of each final video
MAKE_BLACK_COPY = True

# How many videos to download in parallel
MAX_WORKERS = 2

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})


def parse_url_parts(any_url: str):
    """
    Extracts a folder name and video name based on Acharya Prashant URLs.
    Works for:
      /courses/<date>/<slug>/<resolution>.m3u8
    """
    path = urlparse(any_url).path
    parts = path.strip("/").split("/")

    if "courses" in parts and len(parts) >= 4:
        folder_name = parts[1]   # date, e.g. 2023-12-12
        video_name = parts[2]    # slug, unique identifier
    else:
        folder_name = "videos"
        video_name = parts[-1].split(".")[0]

    return folder_name, video_name


def build_playlist_url(input_url: str, resolution: str) -> str:
    """
    Adjust the URL to target a specific playlist resolution.
    """
    base = input_url.rsplit("/", 1)[0]
    return f"{base}/{resolution}.m3u8"


def download_with_ffmpeg(playlist_url: str, mp4_path: str) -> bool:
    """
    Let ffmpeg handle HLS (.m3u8) download and remux to MP4 directly.
    """
    print(f"    Downloading via ffmpeg → {mp4_path}")
    cmd = [
        "ffmpeg", "-y",
        "-loglevel", "warning",      # less spam, a bit less overhead
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


def make_black_screen_copy(mp4_path: str):
    """
    Create a black-screen version (audio only from original, synthetic black video).
    """
    black_mp4_path = mp4_path.replace(".mp4", "_black.mp4")
    if os.path.exists(black_mp4_path):
        print(f"    Black-screen already exists, skipping: {black_mp4_path}")
        return

    print(f"    Creating black-screen version (fast): {black_mp4_path}")

    cmd_black = [
        "ffmpeg", "-y",
        "-loglevel", "warning",
        "-i", mp4_path,                               # original (we use only audio)
        "-f", "lavfi", "-i", "color=black:s=426x240:r=25",  # synthetic black video
        "-map", "1:v",                                # video from color source
        "-map", "0:a",                                # audio from original
        "-shortest",                                  # stop when audio ends
        "-c:v", "libx264",
        "-c:a", "copy",
        black_mp4_path,
    ]

    try:
        subprocess.run(cmd_black, check=True)
        print(f"    ✔ Created black-screen video: {black_mp4_path}")
    except subprocess.CalledProcessError as e:
        print("    ffmpeg (black-screen) failed:", e)


def process_video_from_url(input_url: str):
    input_url = input_url.strip()
    if not input_url:
        return

    folder_name, video_name = parse_url_parts(input_url)

    final_folder = os.path.join(OUTPUT_ROOT, folder_name)
    os.makedirs(final_folder, exist_ok=True)

    print(f"\n=== VIDEO: {video_name} ===")
    print("  Folder:", final_folder)

    for res in TARGET_RESOLUTIONS:
        print(f"\n  --- Downloading {res} ---")

        playlist_url = build_playlist_url(input_url, res)
        print("  Playlist:", playlist_url)

        output_mp4 = os.path.join(final_folder, f"{video_name}_{res}.mp4")

        # Skip if already downloaded
        if os.path.exists(output_mp4):
            print(f"    File already exists, skipping download: {output_mp4}")
            if MAKE_BLACK_COPY:
                make_black_screen_copy(output_mp4)
            continue

        success = download_with_ffmpeg(playlist_url, output_mp4)

        if success and MAKE_BLACK_COPY:
            make_black_screen_copy(output_mp4)


def main(url_list):
    os.makedirs(OUTPUT_ROOT, exist_ok=True)

    # Run multiple downloads in parallel
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(process_video_from_url, url): url
            for url in url_list
            if url.strip()
        }

        for future in as_completed(futures):
            url = futures[future]
            try:
                future.result()
            except Exception as e:
                print(f"\n❌ Error processing {url}: {e}")


if __name__ == "__main__":
    SAMPLE_URLS = [
        "https://video1.acharyaprashant.org/courses/2022-01-28/nu13-video-1-8cf9016/240p.m3u8",
        "https://video1.acharyaprashant.org/courses/2022-01-28/nu13-video-2-27fb0b3/240p.m3u8",
        "https://video1.acharyaprashant.org/courses/2022-01-28/nu13-video-3-56a8e57/240p.m3u8",
        "https://video1.acharyaprashant.org/courses/2022-01-28/nu13-video-4-86bf1ca/240p.m3u8",
        "https://video1.acharyaprashant.org/courses/2022-01-29/nu13-video-5-cf682fd/240p.m3u8",
    ]

    main(SAMPLE_URLS)
    print("\n🎯 Done! Files saved in:", OUTPUT_ROOT)