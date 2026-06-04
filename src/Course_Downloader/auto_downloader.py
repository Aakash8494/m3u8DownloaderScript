import yt_dlp
import re
import os
import sys
import shutil
import json

def clean_filename(name):
    # Removes characters that Windows/Mac hate in folder names
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()

def process_queue():
    queue_dir = "queue"
    completed_dir = "completed"
    
    # 1. Setup directories automatically if they don't exist
    os.makedirs(queue_dir, exist_ok=True)
    os.makedirs(completed_dir, exist_ok=True)

    # 2. Find ALL JSON files in the queue folder (This handles multiple courses!)
    queue_files = [f for f in os.listdir(queue_dir) if f.endswith('.json')]
    
    if not queue_files:
        print(f"😴 The queue is empty! Drop some JSON files into the '{queue_dir}' folder.")
        sys.exit()

    print(f"📦 Found {len(queue_files)} course(s) in the queue. Starting batch download...\n")

    # 3. Loop through every JSON file found
    for file_name in queue_files:
        file_path = os.path.join(queue_dir, file_name)
        
        # Folder name becomes the JSON file name
        raw_course_name = file_name.replace('.json', '')
        safe_course_name = clean_filename(raw_course_name)
        
        os.makedirs(safe_course_name, exist_ok=True)
        print(f"🚀 Starting Course: {safe_course_name}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                videos = json.load(f)
        except Exception as e:
            print(f"❌ Error reading {file_name}: {e}")
            continue

        # 4. Download Loop
        for index, video in enumerate(videos, start=1):
            title = video.get('title', f"Video_{index}")
            url = video.get('url')
            
            if not url:
                continue

            safe_title = clean_filename(title)
            filename = f"{index:02d} - {safe_title}"
            filepath = os.path.join(safe_course_name, f"{filename}.%(ext)s")
            
            ydl_opts = {
                'outtmpl': filepath,
                'merge_output_format': 'mp4',
                'format': 'bestvideo[height<=360]+bestaudio/worst',
                'quiet': True, 
                'no_warnings': True,
                
                # --- NEW SPEED BOOST OPTIONS ---
                'concurrent_fragment_downloads': 10,  # Downloads 10 chunks at the same time
                'http_chunk_size': 10485760,          # 10MB chunk size for faster I/O
                'retries': 5                          # Quick retry if a connection drops
            }
            
            print(f"   📥 [{index}/{len(videos)}] {filename}...", end="", flush=True)
            
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                print(" ✅")
            except Exception as e:
                print(f" ❌ Failed ({e})")

        # 5. Backup and Cleanup
        # Copy the JSON file into the newly created course folder as a backup
        backup_path = os.path.join(safe_course_name, file_name)
        shutil.copy(file_path, backup_path)
        print(f"📁 Backup saved: '{backup_path}'")

        # Move the original JSON to the completed folder so it doesn't run again
        shutil.move(file_path, os.path.join(completed_dir, file_name))
        print(f"✨ Finished {safe_course_name}! Moved config to '{completed_dir}'.\n")
        print("-" * 50)

    print("🎉 ALL QUEUED COURSES DOWNLOADED SUCCESSFULLY! 🎉")

if __name__ == "__main__":
    process_queue()