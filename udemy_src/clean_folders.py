import os
import sys
import re
import logging

# --- CONFIGURATION ---
# Setting up logging to show the time and the type of message (INFO, ERROR, etc.)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout) # This ensures logs print to your console
    ]
)

def sanitize_name(name):
    """
    Cleans a string by removing Windows-illegal characters and specific prefixes.
    """
    # 1. Define specific "Junk" strings you want to strip out
    junk_prefixes = [
        "वीडियो श्रृंखला/", "Video Series/", 
        "वीडियो श्रृंखला:", "Video Series:", 
        "वीडियो श्रृंखला/ ", "Video Series/ ",
        "वीडियो श्रृंखला: ", "Video Series: "
    ]
    
    clean_name = name
    
    # Remove the specific prefixes if the name starts with them
    for prefix in junk_prefixes:
        if clean_name.startswith(prefix):
            # replace(prefix, "", 1) only replaces the first occurrence
            clean_name = clean_name.replace(prefix, "", 1)
    
    # 2. REGEX: Remove Windows-illegal characters
    # [\\/:*?"<>|] matches any of these: \ / : * ? " < > |
    # We replace them with an empty string ""
    clean_name = re.sub(r'[\\/:*?"<>|]', '', clean_name)
    
    # 3. Windows ignores trailing spaces and dots at the end of filenames/folders.
    # If they exist, Windows often can't "find" the file. We strip them here.
    clean_name = clean_name.strip().strip('.')
    
    return clean_name

def clean_recursively(target_path):
    """
    Navigates through all subdirectories and renames files/folders.
    """
    target_path = os.path.abspath(target_path)
    
    if not os.path.exists(target_path):
        logging.error(f"Path does not exist: {target_path}")
        return

    logging.info(f"Starting recursive scan in: {target_path}")
    
    # count variables for the final report
    rename_count = 0
    error_count = 0

    # os.walk(topdown=False) is CRITICAL.
    # It starts at the deepest subfolder and works its way UP to the root.
    # If we renamed a parent folder first, the paths to the files inside would break.
    for root, dirs, files in os.walk(target_path, topdown=False):
        
        # We process both files and directories found in the current 'root'
        for item in (files + dirs):
            old_path = os.path.join(root, item)
            
            # Skip the root folder we started in
            if old_path == target_path:
                continue
                
            new_filename = sanitize_name(item)
            
            # If the name is different after cleaning and not empty...
            if new_filename and new_filename != item:
                new_path = os.path.join(root, new_filename)
                
                # Check if a file with the new name already exists to prevent data loss
                if os.path.exists(new_path):
                    logging.warning(f"SKIPPED: '{item}' -> '{new_filename}' (Destination already exists)")
                    continue
                    
                try:
                    os.rename(old_path, new_path)
                    logging.info(f"SUCCESS: '{item}' renamed to '{new_filename}'")
                    rename_count += 1
                except Exception as e:
                    logging.error(f"FAILED: Could not rename '{item}'. Error: {e}")
                    error_count += 1

    logging.info(f"Processing Complete. Renamed: {rename_count}, Errors: {error_count}")

if __name__ == "__main__":
    # Get folder path from command line argument, or use current directory
    if len(sys.argv) > 1:
        folder_to_clean = sys.argv[1]
    else:
        folder_to_clean = os.getcwd()
        
    clean_recursively(folder_to_clean)