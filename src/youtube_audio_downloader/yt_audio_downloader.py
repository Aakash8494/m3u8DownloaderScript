import time
import yt_dlp

def download_audio_batch(url, batch_size=20, cooldown_seconds=30):
    """
    Analyzes a YouTube URL (Single, Playlist, or Channel), extracts all video links,
    and downloads them as MP3s in safe batches to prevent IP bans.
    """
    print(f"🔍 Analyzing URL: {url}...")
    
    # Options just to extract the metadata/list of videos quickly
    ydl_opts_extract = {
        'extract_flat': 'in_playlist',
        'quiet': True,
        'ignoreerrors': True
    }
    
    with yt_dlp.YoutubeDL(ydl_opts_extract) as ydl:
        info = ydl.extract_info(url, download=False)
        
    if not info:
        print("❌ Could not extract information. Check the URL or your internet connection.")
        return

    # Determine if it's a list (playlist/channel) or a single video
    videos = []
    if 'entries' in info:
        for entry in info['entries']:
            if entry:
                # Flat extraction usually provides 'url', fallback to 'id' if needed
                if entry.get('url'):
                    videos.append(entry['url'])
                elif entry.get('id'):
                    videos.append(f"https://www.youtube.com/watch?v={entry['id']}")
        
        title = info.get('title', 'Unknown Playlist/Channel')
        print(f"📁 Found {len(videos)} videos in '{title}'.")
    else:
        videos.append(info.get('original_url', url))
        print("🎬 Single video detected.")

    if not videos:
        print("❌ No valid videos found to download.")
        return

    # Download options for high-quality MP3 extraction
    ydl_opts_download = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        # Organizes files into folders: Downloads -> Channel Name -> Video Title.mp3
        'outtmpl': 'Downloads/%(uploader)s/%(title)s.%(ext)s',
        'ignoreerrors': True, # Skip unavailable/private videos without crashing
        'quiet': False,       # Show download progress
        'no_warnings': True,
    }

    # Process videos in chunks defined by batch_size
    for i in range(0, len(videos), batch_size):
        chunk = videos[i:i + batch_size]
        current_batch = (i // batch_size) + 1
        total_batches = (len(videos) + batch_size - 1) // batch_size
        
        print(f"\n🚀 Starting Batch {current_batch} of {total_batches} (Videos {i + 1} to {min(i + batch_size, len(videos))})...")
        
        with yt_dlp.YoutubeDL(ydl_opts_download) as ydl:
            for video_url in chunk:
                try:
                    ydl.download([video_url])
                except Exception as e:
                    print(f"⚠️ Error downloading {video_url}: {e}")
        
        # Trigger cooldown if there are more videos left to process
        if i + batch_size < len(videos):
            print(f"\n⏸️ Batch {current_batch} complete. Sleeping for {cooldown_seconds} seconds to dodge rate limits...")
            time.sleep(cooldown_seconds)
            
    print("\n✅ All downloads completed successfully!")

if __name__ == "__main__":
    print("=" * 50)
    print("🎵 YouTube to MP3 Batch Downloader 🎵")
    print("=" * 50)
    target_url = input("Paste a YouTube Video, Playlist, or Channel URL: ").strip()
    
    if target_url:
        # You can adjust the batch size and cooldown time here
        download_audio_batch(target_url, batch_size=20, cooldown_seconds=30)
    else:
        print("❌ No URL provided. Exiting.")