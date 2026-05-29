import yt_dlp
import re
import os

def clean_filename(name):
    # Removes illegal characters to prevent saving errors
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()

def download_course():
    # --- 1. Set your Course Title here ---
    course_title = "Rich Dad Poor Dad"
    
    # --- 2. Your Extracted Data ---
    titles = [
        "Introduction",
        "Chapter One- Lesson 1- The Rich Don’t Work for Money",
        "Chapter Two- Lesson 2- Why Teach Financial Literacy-",
        "Chapter Three- Lesson 3- Mind Your Own Business",
        "Chapter Four- Lesson 4- The History of Taxes and the Power of Corporations",
        "Chapter Five- Lesson 5- The Rich Invent Money",
        "Chapter Six- Lesson 6- Work to Learn—Don’t Work for Money",
        "Chapter Seven- Overcoming Obstacles",
        "Chapter Eight- Getting Started",
        "Chapter Nine- Still Want More- Here Are Some To Do’s"
    ]
    
    urls = [
        "https://video.gumlet.io/6834eb307853948a94254415/68ae620619535c52ef3fbf16/main.m3u8",
        "https://video.gumlet.io/6834eb307853948a94254415/68ae6202cd4a3cfd541f9f29/main.m3u8",
        "https://video.gumlet.io/6834eb307853948a94254415/68ae620219535c52ef3fbec4/main.m3u8",
        "https://video.gumlet.io/6834eb307853948a94254415/68ae620319535c52ef3fbed4/main.m3u8",
        "https://video.gumlet.io/6834eb307853948a94254415/68ae6203cd4a3cfd541f9f36/main.m3u8",
        "https://video.gumlet.io/6834eb307853948a94254415/68ae62040a8c57042dcc869e/main.m3u8",
        "https://video.gumlet.io/6834eb307853948a94254415/68ae62040a8c57042dcc86b2/main.m3u8",
        "https://video.gumlet.io/6834eb307853948a94254415/68ae620519535c52ef3fbee4/main.m3u8",
        "https://video.gumlet.io/6834eb307853948a94254415/68ae620519535c52ef3fbef1/main.m3u8",
        "https://video.gumlet.io/6834eb307853948a94254415/68ae620619535c52ef3fbf09/main.m3u8"
    ]
    
    # --- Safety Check ---
    if len(titles) != len(urls):
        print("❌ Error: The number of titles doesn't match the number of URLs.")
        return

    # --- 3. Create the Main Folder ---
    safe_course_name = clean_filename(course_title)
    os.makedirs(safe_course_name, exist_ok=True)
    print(f"\n📁 Created/Found folder: {safe_course_name}\n")
    
    # --- 4. Loop through the lists and download ---
    for index, (title, url) in enumerate(zip(titles, urls), start=1):
        safe_title = clean_filename(title)
        
        # Format the filename with a leading zero (e.g., 01 - Title)
        filename = f"{index:02d} - {safe_title}"
        filepath = os.path.join(safe_course_name, f"{filename}.%(ext)s")
        
        ydl_opts = {
            'outtmpl': filepath,
            'merge_output_format': 'mp4',
            # Force 360p video + best audio. If 360p fails, grab the worst/lowest quality to prevent crashing.
            'format': 'bestvideo[height<=360]+bestaudio/worst'
        }
        
        print("-" * 50)
        print(f"📥 [{index}/{len(titles)}] Starting: {filename} (Targeting 360p)")
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            print(f"✅ Success!")
        except Exception as e:
            print(f"❌ Failed to download {filename}. Error: {e}")

    print("\n🎉 ALL DOWNLOADS COMPLETE! 🎉")

if __name__ == "__main__":
    download_course()