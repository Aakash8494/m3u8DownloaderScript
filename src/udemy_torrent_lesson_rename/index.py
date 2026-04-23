import os
import re

def sanitize_filename(name):
    """Removes characters that are invalid in file names across different OS."""
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()

def extract_number(filename):
    """Extracts the first sequence of numbers from a string for natural sorting."""
    match = re.search(r'\d+', filename)
    return int(match.group()) if match else 0

# --- CONFIGURATION ---
# Change these paths to match where your files are located
txt_file_path = 'C:\Quick Share\[FreeCoursesOnline.Me] Code With Mosh - The Ultimate Docker Course\Content Table.txt'
video_folder_path = 'C:\Quick Share\[FreeCoursesOnline.Me] Code With Mosh - The Ultimate Docker Course\\video' # Use '.' if the script is in the same folder as the videos

def main():
    # 1. Read titles from the text file
    try:
        with open(txt_file_path, 'r', encoding='utf-8') as f:
            # Read lines, strip trailing spaces/newlines, and ignore completely empty lines
            titles = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: Could not find the text file at '{txt_file_path}'")
        return

    # 2. Get the list of video files and sort them numerically
    try:
        video_files = [f for f in os.listdir(video_folder_path) if f.endswith('.mp4')]
    except FileNotFoundError:
        print(f"Error: Could not find the video folder at '{video_folder_path}'")
        return

    # Sort files so lesson1, lesson2 ... lesson10 are in the correct order
    video_files.sort(key=extract_number)

    # 3. Verify we have the same number of items
    print(f"Found {len(titles)} titles and {len(video_files)} video files.")
    if len(titles) != len(video_files):
        print("Warning: The number of titles and videos do not match!")
        print("The script will only rename up to the smallest count.")
    
    # 4. Process and rename
    print("-" * 30)
    for video_file, title in zip(video_files, titles):
        # Separate the filename from the .mp4 extension
        name_part, ext = os.path.splitext(video_file)
        
        # Clean the text file line so it's safe to use as a filename
        clean_title = sanitize_filename(title)
        
        # Create the new filename (e.g., "lesson66 - 11- Publishing Changes.mp4")
        new_name = f"{name_part} - {clean_title}{ext}"
        
        old_path = os.path.join(video_folder_path, video_file)
        new_path = os.path.join(video_folder_path, new_name)
        
        # Rename the file
        try:
            os.rename(old_path, new_path)
            print(f"Success: '{video_file}' -> '{new_name}'")
        except Exception as e:
            print(f"Error renaming '{video_file}': {e}")

if __name__ == "__main__":
    main()