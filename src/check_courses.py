import os
import pyperclip
import json
import re

# --- CONFIGURATION ---
CONFIG = {
    "LOCAL_DIRECTORY": "/Users/aakashjadhav/Documents/GitHub/m3u8DownloaderScript/src/output_videos",
    
    # 1. Regex to remove specific localized prefixes (Case insensitive)
    "PATTERN_PREFIX": r"वीडियो श्रृंखला|Video Series",
    
    # 2. Regex to remove '!' and all other messy symbols
    # Matches: ! @ # $ % ^ & ( ) [ ] { } ; ' , . ` ~ + = | / \ * ? < > : "
    "PATTERN_SYMBOLS": r"[!@#$%^&()[\]{};',.`~+=|/\\*?<>:\"]",
}

class Sanitizer:
    @staticmethod
    def clean(text):
        """
        Applies the exact same cleaning logic as the browser script.
        """
        if not text: return ""
        
        # 1. Remove Prefixes
        text = re.sub(CONFIG["PATTERN_PREFIX"], "", text, flags=re.IGNORECASE)
        
        # 2. Remove Symbols (including !)
        text = re.sub(CONFIG["PATTERN_SYMBOLS"], "", text)
        
        # 3. Collapse Spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()

def get_local_folders(path):
    """Scans the local directory and returns a list of sanitized folder names."""
    if not os.path.exists(path):
        print(f"❌ [ERROR] Path not found: {path}")
        return []

    clean_names = []
    raw_folders = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]

    print(f"📂 Found {len(raw_folders)} local folders. Sanitizing...")

    for folder in raw_folders:
        clean_name = Sanitizer.clean(folder)
        if clean_name:
            clean_names.append(clean_name)
            
    return clean_names

def generate_js_snippet(folder_list):
    """
    Generates the JavaScript code. 
    NOTE: We inject the exact same regex logic into the JS so the browser behaves identically.
    """
    names_json = json.dumps(folder_list, ensure_ascii=False)
    
    # We use an f-string with a raw string literal (r) for the JS code.
    # We double the curly braces {{ }} for JS code, single { } for Python variables.
    return f"""
(function() {{
    // 1. Data from Python
    const localFolders = {names_json};
    
    // 2. Cleaning Logic (Synced with Python)
    const clean = (text) => {{
        return text
            .replace(/{CONFIG['PATTERN_PREFIX']}/gi, "")
            .replace(/{CONFIG['PATTERN_SYMBOLS'].replace('\\', '\\\\')}/g, "") 
            .replace(/\\s+/g, ' ') 
            .trim();
    }};

    // 3. UI Logic
    const selectors = ['span.font-hi', '.line-clamp-1.leading-normal', 'div.flex-col > span'];
    let elements = [];
    
    // Aggregate all potential title elements
    selectors.forEach(s => elements = [...elements, ...Array.from(document.querySelectorAll(s))]);
    const uniqueSpans = [...new Set(elements)];

    console.log(`Processing ${{uniqueSpans.length}} elements against ${{localFolders.length}} local folders...`);

    uniqueSpans.forEach(span => {{
        const title = span.innerText.trim();
        if (title.length < 2 || title === "FAQs") return;

        const cleanTitle = clean(title);
        const card = span.closest('a') || span.parentElement;

        if (localFolders.includes(cleanTitle)) {{
            // MATCH FOUND: Gray it out
            card.style.opacity = "0.2";
            card.style.filter = "grayscale(100%)";
            card.style.pointerEvents = "none"; // Optional: prevent clicking
        }} else {{
            // MISSING: Highlight it
            card.style.border = "4px solid #E11D48"; // Red border
            card.style.boxShadow = "0 0 10px rgba(225, 29, 72, 0.5)";
        }}
    }});
    
    console.log("✅ Visual Scan Complete.");
}})();
"""

if __name__ == "__main__":
    folders = get_local_folders(CONFIG["LOCAL_DIRECTORY"])
    
    if folders:
        js_code = generate_js_snippet(folders)
        try:
            pyperclip.copy(js_code)
            print("-" * 40)
            print(f"✅ Success! Processed {len(folders)} folders.")
            print("📋 JavaScript snippet copied to clipboard.")
            print("-" * 40)
        except Exception as e:
            print(f"⚠️ Could not copy to clipboard: {e}")
            print("Printing code instead:\n")
            print(js_code)
    else:
        print("⚠️ No folders found to process.")