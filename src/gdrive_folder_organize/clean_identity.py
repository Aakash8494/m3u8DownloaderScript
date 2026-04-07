import os
import shutil
import argparse
from pathlib import Path

def clean_identity_folder(target_dir):
    base_dir = Path(target_dir).resolve()
    
    if not base_dir.exists():
        print(f"❌ Error: The path '{base_dir}' does not exist.")
        return

    print(f"🚀 Starting cleanup for: {base_dir}\n")

    # 1. Create target folders
    categories = [
        "ID_Cards_Aadhar_Pan_Voter", 
        "Passports", 
        "Covid_Certificates", 
        "_Redundant_Archive"
    ]
    for cat in categories:
        (base_dir / cat).mkdir(exist_ok=True)

    # 2. The exact final files we want to keep, mapped to their new homes
    clean_files = {
        "Passports": [
            "Aakash Passport U5044550.pdf", "Harshada Passport U6031300.pdf",
            "Sunil Passport U5044552.pdf", "Supriya Passport U8333033.pdf", 
            "Passport stamp.pdf"
        ],
        "Covid_Certificates": [
            "Aakash International travel certificate.pdf", "Aakash Universal Travel Pass.pdf", 
            "Aakash Vaccination certificate for dose 2.pdf", "Harshada Certificate for COVID-19 Vaccination.pdf", 
            "Harshada Universal Travel Pass.pdf", "Sunil Certificate for COVID-19 Vaccination.pdf", 
            "Sunil Universal Travel Pass.pdf", "Supriya Certificate for COVID-19 Vaccination.pdf", 
            "Supriya Universal Travel Pass.pdf"
        ],
        "ID_Cards_Aadhar_Pan_Voter": [
            "Aakash Aadhar Card.jpg", "Aakash Aadhar Card.pdf", "Aakash Pan Card.jpg", 
            "Aakash Pan Card.pdf", "Aakash Pan Card_self_attested.pdf", "Aakash Voter Id.jpg", 
            "Aakash Voter Id.pdf", "Harshada Aadhar Card.jpg", "Harshada Aadhar Card.pdf", 
            "Harshada Pan Card.pdf", "Harshada Voter Id.jpg", "Harshada Voter Id.pdf", 
            "Sunil Aadhar Card.jpg", "Sunil Aadhar Card.pdf", "Sunil Pan Card.jpg", 
            "Sunil Pan Card.pdf", "Sunil Voter Id.jpg", "Sunil Voter Id.pdf", 
            "Supriya Aadhaar Card.jpg", "Supriya Aadhaar Card.pdf", "Supriya Pan Card.jpg", 
            "Supriya Pan Card.pdf", "Supriya Voter Id.jpg", "Supriya Voter Id.pdf"
        ]
    }

    # Flatten the map for quick lower-case lookups (Windows is case-insensitive, but this is safer)
    good_file_map = {}
    for category, files in clean_files.items():
        for f in files:
            good_file_map[f.lower()] = category

    # 3. Walk the tree to find all files
    all_files = []
    for root, dirs, files in os.walk(base_dir):
        # Skip the brand new category folders we just created so we don't process them twice
        if Path(root).name in categories:
            continue
        for file in files:
            all_files.append(Path(root) / file)

    # 4. Move files to their final destinations
    for file_path in all_files:
        file_name_lower = file_path.name.lower()
        
        # If it's on the list, it goes to the clean folder. Otherwise, into the dumpster.
        if file_name_lower in good_file_map:
            target_category = good_file_map[file_name_lower]
        else:
            target_category = "_Redundant_Archive"

        dest_folder = base_dir / target_category
        dest_path = dest_folder / file_path.name

        # STRICT RULE: No overwrite/delete. Handle collisions by adding a number.
        if dest_path.exists() and dest_path != file_path:
            suffix = 1
            while dest_path.with_name(f"{file_path.stem}_{suffix}{file_path.suffix}").exists():
                suffix += 1
            dest_path = dest_path.with_name(f"{file_path.stem}_{suffix}{file_path.suffix}")

        if dest_path != file_path:
            try:
                shutil.move(str(file_path), str(dest_path))
                print(f"✅ Moved: {file_path.name} -> {target_category}")
            except Exception as e:
                print(f"⚠️ Failed to move {file_path.name}: {e}")

    # 5. Move the original empty/leftover folders into the Archive to completely clean the root
    original_folders = ["2. COVID_DOCUMENTS", "3. ADHAAR PAN VOTER", "4. PASSPORTS"]
    archive_folder = base_dir / "_Redundant_Archive"
    
    for folder_name in original_folders:
        folder_path = base_dir / folder_name
        if folder_path.exists():
            try:
                # If a folder with the same name exists in archive, merge/rename logic could be complex, 
                # so we just add an _old suffix to the folder name to be safe
                dest_folder_path = archive_folder / f"{folder_name}_old"
                shutil.move(str(folder_path), str(dest_folder_path))
                print(f"📁 Archived leftover folder structure: {folder_name}")
            except Exception as e:
                print(f"⚠️ Could not move folder {folder_name}: {e}")

    print("\n🎉 Cleanup complete! Zero files were deleted. All redundancy is now in the archive.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Safely clean and organize the Identity folder.")
    parser.add_argument("path", help="The absolute path to your 01_Identity_and_Family folder")
    
    args = parser.parse_args()
    clean_identity_folder(args.path)