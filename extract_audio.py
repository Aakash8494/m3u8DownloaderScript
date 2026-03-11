import sys
import subprocess
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# Supported video formats
VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv'}

def check_ffmpeg():
    """Checks if FFmpeg is installed and accessible."""
    if shutil.which("ffmpeg") is None:
        print("Error: FFmpeg is not installed or not in your system PATH.")
        print("Please install FFmpeg to use this lightning-fast extraction method.")
        sys.exit(1)

def process_single_video(video_path, output_folder, output_format=".mp3"):
    """Extracts audio using direct FFmpeg commands."""
    audio_filename = video_path.stem + output_format
    audio_path = output_folder / audio_filename

    # The FFmpeg command for fast, high-quality MP3 extraction
    command = [
        "ffmpeg", 
        "-i", str(video_path), 
        "-vn", 
        "-y", 
        "-q:a", "2", 
        str(audio_path)
    ]

    try:
        # FIX: Added encoding="utf-8" and errors="replace" so Python doesn't crash 
        # when reading Hindi characters or weird symbols from FFmpeg's output log.
        process = subprocess.run(
            command, 
            capture_output=True, 
            text=True, 
            encoding="utf-8", 
            errors="replace" 
        )
        
        if process.returncode == 0:
            return f" -> [SUCCESS] Saved: {audio_filename}"
        else:
            return f" -> [ERROR] FFmpeg failed on {video_path.name}\nDetails: {process.stderr.strip().split()[-1]}"
            
    except Exception as e:
        return f" -> [ERROR] System failed on {video_path.name}: {e}"

def extract_audio_from_videos(folder_path, output_format=".mp3"):
    """Scans a folder and extracts audio using FFmpeg in parallel."""
    check_ffmpeg()
    
    folder = Path(folder_path.strip("\"'"))
    
    if not folder.exists() or not folder.is_dir():
        print(f"Error: The folder '{folder}' does not exist.")
        return

    output_folder = folder / "Audio_Output"
    output_folder.mkdir(exist_ok=True)

    video_files = [
        file for file in folder.iterdir() 
        if file.is_file() and file.suffix.lower() in VIDEO_EXTENSIONS
    ]

    if not video_files:
        print("No video files found in the directory.")
        return

    print(f"Scanning: {folder}")
    print(f"Found {len(video_files)} video files. Starting ultra-fast extraction...")
    print("-" * 50)

    files_processed = 0
    
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_single_video, video, output_folder, output_format) 
                   for video in video_files]
        
        for future in futures:
            result_message = future.result()
            print(result_message)
            if "[SUCCESS]" in result_message:
                files_processed += 1

    print("-" * 50)
    print(f"Done! {files_processed} audio files extracted to '{output_folder.name}'.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_directory = sys.argv[1]
    else:
        print("Usage Tip: You can pass the path directly like: python script.py \"C:\\Path\"")
        target_directory = input("Enter folder path: ")

    extract_audio_from_videos(target_directory)