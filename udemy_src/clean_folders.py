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

def core_cleaner(name):
    """
    Modular logic to sanitize a single file or folder name.
    1. Removes Junk Prefixes
    2. Removes Windows-illegal characters (including : / and ")
    3. Collapses double spaces into single spaces
    4. Trims ends
    """
    # 1. Define specific prefixes to strip.
    junk_prefixes = [
        "वीडियो श्रृंखला/", "Video Series/", 
        "वीडियो श्रृंखला:", "Video Series:", 
        "वीडियो श्रृंखला/ ", "Video Series/ ",
        "वीडियो श्रृंखला: ", "Video Series: ",
        "वीडियो श्रृंखला", "Video Series"
    ]
    
    clean_name = name
    
    # Remove the specific prefixes first
    for prefix in junk_prefixes:
        if clean_name.startswith(prefix):
            clean_name = clean_name.replace(prefix, "", 1)
    
    # 2. Remove Windows Reserved Characters: \ / : * ? " < > |
    clean_name = re.sub(r'[\\/:*?"<>|]', '', clean_name)

    # 3. THE FIX: Collapse multiple spaces into a single space
    clean_name = re.sub(r'\s+', ' ', clean_name)
    
    # 4. Clean up trailing/leading whitespace and trailing dots
    return clean_name.strip().strip('.')

def process_renaming(root_path):
    """
    Handles the directory walking and OS renaming operations.
    """
    target_path = os.path.abspath(root_path)
    
    if not os.path.exists(target_path):
        logging.error(f"Path does not exist: {target_path}")
        return

    logging.info(f"--- Starting Recursive Clean: {target_path} ---")
    
    rename_count = 0
    ignore_count = 0
    error_count = 0

    # topdown=False renames children before parents
    for root, dirs, files in os.walk(target_path, topdown=False):
        for item in (files + dirs):
            old_path = os.path.join(root, item)
            
            # Skip the starting folder
            if old_path == target_path:
                continue
            
            # --- THE FIX: IGNORE HIDDEN FILES / DOTFILES ---
            # If the name starts with a dot (like .gitignore), skip it entirely
            if item.startswith('.'):
                logging.debug(f"IGNORING DOTFILE: {item}")
                ignore_count += 1
                continue
                
            new_name = core_cleaner(item)
            
            if new_name and new_name != item:
                new_path = os.path.join(root, new_name)
                
                # Check for collisions
                if os.path.exists(new_path):
                    logging.warning(f"SKIPPED: '{item}' -> '{new_name}' (Already exists)")
                    continue
                    
                try:
                    os.rename(old_path, new_path)
                    logging.info(f"RENAMED: '{item}' -> '{new_name}'")
                    rename_count += 1
                except Exception as e:
                    logging.error(f"ERROR: Could not rename '{item}'. {e}")
                    error_count += 1

    logging.info(f"--- Task Finished ---")
    logging.info(f"Successfully Renamed: {rename_count}")
    logging.info(f"Ignored (Dotfiles): {ignore_count}")
    logging.info(f"Errors Encountered: {error_count}")

if __name__ == "__main__":
    folder_to_clean = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    process_renaming(folder_to_clean)