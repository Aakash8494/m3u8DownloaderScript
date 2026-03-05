import os
import sys

# --- Import Logic for MoviePy v2.0 vs v1.0 ---
try:
    # Try the new MoviePy v2.0 import
    from moviepy import VideoFileClip
except ImportError:
    # Fallback to MoviePy v1.0 import
    try:
        from moviepy.editor import VideoFileClip
    except ImportError:
        print("Error: MoviePy is not installed. Run 'pip install moviepy'")
        sys.exit(1)

def extract_audio_from_videos(folder_path, output_format=".mp3"):
    video_extensions = ('.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv')
    
    # Clean up path (remove quotes if user pasted them from "Copy as path")
    folder_path = folder_path.strip().replace('"', '').replace("'", "")

    if not os.path.exists(folder_path):
        print(f"Error: The folder '{folder_path}' does not exist.")
        return

    output_folder = os.path.join(folder_path, "Audio_Output")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    files_processed = 0

    print(f"Scanning: {folder_path}")
    print("-" * 30)

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(video_extensions):
            video_path = os.path.join(folder_path, filename)
            audio_filename = os.path.splitext(filename)[0] + output_format
            audio_path = os.path.join(output_folder, audio_filename)
            
            print(f"Processing: {filename}...")
            
            try:
                # Load video and export audio
                with VideoFileClip(video_path) as video:
                    if video.audio:
                        # FIX: Removed 'verbose=False' which caused the error in MoviePy 2.0
                        video.audio.write_audiofile(audio_path, logger=None) 
                        print(f" -> Saved: {audio_filename}")
                        files_processed += 1
                    else:
                        print(f" -> Skipped (No audio track)")
            except Exception as e:
                print(f" -> Error: {e}")

    print("-" * 30)
    print(f"Done. {files_processed} files extracted.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_directory = sys.argv[1]
    else:
        print("Usage Tip: You can pass the path directly like: python extract_audio.py 'C:\\Path'")
        target_directory = input("Enter folder path: ")

    extract_audio_from_videos(target_directory)