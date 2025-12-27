import os

def rename_folders(target_path):
    # We check for both the slash and common replacements like a colon or dash
    junk_prefixes = ["वीडियो श्रृंखला/", "Video Series/", "वीडियो श्रृंखला", "Video Series"]
    
    print(f"--- Scanning directory: {target_path} ---")
    
    found_any = False
    for folder_name in os.listdir(target_path):
        full_path = os.path.join(target_path, folder_name)

        if os.path.isdir(full_path):
            found_any = True
            new_name = folder_name
            
            # Check for matches
            matched_prefix = None
            for prefix in junk_prefixes:
                if folder_name.startswith(prefix):
                    matched_prefix = prefix
                    new_name = folder_name.replace(prefix, "").strip()
                    break # Stop looking once we find a match
            
            if new_name != folder_name:
                new_path = os.path.join(target_path, new_name)
                try:
                    os.rename(full_path, new_path)
                    print(f"[SUCCESS] Renamed: '{folder_name}' -> '{new_name}'")
                except Exception as e:
                    print(f"[ERROR]   Could not rename '{folder_name}': {e}")
            else:
                print(f"[SKIPPED] No match found for: '{folder_name}'")
    
    if not found_any:
        print("[NOTICE]  No folders were found in this directory at all.")
    print("--- Scan Complete ---")

if __name__ == "__main__":
    # This gets the folder where the script is saved
    current_dir = os.path.dirname(os.path.abspath(__file__))
    rename_folders(current_dir)