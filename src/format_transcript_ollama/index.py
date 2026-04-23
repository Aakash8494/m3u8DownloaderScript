import sys
import os
import re
import winsound
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
import ollama

def sanitize_filename(name):
    """Removes illegal characters and trailing spaces so Windows doesn't cry."""
    # Remove bad characters
    safe_name = re.sub(r'[\\/*?:"<>|]', "", name)
    # Strip spaces from start and end
    return safe_name.strip()

def get_video_id(url):
    """Extracts the video ID from the YouTube URL."""
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    return url

def get_video_metadata(video_url):
    """Uses yt-dlp to quickly grab channel name and video title."""
    ydl_opts = {'quiet': True, 'skip_download': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            return info.get('uploader', 'Unknown_Channel'), info.get('title', 'Unknown_Title')
    except Exception as e:
        print(f"Metadata error: {e}")
        return "Unknown_Channel", "Unknown_Title"

def fetch_transcript(video_url):
    """Fetches the transcript from YouTube using the new API method."""
    video_id = get_video_id(video_url)
    try:
        api = YouTubeTranscriptApi()
        transcript_list = api.fetch(video_id)
        
        texts = []
        for chunk in transcript_list:
            if isinstance(chunk, dict):
                texts.append(chunk.get('text', ''))
            else:
                texts.append(getattr(chunk, 'text', ''))
                
        full_text = " ".join(texts)
        full_text = " ".join(full_text.split()) 
        return full_text
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        return None

def chunk_text_by_words(text, word_limit=400):
    """Breaks the text into chunks based on word count."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), word_limit):
        chunk = " ".join(words[i:i + word_limit])
        chunks.append(chunk)
    return chunks

def process_chunk_with_llm(chunk_text, chunk_number, total_chunks, output_filepath, model_name="phi3"):
    """Sends a chunk to Ollama and saves the stream to a file."""
    
    prompt = f"""
    You are an expert content editor. I am giving you a part of a video transcript.
    Your task is to provide a short, appropriate title for this specific text and fix any obvious grammatical errors or missing punctuation.
    
    Format your response EXACTLY like this:
    
    ### [Your Title]
    [The corrected paragraph...]

    Here is the transcript part:
    {chunk_text}
    """

    print(f"\n--- Processing Part {chunk_number} of {total_chunks} ---")
    
    response = ollama.chat(
        model=model_name,
        messages=[{'role': 'user', 'content': prompt}],
        stream=True
    )

    # Open the file in 'append' mode so we don't overwrite previous chunks
    with open(output_filepath, 'a', encoding='utf-8') as f:
        for chunk in response:
            text_piece = chunk['message']['content']
            # Print to terminal
            print(text_piece, end='', flush=True)
            # Save to file
            f.write(text_piece)
        f.write("\n\n") # Add spacing between chunks in the final document
    print("\n")

# --- Run the Script ---
if __name__ == "__main__":
    url = input("Enter YouTube URL: ")
    
    print("\nFetching video details...")
    channel, title = get_video_metadata(url)
    
    safe_channel = sanitize_filename(channel)
    safe_title = sanitize_filename(title)
    
    # Setup our folder structure: Transcripts/Channel Name/
    base_folder = "Transcripts"
    channel_folder = os.path.join(base_folder, safe_channel)
    os.makedirs(channel_folder, exist_ok=True)
    
    raw_transcript_path = os.path.join(channel_folder, f"{safe_title}_raw.txt")
    formatted_transcript_path = os.path.join(channel_folder, f"{safe_title}_formatted.md")
    
    raw_text = ""
    
    # 1. Cache Check: See if we already downloaded it
    if os.path.exists(raw_transcript_path):
        print(f"Transcript found in cache! Loading from:\n{raw_transcript_path}")
        with open(raw_transcript_path, 'r', encoding='utf-8') as f:
            raw_text = f.read()
    else:
        print("Downloading new transcript...")
        raw_text = fetch_transcript(url)
        if raw_text:
            with open(raw_transcript_path, 'w', encoding='utf-8') as f:
                f.write(raw_text)
            print(f"Saved raw transcript to:\n{raw_transcript_path}")
            
    # 2. Process with LLM if we have the text
    if raw_text:
        max_words = 400 
        print(f"\nBreaking text into chunks of {max_words} words...")
        text_chunks = chunk_text_by_words(raw_text, word_limit=max_words)
        total = len(text_chunks)
        print(f"Total chunks created: {total}\n")
        
        # Clear out any old formatted file before we start appending
        if os.path.exists(formatted_transcript_path):
            os.remove(formatted_transcript_path)
        
        for index, chunk in enumerate(text_chunks, start=1):
            process_chunk_with_llm(chunk, index, total, formatted_transcript_path, model_name="phi3")
            
        print(f"\nAll done! Final formatted file saved here:\n{formatted_transcript_path}")
        
        winsound.Beep(1000, 1000) 
        
        # Kill the terminal window cleanly
        os.system("taskkill /F /PID %d" % os.getppid())