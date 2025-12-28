import os
import pyperclip
import json

# --- CONFIGURATION ---
LOCAL_DIRECTORY = "/Users/aakashjadhav/Documents/GitHub/m3u8DownloaderScript/src/output_videos"

def get_js_snippet():
    print(f"--- DEBUG: Accessing Directory: {LOCAL_DIRECTORY} ---")
    
    if not os.path.exists(LOCAL_DIRECTORY):
        print(f"[ERROR] Path does not exist: {LOCAL_DIRECTORY}")
        return

    # 1. Get all items and filter for folders only
    all_items = os.listdir(LOCAL_DIRECTORY)
    folders = [f for f in all_items if os.path.isdir(os.path.join(LOCAL_DIRECTORY, f))]
    
    print(f"[INFO] Found {len(folders)} total folders.")

    # 2. Clean names to match website text (Removing prefixes/slashes)
    clean_names = []
    junk_prefixes = ["वीडियो श्रृंखला/", "Video Series/", "वीडियो श्रृंखला:", "Video Series:", "वीडियो श्रृंखला", "Video Series"]
    
    for f in folders:
        temp_name = f
        for prefix in junk_prefixes:
            if temp_name.startswith(prefix):
                temp_name = temp_name.replace(prefix, "").strip()
        
        # Log one example to check if cleaning is working
        clean_names.append(temp_name)

    print(f"[DEBUG] Sample cleaned name: '{clean_names[0] if clean_names else 'None'}'")

    # 3. Create the JS code with a built-in logger
    # We use json.dumps to ensure Hindi characters and quotes are handled correctly for JS
    names_json = json.dumps(clean_names, ensure_ascii=False)

    js_code = f"""
(function() {{
    const localFolders = {names_json};
    console.log("--- DEBUG: JS Snippet Started ---");
    
    // 1. Define multiple potential selectors based on your input
    const selectors = [
        'span.font-hi',                                     // Your original
        'span.font-normal.font-hi',                        // Combined fonts
        'span[class*="text-[#2E2F31]"]',                   // Specific color hex
        '.line-clamp-1.leading-normal',                    // Layout classes
        'div.flex-col > span'                              // Structure-based
    ];

    // 2. Gather all unique elements matching any of these selectors
    let allElements = [];
    selectors.forEach(selector => {{
        const found = document.querySelectorAll(selector);
        allElements = [...allElements, ...Array.from(found)];
    }});

    // Remove duplicates (elements matching multiple selectors)
    const courseSpans = [...new Set(allElements)];
    
    console.log("Total unique elements found:", courseSpans.length);

    let matchCount = 0;
    let highlightCount = 0;

    courseSpans.forEach((span) => {{
        const webTitle = span.innerText.trim();
        
        // Skip empty or generic UI labels
        if (!webTitle || webTitle.length < 2 || webTitle === "Video Series" || webTitle === "FAQs") return;

        // DEBUG: Log every 10th title to console to verify what the script is "seeing"
        // console.log("Checking web title:", webTitle);

        // 3. The Comparison Logic
        if (localFolders.includes(webTitle)) {{
            matchCount++;
            // Dim items we ALREADY have
            const card = span.closest('a') || span.parentElement;
            card.style.opacity = "0.2"; 
            card.style.filter = "grayscale(100%)";
        }} else {{
            // HIGHLIGHT items we are MISSING
            highlightCount++;
            const card = span.closest('a') || span.parentElement;
            card.style.border = "4px solid #E11D48"; // Rose-600 color
            card.style.backgroundColor = "rgba(225, 29, 72, 0.05)";
            card.style.borderRadius = "8px";
            
            // Add a visual badge
            if (!card.querySelector('.missing-badge')) {{
                const badge = document.createElement('div');
                badge.className = 'missing-badge';
                badge.innerText = "MISSING";
                badge.style.cssText = "position:absolute; top:10px; right:10px; background:#E11D48; color:white; font-size:12px; padding:4px 8px; border-radius:4px; z-index:10; font-weight:bold;";
                card.style.position = "relative";
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