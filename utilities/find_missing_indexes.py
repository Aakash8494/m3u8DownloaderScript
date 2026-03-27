import os
import re
import sys

def find_missing_indexes(folder_path):
    if not os.path.isdir(folder_path):
        print(f"❌ Invalid directory: {folder_path}")
        sys.exit(1)

    indexes = []

    for filename in os.listdir(folder_path):
        match = re.match(r"(\d+)\.", filename)
        if match:
            indexes.append(int(match.group(1)))

    if not indexes:
        print("⚠️ No indexed files found.")
        return

    indexes.sort()

    expected = set(range(indexes[0], indexes[-1] + 1))
    actual = set(indexes)

    missing = sorted(expected - actual)

    print(f"📁 Folder          : {folder_path}")
    print(f"🔢 Found indexes   : {indexes}")
    print(f"❓ Missing indexes : {missing if missing else 'None 🎉'}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python find_missing_indexes.py <folder_path>")
        sys.exit(1)

    folder_path = sys.argv[1]
    find_missing_indexes(folder_path)


    # python find_missing_indexes.py "/Users/aakashjadhav/Downloads/udemy-downloaded-nextjs react chai with code"