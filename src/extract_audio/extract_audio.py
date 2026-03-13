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
        input("Press Enter to exit...")
        sys.exit(1)

def process_single_video(video_path, root_folder, base_output_folder, output_format=".m4a"):
    """Extracts audio instantly using stream copy and checks for existing files."""
    relative_dir = video_path.relative_to(root_folder).parent
    target_dir = base_output_folder / relative_dir
    target_dir.mkdir(parents=True, exist_ok=True)
    
    audio_filename = video_path.stem + output_format
    audio_path = target_dir / audio_filename

    # --- THE SKIP CHECK ---
    # If file exists AND is larger than 50KB (51200 bytes), assume it's valid and skip
    if audio_path.exists():
        if audio_path.stat().st_size > 51200:
            return f" -> [SKIPPED] Already exists & valid size: {relative_dir / audio_filename}"
        else:
            # If it exists but is tiny, it's probably corrupt. We'll overwrite it.
            print(f" -> [WARNING] Existing file '{audio_filename}' is too small. Overwriting...")

    # --- THE INSTANT EXTRACTION COMMAND ---
    # -c:a copy simply copies the audio stream without re-encoding
    command = [
        "ffmpeg", 
        "-i", str(video_path), 
        "-vn", 
        "-c:a", "copy", 
        "-y", 
        str(audio_path)
    ]

    try:
        process = subprocess.run(
            command, 
            capture_output=True, 
            text=True, 
            encoding="utf-8", 
            errors="replace",
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        if process.returncode == 0:
            return f" -> [SUCCESS] Saved: {relative_dir / audio_filename}"
        else:
            error_msg = process.stderr.strip().split('\n')[-1] if process.stderr else "Unknown error"
            return f" -> [ERROR] FFmpeg failed on {video_path.name}\nDetails: {error_msg}"
            
    except Exception as e:
        return f" -> [ERROR] System failed on {video_path.name}: {e}"

def extract_audio_from_videos(folder_path, output_format=".m4a"):
    """Recursively scans a folder and extracts audio using FFmpeg in parallel."""
    check_ffmpeg()
    
    folder = Path(folder_path.strip("\"'"))
    
    if not folder.exists() or not folder.is_dir():
        print(f"Error: The folder '{folder}' does not exist.")
        input("Press Enter to exit...")
        return

    output_folder = folder / "Audio_Output"

    video_files = [
        file for file in folder.rglob("*") 
        if file.is_file() and file.suffix.lower() in VIDEO_EXTENSIONS
    ]

    if not video_files:
        print("No video files found in the directory or subdirectories.")
        input("Press Enter to exit...")
        return

    print(f"Scanning: {folder}")
    print(f"Found {len(video_files)} video files. Starting instant extraction...")
    print("-" * 50)

    files_processed = 0
    files_skipped = 0
    
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_single_video, video, folder, output_folder, output_format) 
                   for video in video_files]
        
        for future in futures:
            result_message = future.result()
            print(result_message)
            if "[SUCCESS]" in result_message:
                files_processed += 1
            elif "[SKIPPED]" in result_message:
                files_skipped += 1

    print("-" * 50)
    print(f"Done! {files_processed} extracted instantly, {files_skipped} skipped.")
    input("\nPress Enter to close this window...")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_directory = sys.argv[1]
    else:
        target_directory = input("Enter folder path: ")

    extract_audio_from_videos(target_directory)