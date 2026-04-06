import os
import shutil
import argparse
from pathlib import Path

def organize_gdrive(target_dir):
    # Resolve the path to an absolute path
    base_dir = Path(target_dir).resolve()
    
    if not base_dir.exists():
        print(f"❌ Error: The path '{base_dir}' does not exist.")
        return

    print(f"🚀 Starting organization for: {base_dir}\n")

    # The 8 Master Folders and their exact targets from your drive
    categories = {
        "01_Identity_and_Family": [
            "DOCUMENTS/3. ADHAAR PAN VOTER", 
            "DOCUMENTS/4. PASSPORTS", 
            "DOCUMENTS/2. COVID_DOCUMENTS"
        ],
        "02_Career_and_Employment": [
            "DOCUMENTS/1. company documents", 
            "DOCUMENTS/5. COGNIZANT DOCUMENTS",
            "Nagarro payslips", 
            "drive/Cognizant", 
            "eletters",
            "DOCUMENTS/1. Nagarro Documents", 
            "DOCUMENTS/1. DOCUMENTS_All/1. ZEKI DOCUMENTS"
        ],
        "03_Education_and_Academics": [
            "DOCUMENTS/1. DOCUMENTS_All/2. RESULTS OF EXAM"
        ],
        "04_Property_and_Home": [
            "DOCUMENTS/5. Kolte Patil", 
            "PUNE FLAT DOCUMENTS", 
            "PUNE GAS BILL KYC",
            "DOCUMENTS/Deed of Transfer", 
            "DOCUMENTS/Individual Agreement",
            "DOCUMENTS/Individual Agreement Dede", 
            "DOCUMENTS/Life republic ",
            "DOCUMENTS/Property evaluation", 
            "DOCUMENTS/Gas bill"
        ],
        "05_Immigration_and_Travel": [
            "GERMANY OPPORTUNITY CARD", 
            "TIG DOCUMENTS"
        ],
        "06_Purchases_and_Warranties": [
            "bills-tv-s24", 
            "DOCUMENTS/BILLS", 
            "DOCUMENTS/6. Fan warranty card",
            "DOCUMENTS/Gold Evaluation", 
            "DOCUMENTS/Purchases", 
            "DOCUMENTS/Other bills"
        ],
        "07_Media_and_Personal": [
            "PICS ALL FOLDER WISE", 
            "aakash.s.jadhav@gmail.com"
        ],
        "08_Archive_and_Review": [
            "__BIN"
        ]
    }

    # Step 1: Create the 8 target directories
    for category in categories.keys():
        target_folder = base_dir / category
        target_folder.mkdir(exist_ok=True)

    # Step 2: Move the items safely
    for category, sources in categories.items():
        dest_folder = base_dir / category

        for src_path_str in sources:
            src_path = base_dir / src_path_str

            # Only attempt to move if the source folder/file actually exists
            if src_path.exists():
                dest_path = dest_folder / src_path.name

                # STRICT RULE: No overwrite/delete. Handle collisions safely.
                if dest_path.exists():
                    suffix = 1
                    # Keep adding numbers until we find an empty name
                    while dest_path.with_name(f"{src_path.name}_{suffix}").exists():
                        suffix += 1
                    dest_path = dest_path.with_name(f"{src_path.name}_{suffix}")

                try:
                    shutil.move(str(src_path), str(dest_path))
                    print(f"✅ Moved: {src_path.name} -> {category}/{dest_path.name}")
                except Exception as e:
                    print(f"⚠️ Failed to move {src_path.name}: {e}")
            else:
                # Silently skip if not found, keeps the terminal clean
                pass

    print("\n🎉 Organization complete! Zero files were deleted.")

if __name__ == "__main__":
    # Setup the argument parser for the path
    parser = argparse.ArgumentParser(description="Safely organize downloaded Google Drive folders.")
    parser.add_argument("path", help="The path to your Google Drive sync folder")
    
    args = parser.parse_args()
    organize_gdrive(args.path)