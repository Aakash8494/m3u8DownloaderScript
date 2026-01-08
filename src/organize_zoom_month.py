import os
import shutil
import datetime

def organize_zoom_by_month():
    source_dir = os.getcwd()
    files = [f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f))]
    
    print(f"Found {len(files)} files. Organizing by Month...\n")

    for filename in files:
        if filename == os.path.basename(__file__):
            continue

        # Check if file starts with GMT and has enough characters for a date
        # Expected format: GMT20230323-...
        if filename.startswith("GMT") and len(filename) >= 11:
            
            # Extract the date part (characters 3 to 11) -> "20230323"
            date_str = filename[3:11]
            
            # Verify it is actually numbers
            if date_str.isdigit():
                try:
                    # Parse the date object
                    date_obj = datetime.datetime.strptime(date_str, "%Y%m%d")
                    
                    # Create folder name: "2023-03 (March)"
                    # %Y = Year, %m = Month number, %B = Month name
                    folder_name = date_obj.strftime("%Y-%m (%B)")
                    
                    target_folder = os.path.join(source_dir, folder_name)
                    
                    # Create folder if it doesn't exist
                    if not os.path.exists(target_folder):
                        os.makedirs(target_folder)
                        print(f"📁 Created Month Folder: {folder_name}")

                    # Move the file
                    shutil.move(os.path.join(source_dir, filename), os.path.join(target_folder, filename))
                    print(f"   -> Moved {filename} to {folder_name}")
                    
                except ValueError:
                    print(f"   ⚠️ Skipped (Date parse error): {filename}")
            else:
                print(f"   ⚠️ Skipped (No valid date found): {filename}")
        else:
            print(f"   ⚠️ Skipped (Not a Zoom file): {filename}")

    print("\n✅ Monthly organization complete.")

if __name__ == "__main__":
    organize_zoom_by_month()