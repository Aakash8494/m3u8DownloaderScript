import os
import subprocess
import requests
from urllib.parse import urljoin

VIDEO_NUMBERS = range(1, 10 + 1)
RESOLUTION = "480p"  # only download 480p

BASE_URL_TEMPLATE = "https://video.acharyaprashant.org/prem-aur-hawas/prem-aur-hawas-video-{vid}/playlist.m3u8"
OUTPUT_DIR = f"output_videos/{RESOLUTION}"

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})

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
        if line and not line.startswith("#"):
            segments.append(urljoin(pl_url, line))
    return segments

def download_segments(seg_urls, folder):
    os.makedirs(folder, exist_ok=True)

    for i, url in enumerate(seg_urls, start=1):
        filename = os.path.join(folder, f"{i:04d}.ts")
        if os.path.exists(filename):
            print(f"    {i}/{len(seg_urls)} exists")
            continue

        try:
            r = session.get(url, timeout=60, stream=True)
            r.raise_for_status()
            with open(filename, "wb") as f:
                for chunk in r.iter_content(1024 * 8):
                    if chunk:
                        f.write(chunk)
            print(f"    Downloaded {i}/{len(seg_urls)}")
        except Exception as e:
            print("    Error:", e)

def merge_to_mp4(folder, mp4_path):
    print("    Merging…")
    ts_files = sorted(f for f in os.listdir(folder) if f.endswith(".ts"))
    if not ts_files:
        print("    No segments found")
        return

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
    subprocess.run(cmd, check=True)
    print(f"    ✔ Created: {mp4_path}")

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for vid in VIDEO_NUMBERS:
        print(f"\n=== VIDEO {vid} ({RESOLUTION}) ===")
        master_url = BASE_URL_TEMPLATE.format(vid=vid)

        playlist = find_480p_playlist(master_url)
        if not playlist:
            print("  480p playlist not found, skipping")
            continue

        print("  480p Playlist:", playlist)
        seg_urls = get_ts_segments(playlist)
        print(f"  {len(seg_urls)} segments")

        seg_folder = os.path.join(OUTPUT_DIR, f"video_{vid}_segments")
        download_segments(seg_urls, seg_folder)

        output_mp4 = os.path.join(OUTPUT_DIR, f"video_{vid}.mp4")
        merge_to_mp4(seg_folder, output_mp4)

    print("\n🎯 Done! All 480p videos saved in:", OUTPUT_DIR)

if __name__ == "__main__":
    main()