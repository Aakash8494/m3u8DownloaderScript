import re
import requests
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound


def extract_video_id(value: str) -> str:
    value = value.strip()
    parsed = urlparse(value)

    # If it's a full URL
    if parsed.scheme in ("http", "https"):
        # youtu.be short links
        if parsed.netloc in ("youtu.be", "www.youtu.be"):
            return parsed.path.lstrip("/")

        # ?v=VIDEO_ID
        qs = parse_qs(parsed.query)
        if "v" in qs:
            return qs["v"][0]

        # /shorts/VIDEO_ID or /embed/VIDEO_ID
        m = re.search(r"/(shorts|embed)/([^/?&#]+)", parsed.path)
        if m:
            return m.group(2)

        return parsed.path.lstrip("/")

    # Not a URL → treat as ID
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

        # Build page URL for oEmbed
        if video_input.startswith("http"):
            page_url = video_input
        else:
            page_url = f"https://www.youtube.com/watch?v={video_id}"

        title, channel = get_title_and_channel(page_url)
        file_name = f"{clean_filename(channel)} - {clean_filename(title)}.txt"

        print(f"Fetching transcript for: {title} ({channel})")

        # ✅ This should now exist on the class
        transcript = YouTubeTranscriptApi.get_transcript(video_id)

        text_lines = [entry["text"] for entry in transcript if entry["text"].strip()]
        text = "\n".join(text_lines)

        with open(file_name, "w", encoding="utf-8") as f:
            f.write(text)

        print(f"✅ Saved transcript as: {file_name}")

    except NoTranscriptFound:
        print("❌ No transcript found for this video.")
    except TranscriptsDisabled:
        print("❌ Transcripts are disabled for this video.")
    except requests.HTTPError as e:
        print(f"❌ HTTP error while fetching metadata: {e}")
    except Exception as e:
        print("❌ Error:", e)


if __name__ == "__main__":
    main()