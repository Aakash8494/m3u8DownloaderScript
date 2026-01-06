import os
import platform

# --- Configuration ---
SOURCE_PATH = '/Users/aakashjadhav/Documents/GitHub/m3u8DownloaderScript/src/output_videos'
DEST_PATH = '/Volumes/500GB - PENDRIVE/AP'

def normalize(name):
    """Handles minor naming differences (strips extra spaces)."""
    return name.strip()

print("--- Checking for Missing Folders ---\n")

# 1. Check if paths exist
if not os.path.exists(SOURCE_PATH):
    print(f"❌ Error: Source path not found: {SOURCE_PATH}")
    exit()
if not os.path.exists(DEST_PATH):
    print(f"❌ Error: Pendrive path not found: {DEST_PATH}")
    exit()

# 2. Get the list of folders currently on the Pendrive
# We use a 'set' for fast checking
dest_folders = set(normalize(f) for f in os.listdir(DEST_PATH) if not f.startswith('.'))

# 3. Find what is missing
missing_folders = []

# Scan source folders
for item in os.listdir(SOURCE_PATH):
    if item.startswith('.'): continue # Skip hidden files
    
    full_path = os.path.join(SOURCE_PATH, item)
    
    if os.path.isdir(full_path):
        normalized_name = normalize(item)
        
        # If the name is NOT in the destination list, it's missing
        if normalized_name not in dest_folders:
            missing_folders.append(item)

# 4. Sort the missing list Alphabetically (A-Z)
missing_folders.sort()

# --- Output Results ---
if not missing_folders:
    print("🎉 Good news: No folders are missing. Your Pendrive is up to date.")
else:
    print(f"⚠️ Found {len(missing_folders)} missing folders.")
    print("Here they are (sorted alphabetically):\n")
    
    for name in missing_folders:
        print(f"[MISSING] {name}")

    # Save to a file on Desktop
    output_file = os.path.join(os.path.expanduser('~'), 'Desktop', 'missing_folders.txt')
    with open(output_file, 'w') as f:
        for name in missing_folders:
            f.write(f"{name}\n")
    
    print(f"\n📄 I have also saved this list to: {output_file}")