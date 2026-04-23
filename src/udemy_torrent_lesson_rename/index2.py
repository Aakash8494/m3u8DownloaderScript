import os
import re

# Set the path to your directory here
# Example: r'C:\Quick Share\Code With Mosh'
directory = r'C:\\Quick Share\\[FreeCoursesOnline.Me] Code With Mosh - The Ultimate Docker Course\\video'

def rename_files(path):
    # Change current working directory
    os.chdir(path)
    
    # Pattern to find 'lesson' followed by numbers
    # It captures the number in a group to be padded
    pattern = re.compile(r'(lesson)(\d+)(.*)')

    files = [f for f in os.listdir(path) if os.path.isfile(f)]
    
    print(f"Found {len(files)} files. Starting rename...")

    for filename in files:
        match = pattern.match(filename)
        if match:
            prefix = match.group(1)   # 'lesson'
            number = match.group(2)   # e.g., '1'
            suffix = match.group(3)   # everything after the number
            
            # Pad the number to 2 digits (e.g., '1' becomes '01')
            new_number = number.zfill(2)
            
            new_name = f"{prefix}{new_number}{suffix}"
            
            if filename != new_name:
                print(f"Renaming: {filename} -> {new_name}")
                os.rename(filename, new_name)

    print("Renaming complete!")

if __name__ == "__main__":
    if os.path.exists(directory):
        rename_files(directory)
    else:
        print("Error: The directory path provided does not exist.")