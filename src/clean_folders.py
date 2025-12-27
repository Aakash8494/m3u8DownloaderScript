import os

def rename_folders(target_path):
    # 1. Define the strings we want to get rid of
    junk_prefixes = ["वीडियो श्रृंखला/ ", "Video Series/ "]

    # 2. List everything in the folder
    for folder_name in os.listdir(target_path):
        full_path = os.path.join(target_path, folder_name)

        # 3. Only process if it is a folder (directory)
        if os.path.isdir(full_path):
            new_name = folder_name
            
            # 4. Check if the name starts with our junk strings
            for prefix in junk_prefixes:
                if folder_name.startswith(prefix):
                    new_name = folder_name.replace(prefix, "").strip()
            
            # 5. Perform the actual rename if a change is needed
            if new_name != folder_name:
                new_path = os.path.join(target_path, new_name)
                os.rename(full_path, new_path)
                print(f"Renamed: {folder_name} -> {new_name}")

# Run the function on the current folder
if __name__ == "__main__":
    current_dir = os.getcwd() 
    rename_folders(current_dir)