from youtube_transcript_api import YouTubeTranscriptApi
import argparse

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
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument(
        "--lang",
        nargs="+",
        default=["en-IN", "en", "hi"],
        help="Preferred languages (space separated). Example: --lang en en-IN hi"
    )

    args = parser.parse_args()

    download_transcript(args.url, args.lang)


    # py index.py https://www.youtube.com/watch?v=j7yjw4D6Pi4 --lang en-IN en hi