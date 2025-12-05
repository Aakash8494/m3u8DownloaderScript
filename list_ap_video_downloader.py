import os
import subprocess
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

VIDEO_NUMBERS = range(1, 20 + 1)
RESOLUTION = "240p"  # only download 240p

BASE_URL_TEMPLATE = (
    "https://video.acharyaprashant.org/mansik-bechaini-karan/mansik-bechaini-karan-video-{vid}/240p.m3u8"
)

# Root folder where everything goes
OUTPUT_ROOT = "output_videos"

# Whether to also create a black-screen version of each final video
MAKE_BLACK_COPY = True

# How many videos to process in parallel
MAX_WORKERS = 2


def parse_url_parts(master_url: str):
    """
    Given a URL like:
      https://.../prem-aur-hawas/prem-aur-hawas-video-1/240p.m3u8

    Returns:
      folder_name = 'prem-aur-hawas'
      video_name  = 'prem-aur-hawas-video-1'
    """
    path = urlparse(master_url).path
    parts = path.strip("/").split("/")

    if len(parts) < 3:
        folder_name = "videos"
        video_name = parts[-2] if len(parts) >= 2 else "video"
    else:
        folder_name = parts[-3]
        video_name = parts[-2]

    return folder_name, video_name


def download_with_ffmpeg(playlist_url: str, mp4_path: str) -> bool:
    """
    Let ffmpeg handle HLS (.m3u8) download and remux to MP4 directly.
    """
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


def process_single_video(vid: int):
    print(f"\n=== VIDEO {vid} ({RESOLUTION}) ===")
    master_url = BASE_URL_TEMPLATE.format(vid=vid)

    # Derive folder + video file name from URL
    folder_name, video_name = parse_url_parts(master_url)

    # Final folder & file paths
    final_folder = os.path.join(OUTPUT_ROOT, folder_name)
    os.makedirs(final_folder, exist_ok=True)

    final_mp4_path = os.path.join(final_folder, f"{video_name}.mp4")

    print("  Master URL:", master_url)
    print("  Folder    :", final_folder)
    print("  File name :", os.path.basename(final_mp4_path))

    # If normal file already exists, just ensure black copy exists too
    if os.path.exists(final_mp4_path):
        print("    File already exists, skipping download.")
        if MAKE_BLACK_COPY:
            make_black_screen_copy(final_mp4_path)
        return

    # master_url is already the 240p playlist
    success = download_with_ffmpeg(master_url, final_mp4_path)

    if success and MAKE_BLACK_COPY:
        make_black_screen_copy(final_mp4_path)


def main():
    os.makedirs(OUTPUT_ROOT, exist_ok=True)

    # Process multiple videos in parallel
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(process_single_video, vid): vid
            for vid in VIDEO_NUMBERS
        }

        for future in as_completed(futures):
            vid = futures[future]
            try:
                future.result()
            except Exception as e:
                print(f"\n❌ Error processing VIDEO {vid}: {e}")

    print("\n🎯 Done! All 240p videos (and black-screen copies) saved under:", OUTPUT_ROOT)


if __name__ == "__main__":
    main()