import os
import re
import requests
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(value: str) -> str:
    value = value.strip()
    parsed = urlparse(value)

    if parsed.scheme in ("http", "https"):
        if parsed.netloc in ("youtu.be", "www.youtu.be"):
            return parsed.path.lstrip("/")

        qs = parse_qs(parsed.query)
        if "v" in qs:
            return qs["v"][0]

        m = re.search(r"/(shorts|embed)/([^/?&#]+)", parsed.path)
        if m:
            return m.group(2)

        return parsed.path.lstrip("/")

    return value


def clean_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "", name)


def get_title_and_channel(video_page_url: str):
    oembed_url = "https://www.youtube.com/oembed"
    params = {"url": video_page_url, "format": "json"}
    resp = requests.get(oembed_url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    title = data.get("title", "Untitled")
    channel = data.get("author_name", "UnknownChannel")
    return title, channel


def main():
    video_input = input("Enter YouTube URL or ID: ").strip()

    try:
        video_id = extract_video_id(video_input)
        print(f"Using video ID: {video_id}")

        if video_input.startswith("http"):
            page_url = video_input
        else:
            page_url = f"https://www.youtube.com/watch?v={video_id}"

        title, channel = get_title_and_channel(page_url)
        print(f"Fetching transcript for: {title} ({channel})")

        # Clean names for folder/file
        clean_channel = clean_filename(channel)
        clean_title = clean_filename(title)

        # Folder structure: transcripts/channel/title.txt
        base_dir = "transcripts"
        channel_dir = os.path.join(base_dir, clean_channel)
        os.makedirs(channel_dir, exist_ok=True)

        file_path = os.path.join(channel_dir, f"{clean_title}.txt")

        # Fetch transcript (new API)
        api = YouTubeTranscriptApi()
        fetched = api.fetch(video_id)
        data = fetched.to_raw_data()

        text_lines = [
            entry["text"]
            for entry in data
            if entry.get("text", "").strip()
        ]
        text = "\n".join(text_lines)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)

        print(f"✅ Saved transcript: {file_path}")

    except requests.HTTPError as e:
        print(f"❌ HTTP error while fetching metadata: {e}")
    except Exception as e:
        print("❌ Error:", e)


if __name__ == "__main__":
    main()