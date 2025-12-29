import os
import pyperclip
import json
import re

# --- CONFIGURATION ---
LOCAL_DIRECTORY = "/Users/aakashjadhav/Documents/GitHub/m3u8DownloaderScript/src/output_videos"

def sanitize_name(name):
    """
    Synchronized sanitization logic to match the download scripts.
    """
    # 1. Junk prefixes to strip
    junk_prefixes = [
        "वीडियो श्रृंखला/", "Video Series/", 
        "वीडियो श्रृंखला:", "Video Series:", 
        "वीडियो श्रृंखला/ ", "Video Series/ ",
        "वीडियो श्रृंखला: ", "Video Series: ",
        "वीडियो श्रृंखला", "Video Series"
    ]
    
    clean_name = name
    for prefix in junk_prefixes:
        if clean_name.startswith(prefix):
            clean_name = clean_name.replace(prefix, "", 1)
    
    # 2. Remove Windows Reserved Characters: \ / : * ? " < > |
    clean_name = re.sub(r'[\\/:*?"<>|]', '', clean_name)
    
    # 3. Clean up trailing spaces or dots
    clean_name = clean_name.strip().strip('.')
    
    return clean_name

def get_js_snippet():
    print(f"--- DEBUG: Accessing Directory: {LOCAL_DIRECTORY} ---")
    
    if not os.path.exists(LOCAL_DIRECTORY):
        print(f"[ERROR] Path does not exist: {LOCAL_DIRECTORY}")
        return

    # 1. Get folders and sanitize them
    all_items = os.listdir(LOCAL_DIRECTORY)
    folders = [f for f in all_items if os.path.isdir(os.path.join(LOCAL_DIRECTORY, f))]
    
    # We sanitize the local names so we are comparing "clean" against "clean"
    clean_local_names = [sanitize_name(f) for f in folders]
    
    print(f"[INFO] Found {len(folders)} folders. (Sanitized for matching)")

    # 2. Create the JS code
    names_json = json.dumps(clean_local_names, ensure_ascii=False)

    js_code = f"""
(function() {{
    const localFolders = {names_json};
    console.log("--- DEBUG: JS Snippet Started ---");
    
    // Helper to clean website titles so they match the local sanitized folder names
    const cleanWebTitle = (text) => {{
        return text
            .replace(/वीडियो श्रृंखला|Video Series/g, "") // Remove words
            .replace(/[:/"\\\\|*?<>]/g, "")               // Remove illegal Windows chars
            .replace(/\\s+/g, ' ')                        // Collapse multiple spaces
            .trim()
            .replace(/\\.+$/, "");                        // Remove trailing dots
    }};

    const selectors = [
        'span.font-hi', 
        'span.font-normal.font-hi',
        'span[class*="text-[#2E2F31]"]',
        '.line-clamp-1.leading-normal',
        'div.flex-col > span'
    ];

    let allElements = [];
    selectors.forEach(selector => {{
        const found = document.querySelectorAll(selector);
        allElements = [...allElements, ...Array.from(found)];
    }});

    const courseSpans = [...new Set(allElements)];
    console.log("Total unique elements found:", courseSpans.length);

    let matchCount = 0;
    let highlightCount = 0;

    courseSpans.forEach((span) => {{
        const originalTitle = span.innerText.trim();
        
        // Skip empty or generic UI labels
        if (!originalTitle || originalTitle.length < 2) return;

        // SANITIZE the title from the website before comparing
        const sanitizedWebTitle = cleanWebTitle(originalTitle);
        
        if (!sanitizedWebTitle || sanitizedWebTitle === "FAQs") return;

        // 3. The Comparison Logic (Sanitized vs Sanitized)
        if (localFolders.includes(sanitizedWebTitle)) {{
            matchCount++;
            const card = span.closest('a') || span.parentElement;
            card.style.opacity = "0.2"; 
            card.style.filter = "grayscale(100%)";
        }} else {{
            highlightCount++;
            const card = span.closest('a') || span.parentElement;
            card.style.border = "4px solid #E11D48";
            card.style.backgroundColor = "rgba(225, 29, 72, 0.05)";
            card.style.borderRadius = "8px";
            card.style.position = "relative";
            
            if (!card.querySelector('.missing-badge')) {{
                const badge = document.createElement('div');
                badge.className = 'missing-badge';
                badge.innerText = "MISSING";
                badge.style.cssText = "position:absolute; top:10px; right:10px; background:#E11D48; color:white; font-size:12px; padding:4px 8px; border-radius:4px; z-index:10; font-weight:bold;";
                card.appendChild(badge);
            }}
        }}
    }});

    console.log(`--- SCAN SUMMARY ---`);
    console.log(`Matching Local Folders: ${{matchCount}}`);
    console.log(`Missing on Local: ${{highlightCount}}`);
    alert(`Found ${{highlightCount}} new items to download!`);
}})();
    """
    
    pyperclip.copy(js_code)
    print("\n✅ STEP 2: Paste the copied code into the Browser Console now.")

if __name__ == "__main__":
    get_js_snippet()