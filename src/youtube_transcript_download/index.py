from youtube_transcript_api import YouTubeTranscriptApi
import argparse
import pyperclip  # 👈 Imported pyperclip

def get_video_id(url):
    if "v=" in url:
        return url.split("v=")[-1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[-1].split("?")[0]
    return url

def download_transcript(video_url, languages):
    video_id = get_video_id(video_url)
    api = YouTubeTranscriptApi()

    try:
        transcript = api.fetch(video_id, languages=languages)

        text = " ".join(
            [t.text if hasattr(t, "text") else t["text"] for t in transcript]
        )

        with open(f"{video_id}.txt", "w", encoding="utf-8") as f:
            f.write(text)

        print(f"✅ Saved transcript ({languages})")

    except Exception as e:
        print("❌ Error:", e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download YouTube transcript")
    
    # 👈 Made the URL argument optional (nargs="?")
    parser.add_argument("url", nargs="?", default=None, help="YouTube video URL (leave blank to use clipboard)")
    parser.add_argument(
        "--lang",
        nargs="+",
        default=["en-IN", "en", "hi"],
        help="Preferred languages (space separated). Example: --lang en en-IN hi"
    )

    args = parser.parse_args()

    # 👈 New Logic: Check CLI arguments first, then fallback to clipboard
    target_url = args.url

    if not target_url:
        clipboard_text = pyperclip.paste().strip()
        # Basic check to see if the clipboard text looks like a YouTube link
        if "youtube.com" in clipboard_text or "youtu.be" in clipboard_text:
            print(f"📋 Found URL in clipboard: {clipboard_text}")
            target_url = clipboard_text
        else:
            print("❌ Error: No URL provided via command line, and no valid YouTube URL found in clipboard.")
            exit(1)

    download_transcript(target_url, args.lang)