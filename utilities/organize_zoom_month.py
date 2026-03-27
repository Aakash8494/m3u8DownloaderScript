import os
import shutil
import datetime
import argparse

def get_unique_filename(destination_folder, filename):
    """
    Checks if filename exists in destination.
    If yes, returns a new name like 'filename - DUPLICATE.ext'
    If that also exists, returns 'filename - DUPLICATE_1.ext', etc.
    """
    base_name, extension = os.path.splitext(filename)
    counter = 0
    new_filename = filename
    
    # Check if the file exists at the destination path
    while os.path.exists(os.path.join(destination_folder, new_filename)):
        if counter == 0:
            new_filename = f"{base_name} - DUPLICATE{extension}"
        else:
            new_filename = f"{base_name} - DUPLICATE_{counter}{extension}"
        counter += 1
        
    return new_filename

def organize_recursive(source_root, dest_root):
    # 1. Validate paths
    if not os.path.exists(source_root):
        print(f"❌ Error: Source folder '{source_root}' does not exist.")
        return

    # Create destination if it doesn't exist
    if not os.path.exists(dest_root):
        os.makedirs(dest_root)
        print(f"📁 Created destination root: {dest_root}")

    print(f"🚀 Scanning recursively from: {source_root}")
    print(f"🎯 Moving organized files to: {dest_root}\n")

    files_moved = 0
    
    # 2. Walk through all folders and subfolders
    for root, dirs, files in os.walk(source_root):
        for filename in files:
            
            # Skip the script itself
            if filename == os.path.basename(__file__):
                continue

            # Check for Zoom filename pattern (GMT...)
            if filename.startswith("GMT") and len(filename) >= 11:
                
                date_str = filename[3:11] # Extract '20230323'
                
                if date_str.isdigit():
                    try:
                        # Parse date
                        date_obj = datetime.datetime.strptime(date_str, "%Y%m%d")
                        folder_name = date_obj.strftime("%Y-%m (%B)")
                        
                        # Define the target folder inside the DESTINATION root
                        target_month_folder = os.path.join(dest_root, folder_name)
                        
                        # Create the month folder in the destination if missing
                        if not os.path.exists(target_month_folder):
                            os.makedirs(target_month_folder)
                        
                        # --- DUPLICATE HANDLING ---
                        final_filename = get_unique_filename(target_month_folder, filename)
                        
                        # Build full paths
                        src_path = os.path.join(root, filename)
                        dst_path = os.path.join(target_month_folder, final_filename)
                        
                        # Move the file
                        shutil.move(src_path, dst_path)
                        
                        # Log message based on whether it was renamed
                        if filename != final_filename:
                            print(f"   ⚠️ Duplicate found! Renamed: {final_filename}")
                        else:
                            print(f"   -> Moved: {filename}")
                            
                        files_moved += 1
                        
                    except ValueError:
                        pass # Ignore parse errors quietly
                else:
                    pass # Ignore non-digit dates quietly

    print(f"\n✅ Recursive organization complete.")
    print(f"📊 Total files moved: {files_moved}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Recursively organize Zoom recordings into a new folder.")
    parser.add_argument("source", help="The root folder to search for Zoom files")
    parser.add_argument("dest", help="The final folder where files will be moved")
    
    args = parser.parse_args()
    organize_recursive(args.source, args.dest)