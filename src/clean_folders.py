import os
import sys

def rename_folders(target_path):
    # 1. Standardize the path
    target_path = os.path.abspath(target_path)
    
    # 2. Define the exact strings to remove
    # Note: On macOS, slashes in names are often stored as colons ':' internally
    junk_prefixes = ["वीडियो श्रृंखला/ ", "Video Series/ ","वीडियो श्रृंखला: ", "Video Series: ", "वीडियो श्रृंखला/", "Video Series/", "वीडियो श्रृंखला:", "Video Series:"]
    
    print(f"--- Scanning directory: {target_path} ---")
    
    if not os.path.exists(target_path):
        print(f"[ERROR] Path does not exist: {target_path}")
        return

    items = os.listdir(target_path)
    if not items:
        print("[NOTICE] Folder is empty.")
        return

    for folder_name in items:
        full_path = os.path.join(target_path, folder_name)

        if os.path.isdir(full_path):
            new_name = folder_name
            
            for prefix in junk_prefixes:
                if folder_name.startswith(prefix):
                    new_name = folder_name.replace(prefix, "").strip()
                    break
            
            if new_name != folder_name:
                new_path = os.path.join(target_path, new_name)
                try:
                    os.rename(full_path, new_path)
                    print(f"[SUCCESS] '{folder_name}' -> '{new_name}'")
                except Exception as e:
                    print(f"[ERROR] Failed to rename '{folder_name}': {e}")
            else:
                print(f"[DEBUG] No prefix match for: '{folder_name}'")

if __name__ == "__main__":
    # This logic now correctly takes the folder from your terminal command
    if len(sys.argv) > 1:
        folder_to_clean = sys.argv[1]
    else:
        folder_to_clean = os.getcwd()
        
    rename_folders(folder_to_clean)