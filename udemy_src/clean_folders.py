import os
import sys
import re
import logging

# --- CONFIGURATION ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

def sanitize_name(name):
    """
    Cleans a string by removing Windows-illegal characters, 
    Mac-specific hidden colons, and your custom junk prefixes.
    """
    
    # 1. Define specific prefixes to strip.
    # We include variations with both / and : because Mac/Windows interpret them differently.
    junk_prefixes = [
        "वीडियो श्रृंखला/", "Video Series/", 
        "वीडियो श्रृंखला:", "Video Series:", 
        "वीडियो श्रृंखला/ ", "Video Series/ ",
        "वीडियो श्रृंखला: ", "Video Series: "
    ]
    
    clean_name = name
    
    # Remove the specific prefixes first
    for prefix in junk_prefixes:
        if clean_name.startswith(prefix):
            clean_name = clean_name.replace(prefix, "", 1)
    
    # 2. THE FIX: Explicitly replace Colons and Slashes.
    # On Mac, a '/' in Finder is often a ':' in the filesystem.
    # We replace them with a space or empty string before the regex runs.
    clean_name = clean_name.replace(':', '').replace('/', '')

    # 3. REGEX: Remove all other Windows-illegal characters
    # This covers: \ * ? " < > |
    clean_name = re.sub(r'[\\*?"<>|]', '', clean_name)
    
    # 4. Clean up trailing/leading whitespace and trailing dots
    clean_name = clean_name.strip().strip('.')
    
    return clean_name

def clean_recursively(target_path):
    target_path = os.path.abspath(target_path)
    
    if not os.path.exists(target_path):
        logging.error(f"Path does not exist: {target_path}")
        return

    logging.info(f"Scanning: {target_path}")
    
    rename_count = 0
    error_count = 0

    # bottom-up (topdown=False) is necessary to rename folders correctly
    for root, dirs, files in os.walk(target_path, topdown=False):
        
        # Process both folders (dirs) and files
        for item in (files + dirs):
            old_path = os.path.join(root, item)
            
            if old_path == target_path:
                continue
                
            new_filename = sanitize_name(item)
            
            # Only rename if the name actually changed and isn't empty
            if new_filename and new_filename != item:
                new_path = os.path.join(root, new_filename)
                
                if os.path.exists(new_path):
                    logging.warning(f"SKIPPED: '{item}' -> '{new_filename}' (Already exists)")
                    continue
                    
                try:
                    os.rename(old_path, new_path)
                    logging.info(f"SUCCESS: '{item}' -> '{new_filename}'")
                    rename_count += 1
                except Exception as e:
                    logging.error(f"FAILED: '{item}'. Error: {e}")
                    error_count += 1

    logging.info(f"Done. Renamed: {rename_count}, Errors: {error_count}")

if __name__ == "__main__":
    folder_to_clean = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    clean_recursively(folder_to_clean)