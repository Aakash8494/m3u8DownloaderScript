import yt_dlp
import re
import os
import sys
import shutil

def clean_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()

def download_course():
    # --- 1. Read the text files ---
    try:
        with open("titles.txt", "r", encoding="utf-8") as f:
            # Read lines and ignore empty ones
            titles = [line.strip() for line in f if line.strip()]
            
        with open("urls.txt", "r", encoding="utf-8") as f:
            urls = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("❌ Error: Make sure 'titles.txt' and 'urls.txt' exist in the same folder.")
        sys.exit()

    # --- 2. Safety Check ---
    if len(titles) == 0 or len(urls) == 0:
        print("❌ Error: Your text files are empty!")
        sys.exit()
        
    if len(titles) != len(urls):
        print(f"❌ Error: Mismatch! Found {len(titles)} titles but {len(urls)} URLs.")
        sys.exit()

    # --- 3. Setup Folder ---
    course_title = input("\n📁 Enter the Course Name (this will be your folder name): ").strip()
    if not course_title:
        course_title = "Downloaded_Course"
        
    safe_course_name = clean_filename(course_title)
    os.makedirs(safe_course_name, exist_ok=True)
    print(f"✅ Folder ready: {safe_course_name}\n")
    
    # --- 4. Start Downloading ---
    for index, (title, url) in enumerate(zip(titles, urls), start=1):
        safe_title = clean_filename(title)
        filename = f"{index:02d} - {safe_title}"
        filepath = os.path.join(safe_course_name, f"{filename}.%(ext)s")
        
        ydl_opts = {
            'outtmpl': filepath,
            'merge_output_format': 'mp4',
            'format': 'bestvideo[height<=360]+bestaudio/worst'
        }
        
        print("-" * 50)
        print(f"📥 [{index}/{len(titles)}] Downloading: {filename}")
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            print(f"✅ Done!")
        except Exception as e:
            print(f"❌ Failed. Error: {e}")

    # --- 5. Backup and Cleanup ---
    print("-" * 50)
    print("🧹 Cleaning up text files...")
    try:
        # Copy the original files into the new course folder
        shutil.copy("titles.txt", os.path.join(safe_course_name, "titles_backup.txt"))
        shutil.copy("urls.txt", os.path.join(safe_course_name, "urls_backup.txt"))
        print("📁 Backup saved inside the course folder.")
        
        # Open the files in 'w' (write) mode without writing anything to instantly empty them
        open("titles.txt", 'w').close()
        open("urls.txt", 'w').close()
        print("✨ Original text files are now empty and ready for the next run!")
        
    except Exception as e:
        print(f"⚠️ Cleanup failed: {e}")

    print("\n🎉 ALL VIDEOS DOWNLOADED SUCCESSFULLY! 🎉")

if __name__ == "__main__":
    download_course()