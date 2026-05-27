from youtube_transcript_api import YouTubeTranscriptApi
import argparse
import pyperclip
import urllib.request
import json
import os
import re

def get_video_id(url):
    """Extracts the video ID from various YouTube URL formats."""
    if "v=" in url:
        return url.split("v=")[-1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[-1].split("?")[0]
    elif "shorts/" in url:
        return url.split("shorts/")[-1].split("?")[0]
    return url

def sanitize_filename(name):
    """Removes invalid characters so the string can be used as a folder or file name."""
    # Replaces \ / : * ? " < > | with nothing
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()

def get_video_metadata(video_id):
    """Fetches the video title and channel name using YouTube's oEmbed API."""
    clean_url = f"https://www.youtube.com/watch?v={video_id}"
    oembed_url = f"https://www.youtube.com/oembed?url={clean_url}&format=json"
    
    try:
        # We add a user-agent header to prevent YouTube from blocking the request
        req = urllib.request.Request(oembed_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return data.get("title", "Unknown_Title"), data.get("author_name", "Unknown_Channel")
    except Exception as e:
        print(f"⚠️ Could not fetch metadata (Title/Channel): {e}")
        return f"Video_{video_id}", "Unknown_Channel"

def create_url_shortcut(folder_path, safe_title, video_id):
    """Creates a Windows/Mac compatible internet shortcut (.url file)."""
    shortcut_path = os.path.join(folder_path, f"{safe_title}.url")
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    
    with open(shortcut_path, "w", encoding="utf-8") as f:
        f.write("[InternetShortcut]\n")
        f.write(f"URL={video_url}\n")

def download_transcript(video_url, languages):
    video_id = get_video_id(video_url)
    api = YouTubeTranscriptApi()

    print("Fetching video details...")
    title, channel = get_video_metadata(video_id)
    
    safe_title = sanitize_filename(title)
    safe_channel = sanitize_filename(channel)

    # 1. Create the Channel Folder
    os.makedirs(safe_channel, exist_ok=True)

    try:
        print(f"Downloading transcript for: '{title}'...")
        transcript = api.fetch(video_id, languages=languages)

        text = " ".join(
            [t.text if hasattr(t, "text") else t["text"] for t in transcript]
        )

        # 2. Save the Transcript Text File
        transcript_path = os.path.join(safe_channel, f"{safe_title}.txt")
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(text)

        # 3. Create the Browser Shortcut
        create_url_shortcut(safe_channel, safe_title, video_id)

        print(f"✅ Success! Saved to folder: ./{safe_channel}/")
        print(f"📄 Transcript: {safe_title}.txt")
        print(f"🔗 Shortcut: {safe_title}.url")

    except Exception as e:
        print("❌ Error fetching transcript:", e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download YouTube transcript")
    
    parser.add_argument("url", nargs="?", default=None, help="YouTube video URL (leave blank to use clipboard)")
    parser.add_argument(
        "--lang",
        nargs="+",
        default=["en-IN", "en", "hi"],
        help="Preferred languages (space separated). Example: --lang en en-IN hi"
    )

    args = parser.parse_args()
    target_url = args.url

    # Check CLI arguments first, then fallback to clipboard
    if not target_url:
        clipboard_text = pyperclip.paste().strip()
        if "youtube.com" in clipboard_text or "youtu.be" in clipboard_text:
            print(f"📋 Found URL in clipboard: {clipboard_text}")
            target_url = clipboard_text
        else:
            print("❌ Error: No URL provided via command line, and no valid YouTube URL found in clipboard.")
            exit(1)

    download_transcript(target_url, args.lang)