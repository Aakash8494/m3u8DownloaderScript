import os
import subprocess
import shutil
import requests
from urllib.parse import urljoin, urlparse

VIDEO_NUMBERS = range(4, 10 + 1)
RESOLUTION = "480p"  # only download 480p

BASE_URL_TEMPLATE = "https://video.acharyaprashant.org/love-and-lust/love-and-lust-video-{vid}/playlist.m3u8"

# Root folder where everything goes
OUTPUT_ROOT = "output_videos"

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})


def parse_url_parts(master_url: str):
    """
    Given a URL like:
      https://.../prem-aur-hawas/prem-aur-hawas-video-1/playlist.m3u8

    Returns:
      folder_name = 'prem-aur-hawas'
      video_name  = 'prem-aur-hawas-video-1'
    """
    path = urlparse(master_url).path
    parts = path.strip("/").split("/")

    if len(parts) < 3:
        # Fallback if structure is unexpected
        folder_name = "videos"
        video_name = parts[-2] if len(parts) >= 2 else "video"
    else:
        folder_name = parts[-3]  # prem-aur-hawas
        video_name = parts[-2]   # prem-aur-hawas-video-1

    return folder_name, video_name


def find_480p_playlist(master_url):
    resp = session.get(master_url, timeout=30)
    resp.raise_for_status()

    for line in resp.text.splitlines():
        line = line.strip()
        if line.endswith(f"{RESOLUTION}.m3u8"):
            return urljoin(master_url, line)

    return None


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
            print("    Error downloading segment:", e)


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
        return True
    except subprocess.CalledProcessError as e:
        print("    ffmpeg failed:", e)
        return False


def main():
    os.makedirs(OUTPUT_ROOT, exist_ok=True)

    for vid in VIDEO_NUMBERS:
        print(f"\n=== VIDEO {vid} ({RESOLUTION}) ===")
        master_url = BASE_URL_TEMPLATE.format(vid=vid)

        # Derive folder + video file name from URL
        folder_name, video_name = parse_url_parts(master_url)

        # Final folder & file paths
        final_folder = os.path.join(OUTPUT_ROOT, folder_name)
        os.makedirs(final_folder, exist_ok=True)

        final_mp4_path = os.path.join(final_folder, f"{video_name}.mp4")

        # Temp segments folder
        seg_folder = os.path.join(final_folder, f"{video_name}_segments")

        print("  Master URL: ", master_url)
        print("  Folder    : ", final_folder)
        print("  File name : ", os.path.basename(final_mp4_path))

        playlist = find_480p_playlist(master_url)
        if not playlist:
            print("  480p playlist not found, skipping")
            continue

        print("  480p Playlist:", playlist)
        seg_urls = get_ts_segments(playlist)
        print(f"  {len(seg_urls)} segments")

        download_segments(seg_urls, seg_folder)

        # Merge to mp4
        success = merge_to_mp4(seg_folder, final_mp4_path)

        # Cleanup segments if merge succeeded
        if success:
            print("    Cleaning up segment files…")
            try:
                shutil.rmtree(seg_folder)
                print("    Temp segment folder deleted.")
            except Exception as e:
                print("    Failed to delete segment folder:", e)

    print("\n🎯 Done! All 480p videos saved under:", OUTPUT_ROOT)


if __name__ == "__main__":
    main()