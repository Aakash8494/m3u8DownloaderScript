import os
import requests
from bs4 import BeautifulSoup
import pyperclip # Make sure to run: pip install pyperclip

# --- CONFIGURATION ---
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
        # Chain replacements to handle both prefixes
        name = f.replace("वीडियो श्रृंखला/", "").replace("Video Series/", "").strip()
        cleaned_names.append(name)
    return set(cleaned_names)

def get_website_courses(url):
    """Scrapes titles using the exact class string provided."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8' 
        
        soup = BeautifulSoup(response.text, 'html.parser')
        course_titles = []
        
        target_classes = ["font-normal", "font-hi", "text-[#2E2F31]"]
        spans = soup.find_all('span', class_=lambda x: x and all(c in x for c in target_classes))
        
        for span in spans:
            title = span.get_text().strip()
            if title and title not in ["Video Series", "FAQs"] and len(title) > 1:
                course_titles.append(title)
        
        return set(course_titles)
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

    missing = sorted(list(web_set - local_set))
    
    print(f"Found {len(web_set)} courses on website.")
    print(f"Found {len(local_set)} courses locally.\n")
    
    if missing:
        # Join the missing courses with newlines
        output_text = "\n".join(missing)
        
        # Copy to clipboard
        pyperclip.copy(output_text)
        
        print(f"⚠️  {len(missing)} courses are NOT yet downloaded (COPIED TO CLIPBOARD):")
        print("--------------------------------------------------")
        print(output_text)
        print("--------------------------------------------------")
    else:
        print("✅ All courses from this page are already downloaded!")

if __name__ == "__main__":
    main()