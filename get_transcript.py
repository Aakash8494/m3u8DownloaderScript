import os
import re
import requests
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

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
    # Remove invalid characters and STRIP whitespace
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()

def get_title_and_channel(video_page_url: str):
    oembed_url = "https://www.youtube.com/oembed"
    params = {"url": video_page_url, "format": "json"}
    try:
        resp = requests.get(oembed_url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("title", "Untitled"), data.get("author_name", "UnknownChannel")
    except:
        return "Unknown_Video", "Unknown_Channel"

def main():
    video_input = input("Enter YouTube URL or ID: ").strip()

    try:
        video_id = extract_video_id(video_input)
        print(f"Using video ID: {video_id}")

        if video_input.startswith("http"):
            page_url = video_input
        else:
            page_url = f"https://www.youtube.com/watch?v={video_id}"

        print("Fetching video metadata...")
        title, channel = get_title_and_channel(page_url)
        print(f"Found: {title} ({channel})")

        clean_channel = clean_filename(channel)
        clean_title = clean_filename(title)

        base_dir = "transcripts"
        channel_dir = os.path.join(base_dir, clean_channel)
        os.makedirs(channel_dir, exist_ok=True)

        file_path = os.path.join(channel_dir, f"{clean_title}.txt")

        print("Downloading transcript...")

        # --- NEW API LOGIC (v1.2+) ---
        api = YouTubeTranscriptApi()

        transcript_obj = api.fetch(video_id, languages=['hi', 'en'])

        text_lines = []
        
        # Check if we can convert to raw data (list of dicts)
        if hasattr(transcript_obj, 'to_raw_data'):
            raw_data = transcript_obj.to_raw_data()
            text_lines = [entry['text'] for entry in raw_data]
        else:
            # Fallback: iterate directly
            for entry in transcript_obj:
                if hasattr(entry, 'text'):
                    text_lines.append(entry.text)
                elif isinstance(entry, dict):
                    text_lines.append(entry.get('text'))
        
        # --- NEW METADATA HEADER ---
        video_link = f"https://www.youtube.com/watch?v={video_id}"
        header = (
            f"Title:   {title}\n"
            f"Channel: {channel}\n"
            f"Link:    {video_link}\n"
            f"{'-' * 50}\n\n"
        )
        
        # Combine header with the joined transcript lines
        final_text = header + "\n".join(text_lines)
        # -----------------------------

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(final_text)

        print(f"✅ Saved transcript: {file_path}")

    except NoTranscriptFound:
        print("❌ Error: No transcript found in Hindi or English.")
    except TranscriptsDisabled:
        print("❌ Error: Transcripts are disabled for this video.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()