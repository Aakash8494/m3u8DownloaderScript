import os
import requests
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
# Replace this with the actual path to your "output_videos" folder
LOCAL_DIRECTORY = "/Users/aakashjadhav/Documents/GitHub/m3u8DownloaderScript/src/output_videos"
URL = "https://acharyaprashant.org/en/video-modules/campaign/cc-zx34ev"

def get_local_folders(path):
    """Returns a set of cleaned folder names from your computer."""
    if not os.path.exists(path):
        print(f"Error: The path {path} does not exist.")
        return set()
    
    folders = os.listdir(path)
    cleaned_names = []
    for f in folders:
        # We remove the prefix "वीडियो श्रृंखला/ " so it matches the website titles
        # and strip any leading/trailing whitespace
        name = f.replace("वीडियो श्रृंखला/", "").strip()
        name = f.replace("Video Series/", "").strip()
        cleaned_names.append(name)
    return set(cleaned_names)

def get_website_courses(url):
    """Scrapes titles using the exact class string provided."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        
        # 1. CRITICAL: Fix the encoding so Hindi characters display correctly
        response.encoding = 'utf-8' 
        
        soup = BeautifulSoup(response.text, 'html.parser')
        course_titles = []
        
        # 2. Use the exact classes found in your inspector
        # Note: 'false' at the end is likely a dynamic Svelte class, 
        # so we search for the core styling classes.
        target_classes = ["font-normal", "font-hi", "text-[#2E2F31]"]
        
        # Find all spans that contain THESE classes
        spans = soup.find_all('span', class_=lambda x: x and all(c in x for c in target_classes))
        
        for span in spans:
            title = span.get_text().strip()
            # Clean up: Ignore navigation or very short text
            if title and title not in ["Video Series", "FAQs"] and len(title) > 1:
                course_titles.append(title)
        
        # Remove duplicates while preserving order
        unique_titles = list(dict.fromkeys(course_titles))
        return set(unique_titles)

    except Exception as e:
        print(f"Error fetching website: {e}")
        return set()
    
    
def main():
    print("--- Checking for missing courses ---")
    
    local_set = get_local_folders(LOCAL_DIRECTORY)
    web_set = get_website_courses(URL)
    
    if not web_set:
        print("Could not find any courses on the website. Check your internet or the URL.")
        return

    # Find the difference (Items in Web but not in Local)
    missing = sorted(list(web_set - local_set))
    
    print(f"Found {len(web_set)} courses on website.")
    print(f"Found {len(local_set)} courses locally.\n")
    
    if missing:
        print(f"⚠️  {len(missing)} courses are NOT yet downloaded:")
        for i, course in enumerate(missing, 1):
            print(f"{i}. {course}")
    else:
        print("✅ All courses from this page are already downloaded!")

if __name__ == "__main__":
    main()