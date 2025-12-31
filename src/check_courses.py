import os
import pyperclip
import json
import re

# --- CONFIGURATION ---
CONFIG = {
    "LOCAL_DIRECTORY": "/Users/aakashjadhav/Documents/GitHub/m3u8DownloaderScript/src/output_videos",
    
    # 1. Regex to remove specific localized prefixes (Case insensitive)
    "PATTERN_PREFIX": r"वीडियो श्रृंखला|Video Series",
    
    # 2. Regex to remove symbols.
    # We define this carefully. Note the double backslash \\ inside the string for the literal backslash.
    # Python Raw String: r"[!@#$%^&()[\]{};',.`~+=|/\\*?<>:\"]"
    "PATTERN_SYMBOLS": r"[!@#$%^&()[\]{};',.`~+=|/\\*?<>:\"]",
}

class Sanitizer:
    @staticmethod
    def clean(text):
        """
        Applies cleaning logic in Python.
        """
        if not text: return ""
        
        # 1. Remove Prefixes
        text = re.sub(CONFIG["PATTERN_PREFIX"], "", text, flags=re.IGNORECASE)
        
        # 2. Remove Symbols
        text = re.sub(CONFIG["PATTERN_SYMBOLS"], "", text)
        
        # 3. Collapse Spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()

def get_local_folders(path):
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
    names_json = json.dumps(folder_list, ensure_ascii=False)
    
    # --- KEY FIX ---
    # We need to construct the JS RegExp object safely.
    # 1. Get the raw pattern from config.
    # 2. Convert it to a JSON string so backslashes are escaped correctly for JS strings.
    # 3. Slice off the surrounding quotes from json.dumps to get the inner content.
    
    js_prefix_pattern = json.dumps(CONFIG['PATTERN_PREFIX'])[1:-1]
    
    # For the symbols, we need to ensure the forward slash / is escaped for JS literal syntax,
    # OR we use the new RegExp("pattern", "flags") constructor which is safer.
    # Let's use the RegExp constructor method to match Python exactly without fighting / delimiters.
    
    js_symbol_pattern = json.dumps(CONFIG['PATTERN_SYMBOLS'])[1:-1]

    return f"""
(function() {{
    const localFolders = {names_json};
    
    // Define Regex using the RegExp constructor to avoid slash escaping hell
    const prefixRegex = new RegExp("{js_prefix_pattern}", "gi");
    const symbolRegex = new RegExp("{js_symbol_pattern}", "g");

    const clean = (text) => {{
        return text
            .replace(prefixRegex, "")
            .replace(symbolRegex, "") 
            .replace(/\\s+/g, ' ') 
            .trim();
    }};

    const selectors = ['span.font-hi', '.line-clamp-1.leading-normal', 'div.flex-col > span'];
    let elements = [];
    
    selectors.forEach(s => elements = [...elements, ...Array.from(document.querySelectorAll(s))]);
    const uniqueSpans = [...new Set(elements)];

    console.log(`Processing ${{uniqueSpans.length}} elements against ${{localFolders.length}} local folders...`);

    uniqueSpans.forEach(span => {{
        const title = span.innerText.trim();
        if (title.length < 2 || title === "FAQs") return;

        const cleanTitle = clean(title);
        const card = span.closest('a') || span.parentElement;

        if (localFolders.includes(cleanTitle)) {{
            card.style.opacity = "0.2";
            card.style.filter = "grayscale(100%)";
            card.style.pointerEvents = "none"; 
        }} else {{
            card.style.border = "4px solid #E11D48"; 
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
            print(js_code)
    else:
        print("⚠️ No folders found to process.")