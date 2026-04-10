import re
from urllib.parse import urlparse, parse_qs
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi

def extract_video_id(url: str) -> str:
    """Extracts the YouTube Video ID from a standard, shorts, or embed URL."""
    url = url.strip()
    parsed = urlparse(url)
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
    return url

def get_playlist_videos(playlist_url: str):
    """
    Uses yt-dlp to extract all video IDs, titles, and channels from a playlist.
    Returns a tuple: (playlist_title, list_of_video_dicts)
    """
    # Clean the URL to ensure yt-dlp focuses purely on the playlist
    parsed = urlparse(playlist_url)
    qs = parse_qs(parsed.query)
    if 'list' in qs:
        playlist_id = qs['list'][0]
        playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"

    ydl_opts = {
        'extract_flat': 'in_playlist',
        'quiet': True,
        'ignoreerrors': True
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False)
        if not info:
            return "Unknown Playlist", []
            
        playlist_title = info.get('title', 'Unknown_Playlist')
        videos = []
        
        if 'entries' in info:
            for entry in info['entries']:
                if entry and isinstance(entry, dict) and entry.get('id'):
                    videos.append({
                        'id': entry['id'],
                        'title': entry.get('title', 'Unknown Title'),
                        'channel': entry.get('uploader', entry.get('channel', 'Unknown Channel'))
                    })
        return playlist_title, videos

def fetch_transcript(video_id: str, languages=['hi', 'en']):
    """
    Fetches the transcript for a given video ID. 
    Prefers manual transcripts, falls back to auto-generated.
    """
    api = YouTubeTranscriptApi()
    try:
        # Try to find a specific transcript language
        transcript_list = api.list_transcripts(video_id)
        try:
            # First look for manually created transcripts
            transcript_obj = transcript_list.find_transcript(languages)
        except:
            # Fallback to auto-generated transcripts
            transcript_obj = transcript_list.find_generated_transcript(languages)
            
        raw_data = transcript_obj.fetch()
        text_lines = [entry['text'] for entry in raw_data]
        
    except Exception as e:
        # Final fallback method
        try:
            transcript_obj = api.fetch(video_id, languages=languages)
            text_lines = [entry['text'] if isinstance(entry, dict) else entry.text for entry in transcript_obj]
        except Exception as fallback_err:
            print(f"❌ Failed to fetch transcript for {video_id}: {fallback_err}")
            return None

    # Join the individual text blocks into one continuous string
    return " ".join(text_lines)

# ==========================================
# Example Usage
# ==========================================
if __name__ == "__main__":
    url = input("Enter a YouTube Video or Playlist URL: ").strip()
    
    is_playlist = "list=" in url
    
    if is_playlist:
        print("📂 Fetching playlist data...")
        playlist_title, videos = get_playlist_videos(url)
        print(f"Found {len(videos)} videos in '{playlist_title}'.\n")
        
        for vid in videos[:3]: # Limiting to first 3 for the example
            print(f"▶ Downloading transcript for: {vid['title']}")
            transcript = fetch_transcript(vid['id'])
            if transcript:
                print(f"Preview: {transcript[:100]}...\n")
                
    else:
        print("🎥 Fetching single video data...")
        video_id = extract_video_id(url)
        print(f"Video ID: {video_id}")
        
        transcript = fetch_transcript(video_id)
        if transcript:
            print("\nTranscript successfully downloaded!")
            print(f"Preview: {transcript[:200]}...")