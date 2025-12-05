import os
import subprocess
import shutil
import requests
from urllib.parse import urljoin, urlparse

# Root folder where everything goes
OUTPUT_ROOT = "output_videos"

# Resolutions to download for each URL
# TARGET_RESOLUTIONS = ["240p", "480p"]
TARGET_RESOLUTIONS = ["240p"]

# Whether to also create a black-screen version of each final video
MAKE_BLACK_COPY = True

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


def build_playlist_url(input_url: str, resolution: str):
    """
    Adjust the URL to target a specific playlist resolution.
    """
    base = input_url.rsplit("/", 1)[0]
    return f"{base}/{resolution}.m3u8"


def get_ts_segments(pl_url):
    resp = session.get(pl_url, timeout=30)
    resp.raise_for_status()

    segments = []
    for line in resp.text.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            segments.append(urljoin(pl_url, line))
    return segments


def download_segments(seg_urls, folder):
    os.makedirs(folder, exist_ok=True)
    total = len(seg_urls)

    for i, url in enumerate(seg_urls, start=1):
        filename = os.path.join(folder, f"{i:04d}.ts")

        if os.path.exists(filename):
            print(f"    {i}/{total} exists")
            continue

        try:
            r = session.get(url, timeout=60, stream=True)
            r.raise_for_status()
            with open(filename, "wb") as f:
                for chunk in r.iter_content(1024 * 8):
                    if chunk:
                        f.write(chunk)
            print(f"    Downloaded {i}/{total}")

        except Exception as e:
            print(f"    Error downloading segment {i}: {e}")


def make_black_screen_copy(mp4_path: str):
    """
    Create a black-screen version (audio only from original, synthetic black video).
    """
    black_mp4_path = mp4_path.replace(".mp4", "_black.mp4")
    print(f"    Creating black-screen version (fast): {black_mp4_path}")

    cmd_black = [
        "ffmpeg", "-y",
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


def merge_to_mp4(folder, mp4_path):
    print("    Merging…")

    ts_files = sorted(f for f in os.listdir(folder) if f.endswith(".ts"))
    if not ts_files:
        print("    No segments found")
        return False

    list_file = os.path.join(folder, "list.txt")
    with open(list_file, "w") as lf:
        for ts in ts_files:
            lf.write(f"file '{os.path.abspath(os.path.join(folder, ts))}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", list_file,
        "-c", "copy",
        mp4_path
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"    ✔ Created: {mp4_path}")
        success = True
    except subprocess.CalledProcessError as e:
        print("    ffmpeg failed:", e)
        success = False

    # Optionally create a black-screen copy
    if success and MAKE_BLACK_COPY:
        make_black_screen_copy(mp4_path)

    return success


def process_video_from_url(input_url: str):
    folder_name, video_name = parse_url_parts(input_url)

    final_folder = os.path.join(OUTPUT_ROOT, folder_name)
    os.makedirs(final_folder, exist_ok=True)

    print(f"\n=== VIDEO: {video_name} ===")
    print("  Folder:", final_folder)

    for res in TARGET_RESOLUTIONS:
        print(f"\n  --- Downloading {res} ---")

        playlist_url = build_playlist_url(input_url, res)
        print("  Playlist:", playlist_url)

        try:
            seg_urls = get_ts_segments(playlist_url)
            print(f"  {len(seg_urls)} segments")
        except Exception as e:
            print(f"  Failed to fetch {res}: {e}")
            continue

        seg_folder = os.path.join(final_folder, f"{video_name}_{res}_segments")
        output_mp4 = os.path.join(final_folder, f"{video_name}_{res}.mp4")

        download_segments(seg_urls, seg_folder)

        if merge_to_mp4(seg_folder, output_mp4):
            shutil.rmtree(seg_folder, ignore_errors=True)
            print("    Temp files deleted ✔")


def main(url_list):
    os.makedirs(OUTPUT_ROOT, exist_ok=True)
    for url in url_list:
        url = url.strip()
        if url:
            process_video_from_url(url)


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