import os
import re
import requests
import shutil
import tkinter as tk  # <-- Built-in Windows library to read the clipboard
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

def get_clipboard_text():
    """Silently grabs whatever text is currently copied to your clipboard."""
    root = tk.Tk()
    root.withdraw() # Hides the little empty window
    try:
        text = root.clipboard_get()
    except tk.TclError:
        text = ""
    root.destroy()
    return text

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
    # 1. Instantly grab the copied URL
    video_input = get_clipboard_text().strip()

    # Quick check to make sure you actually copied a YouTube link
    if "youtube.com" not in video_input and "youtu.be" not in video_input:
        print("❌ Error: No YouTube URL found in your clipboard.")
        print(f"What we found instead: '{video_input[:50]}...'")
        input("\nPlease copy a YouTube link and try again. Press Enter to exit...")
        return

    print(f"📋 Read from clipboard: {video_input}\n")

    try:
        video_id = extract_video_id(video_input)
        page_url = f"https://www.youtube.com/watch?v={video_id}"

        print("Fetching video metadata...")
        title, channel = get_title_and_channel(page_url)
        print(f"Found: {title} ({channel})")

        clean_channel = clean_filename(channel)
        clean_title = clean_filename(title)

        base_dir = "transcripts"
        channel_dir = os.path.join(base_dir, clean_channel)
        os.makedirs(channel_dir, exist_ok=True)

        txt_file_path = os.path.join(channel_dir, f"{clean_title}.txt")
        doc_file_path = os.path.join(channel_dir, f"{clean_title}.docx")

        print("Downloading transcript...")
        api = YouTubeTranscriptApi()
        transcript_obj = api.fetch(video_id, languages=['hi', 'en'])

        text_lines = []
        if hasattr(transcript_obj, 'to_raw_data'):
            raw_data = transcript_obj.to_raw_data()
            text_lines = [entry['text'] for entry in raw_data]
        else:
            for entry in transcript_obj:
                if hasattr(entry, 'text'):
                    text_lines.append(entry.text)
                elif isinstance(entry, dict):
                    text_lines.append(entry.get('text'))

        video_link = f"https://www.youtube.com/watch?v={video_id}"
        header = (
            f"Title:   {title}\n"
            f"Channel: {channel}\n"
            f"Link:    {video_link}\n"
            f"{'-' * 50}\n\n"
        )
        
        final_text = header + "\n".join(text_lines)

        with open(txt_file_path, "w", encoding="utf-8") as f:
            f.write(final_text)
        print(f"✅ Saved transcript: {txt_file_path}")

        template_name = "Template.docx"
        if os.path.exists(template_name):
            shutil.copy(template_name, doc_file_path)
            print(f"✅ Created Word doc:  {doc_file_path}")
        else:
            print(f"⚠️ Warning: '{template_name}' not found. Word doc not created.")

    except NoTranscriptFound:
        print("❌ Error: No transcript found in Hindi or English.")
    except TranscriptsDisabled:
        print("❌ Error: Transcripts are disabled for this video.")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Keep window open so you can see it succeeded
    input("\nPress Enter to close this window...")

if __name__ == "__main__":
    import os
    import sys
    import traceback

    # 1. Force Python to use the exact folder where this script is located
    # This guarantees it finds Template.docx and saves transcripts in the right place.
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # 2. Wrap the whole thing in a try/except so the window NEVER force-closes on a crash
    try:
        main()
    except Exception as e:
        print("\n" + "="*50)
        print("❌ A FATAL ERROR OCCURRED:")
        print("="*50)
        traceback.print_exc()
        print("="*50)
        input("\nPress Enter to close this window...")
