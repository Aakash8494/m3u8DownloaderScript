import os
import shutil
import argparse
from pathlib import Path

def organize_property_folder(target_dir):
    base_dir = Path(target_dir).resolve()
    
    if not base_dir.exists():
        print(f"❌ Error: The path '{base_dir}' does not exist.")
        return

    print(f"🚀 Starting Property & Home organization for: {base_dir}\n")

    # 1. Define target folders
    target_folders = [
        "01_Pune_Flat_Life_Republic",
        "01_Pune_Flat_Life_Republic/Receipts",
        "02_HDFC_Home_Loan",
        "03_Grampanchayat_Taxes",
        "04_MNGL_Gas_Bills",
        "05_Family_Property_Agreements",
        "_Redundant_Archive"
    ]
    
    for folder in target_folders:
        (base_dir / folder).mkdir(parents=True, exist_ok=True)

    # 2. Collect all files (ignoring the new folders we just made)
    all_files = []
    ignore_dirs = {f.split('/')[0] for f in target_folders}
    
    for root, dirs, files in os.walk(base_dir):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for file in files:
            all_files.append(Path(root) / file)

    # 3. Process every file based on rules
    for file_path in all_files:
        name_lower = file_path.name.lower()
        path_str = str(file_path).lower()
        
        target_category = "_Redundant_Archive" # Default fallback

        # --- REDUNDANCY CHECKS ---
        # Catch all 108 raw scanner images (CCF09182024.png, etc.)
        if name_lower.startswith("ccf") and name_lower.endswith(".png"):
            target_category = "_Redundant_Archive"
        # Catch the "old" and "old2" evaluation folders
        elif "\\old\\" in path_str or "\\old2\\" in path_str:
            target_category = "_Redundant_Archive"
        # Catch the duplicate gas bills in the KYC folder (keeping only 'index 2.pdf' from it if needed)
        elif "pune gas bill kyc" in path_str and name_lower != "index 2.pdf":
            target_category = "_Redundant_Archive"

        # --- CATEGORY ROUTING ---
        elif "hdfc" in path_str:
            target_category = "02_HDFC_Home_Loan"
        elif "grampanchayat" in path_str:
            target_category = "03_Grampanchayat_Taxes"
        elif "gas bill" in path_str:
            target_category = "04_MNGL_Gas_Bills"
        elif "kolte patil" in path_str or "life republic" in path_str:
            if "receipts" in path_str:
                target_category = "01_Pune_Flat_Life_Republic/Receipts"
            else:
                target_category = "01_Pune_Flat_Life_Republic"
        elif any(k in path_str for k in ["agreement", "deed", "evaluation", "parel", "shilpkala"]):
            target_category = "05_Family_Property_Agreements"
        else:
            # Catch-all for anything left over
            target_category = "_Redundant_Archive"

        # 4. Execute the move safely
        dest_folder = base_dir / target_category
        dest_path = dest_folder / file_path.name

        # STRICT RULE: No overwrite. Add numbers to handle exact name matches safely.
        if dest_path.exists() and dest_path != file_path:
            suffix = 1
            while dest_path.with_name(f"{file_path.stem}_{suffix}{file_path.suffix}").exists():
                suffix += 1
            dest_path = dest_path.with_name(f"{file_path.stem}_{suffix}{file_path.suffix}")

        if dest_path != file_path:
            try:
                shutil.move(str(file_path), str(dest_path))
                # Only print the clean moves to keep terminal readable (skip spamming the 108 CCF moves)
                if target_category != "_Redundant_Archive":
                    print(f"✅ Moved: {file_path.name} -> {target_category}")
            except Exception as e:
                print(f"⚠️ Failed to move {file_path.name}: {e}")

    # 5. Archive the old empty root folders
    old_folders = [
        "5. Kolte Patil", "Deed of Transfer", "Gas bill", "Individual Agreement", 
        "Individual Agreement Dede", "Life republic ", "Property evaluation", 
        "PUNE FLAT DOCUMENTS", "PUNE GAS BILL KYC"
    ]
    for folder_name in old_folders:
        folder_path = base_dir / folder_name
        if folder_path.exists():
            dest_folder_path = base_dir / "_Redundant_Archive" / f"{folder_name.strip()}_old"
            try:
                shutil.move(str(folder_path), str(dest_folder_path))
                print(f"📁 Archived old folder structure: {folder_name}")
            except Exception as e:
                pass

    print("\n🎉 Property organization complete! All raw scans and duplicates archived safely.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Safely organize the Property folder.")
    parser.add_argument("path", help="The absolute path to your 04_Property_and_Home folder")
    
    args = parser.parse_args()
    organize_property_folder(args.path)