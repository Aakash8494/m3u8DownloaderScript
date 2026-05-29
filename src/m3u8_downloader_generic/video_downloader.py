import yt_dlp
import re

def clean_filename(title):
    # Removes illegal characters so your computer doesn't crash saving the file
    return re.sub(r'[\\/*?:"<>|]', "", title)

def download_m3u8(video_url, video_title):
    # Clean the title just in case you typed any special characters
    safe_title = clean_filename(video_title)
    
    # Configuration options
    ydl_opts = {
        # 1. Use your custom title for the filename
        'outtmpl': f'{safe_title}.mp4', 
        
        # 2. Force 360p resolution. 
        # It looks for 360p first. If it can't find it, it grabs the next best thing under 360p.
        'format': 'best[height<=360]/best', 
    }

    print(f"\nConnecting to the stream for '{safe_title}'...")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        print(f"✅ Download complete! Saved as '{safe_title}.mp4'")
    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    print("--- Video Downloader ---")
    
    # Ask for the URL
    url_input = input("Paste the m3u8 URL: ").strip()
    
    # Ask for the Title
    title_input = input("Type the title for your video (no need to add .mp4): ").strip()
    
    if url_input and title_input:
        download_m3u8(url_input, title_input)
    else:
        print("❌ You must provide both a URL and a title to continue.")