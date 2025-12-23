import os
import argparse
from ap_core import (
    parse_url_parts,
    ensure_dir,
    download_with_ffmpeg,
    create_black_video,
    run_in_parallel,
)

OUTPUT_ROOT = "output_videos"

def download_item(item_data, make_black=True, use_gpu=False, folder_override=None):
    """
    item_data is a tuple: (url, custom_name)
    """
    url, custom_name = item_data
    
    # Logic to determine folder and filename
    parsed_folder, parsed_name = parse_url_parts(url)
    
    folder_name = folder_override if folder_override else parsed_folder
    video_name = custom_name if custom_name else parsed_name

    final_folder = os.path.join(OUTPUT_ROOT, folder_name)
    ensure_dir(final_folder)

    mp4_path = os.path.join(final_folder, f"{video_name}.mp4")
    
    print(f"\n--- Processing: {video_name} ---")
    if os.path.exists(mp4_path):
        print(f"    File exists: {mp4_path} (Skipping)")
    else:
        if download_with_ffmpeg(url, mp4_path):
            if make_black:
                create_black_video(mp4_path, overwrite=False, use_gpu=use_gpu)
        else:
            print(f"    Failed to download: {url}")

def main():
    parser = argparse.ArgumentParser(description="AP video downloader (List Mode)")
    
    # Arguments
    parser.add_argument("--url", action="append", help="Format: 'URL' or 'URL|filename'")
    parser.add_argument("--file", help="Text file with one 'URL|filename' per line")
    parser.add_argument("--folder", help="Target subfolder name")
    parser.add_argument("--no-black", action="store_true", help="Skip black video creation")
    parser.add_argument("--use-gpu", action="store_true", help="Use GPU for processing")
    parser.add_argument("--workers", type=int, default=2, help="Parallel workers")

    args = parser.parse_args()

    # Collect raw inputs
    raw_inputs = []
    if args.url:
        raw_inputs.extend(args.url)
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            raw_inputs.extend([line.strip() for line in f if line.strip()])

    if not raw_inputs:
        print("No URLs provided.")
        return

    # Parse URLs and optional custom names
    # Returns list of tuples: [ (url, name), (url, name) ]
    tasks = []
    seen_urls = set()
    for entry in raw_inputs:
        if "|" in entry:
            url, name = entry.split("|", 1)
        else:
            url, name = entry, None
        
        if url not in seen_urls:
            tasks.append((url, name))
            seen_urls.add(url)

    run_in_parallel(
        lambda t: download_item(
            t,
            make_black=not args.no_black,
            use_gpu=args.use_gpu,
            folder_override=args.folder,
        ),
        tasks,
        max_workers=args.workers,
    )

    print(f"\n🎯 Done! Check: {OUTPUT_ROOT}")

if __name__ == "__main__":
    main()