import os
import pyperclip
import json
import re

# --- CONFIGURATION ---
LOCAL_DIRECTORY = "/Users/aakashjadhav/Documents/GitHub/m3u8DownloaderScript/src/output_videos"

def core_sanitizer(name):
    """
    The master logic for cleaning strings to be Windows-compatible.
    """
    # 1. Remove specific junk prefixes
    junk = ["वीडियो श्रृंखला/", "Video Series/", "वीडियो श्रृंखला:", "Video Series:", "वीडियो श्रृंखला", "Video Series"]
    for prefix in junk:
        if name.startswith(prefix):
            name = name.replace(prefix, "", 1)
    
    # 2. Remove Windows Reserved Characters: \ / : * ? " < > |
    name = re.sub(r'[\\/:*?"<>|]', '', name)
    
    # 3. Collapse multiple spaces into a single space
    name = re.sub(r'\s+', ' ', name)
    
    # 4. Final trim of whitespace and trailing dots
    return name.strip().strip('.')

def get_local_folders(path):
    """Retrieves and sanitizes folder names from a local path."""
    if not os.path.exists(path):
        print(f"[ERROR] Path not found: {path}")
        return []
    
    items = os.listdir(path)
    # Only process directories, applying the core_sanitizer to each
    return [core_sanitizer(f) for f in items if os.path.isdir(os.path.join(path, f))]

def generate_js_snippet(folder_list):
    """Creates the JS code used for browser comparison."""
    names_json = json.dumps(folder_list, ensure_ascii=False)
    
    return f"""
(function() {{
    const localFolders = {names_json};
    
    // Internal JS cleaning logic to match Python's core_sanitizer
    const clean = (text) => {{
        return text
            .replace(/वीडियो श्रृंखला|Video Series/g, "")
            .replace(/[:/"\\\\|*?<>]/g, "") 
            .replace(/\\s+/g, ' ') 
            .trim()
            .replace(/\\.+$/, "");
    }};

    const selectors = ['span.font-hi', '.line-clamp-1.leading-normal', 'div.flex-col > span'];
    let elements = [];
    selectors.forEach(s => elements = [...elements, ...Array.from(document.querySelectorAll(s))]);
    const uniqueSpans = [...new Set(elements)];

    uniqueSpans.forEach(span => {{
        const title = span.innerText.trim();
        if (title.length < 2 || title === "FAQs") return;

        const cleanTitle = clean(title);
        const card = span.closest('a') || span.parentElement;

        if (localFolders.includes(cleanTitle)) {{
            card.style.opacity = "0.2";
            card.style.filter = "grayscale(100%)";
        }} else {{
            card.style.border = "4px solid #E11D48";
            card.style.position = "relative";
            // Add Badge logic here if needed
        }}
    }});
    console.log("Scan Complete.");
}})();
    """

if __name__ == "__main__":
    folders = get_local_folders(LOCAL_DIRECTORY)
    js_code = generate_js_snippet(folders)
    pyperclip.copy(js_code)
    print(f"✅ Processed {len(folders)} folders. JS snippet copied to clipboard.")