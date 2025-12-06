# downloader.py
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


def build_urls_from_template(template: str, start: int, end: int):
    for vid in range(start, end + 1):
        yield template.format(vid=vid)


def download_one_url(
    url: str,
    make_black: bool = True,
    use_gpu: bool = False,
    folder_override = None,
):
    # folder_name: either from args (list mode) or parsed from URL (template mode)
    if folder_override:
        # only take video_name from URL
        _, video_name = parse_url_parts(url)
        folder_name = folder_override
    else:
        folder_name, video_name = parse_url_parts(url)

    final_folder = os.path.join(OUTPUT_ROOT, folder_name)
    ensure_dir(final_folder)

    mp4_path = os.path.join(final_folder, f"{video_name}.mp4")
    print(f"\n=== VIDEO: {video_name} ===")
    print("  URL   :", url)
    print("  Folder:", final_folder)

    if os.path.exists(mp4_path):
        print("    File exists, skipping download")
    else:
        ok = download_with_ffmpeg(url, mp4_path)
        if not ok:
            return

    if make_black:
        create_black_video(mp4_path, overwrite=False, use_gpu=use_gpu)


def main():
    parser = argparse.ArgumentParser(description="AP video downloader")
    sub = parser.add_subparsers(dest="mode", required=True)

    # Mode 1: template
    p_tpl = sub.add_parser("template", help="Download using a {vid} URL template")
    p_tpl.add_argument("--template", required=True, help="URL template with {vid}")
    p_tpl.add_argument("--start", type=int, required=True)
    p_tpl.add_argument("--end", type=int, required=True)

    # Mode 2: list
    p_list = sub.add_parser("list", help="Download from a list of URLs")
    p_list.add_argument("--url", action="append", help="URL (can be repeated)")
    p_list.add_argument("--file", help="File with one URL per line")
    p_list.add_argument(
        "--folder",
        help="Folder name under OUTPUT_ROOT where all these URLs will be saved",
    )

    # Common options
    parser.add_argument("--no-black", action="store_true", help="Skip black video creation")
    parser.add_argument("--use-gpu", action="store_true", help="Try to use GPU for black video")
    parser.add_argument("--workers", type=int, default=2, help="Parallel downloads (default: 2)")

    args = parser.parse_args()

    make_black = not args.no_black
    use_gpu = args.use_gpu

    # Build list of URLs depending on mode
    urls: list[str] = []

    if args.mode == "template":
        urls = list(build_urls_from_template(args.template, args.start, args.end))
    elif args.mode == "list":
        if args.url:
            urls.extend(args.url)
        if args.file:
            with open(args.file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        urls.append(line)

    if not urls:
        print("No URLs provided.")
        return

    # Remove duplicates while preserving order
    seen = set()
    unique_urls: list[str] = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            unique_urls.append(u)

    folder_override = getattr(args, "folder", None) if args.mode == "list" else None

    # Run in parallel
    run_in_parallel(
        lambda u: download_one_url(
            u,
            make_black=make_black,
            use_gpu=use_gpu,
            folder_override=folder_override,
        ),
        unique_urls,
        max_workers=args.workers,
    )

    print("\n🎯 Done! Files saved in:", OUTPUT_ROOT)


if __name__ == "__main__":
    main()