import os
import re
import shutil
import argparse
from pathlib import Path

def clean_filename(filename):
    stem = Path(filename).stem
    ext = Path(filename).suffix.lower()

    # 1. Manual overrides for the absolute ugliest system-generated files
    overrides = {
        "30581_1564597104_0_payment_receipt_0011761600 ( payment receipt of first installment )": "HDFC_First_Installment_Receipt",
        "94268_1535658864_0_1326562159365_proposalform": "HDFC_Proposal_Form",
        "94268_1535658864_7_illustration-c2p3dp": "HDFC_Illustration_C2P3DP",
        "gram panchayat bill_pdf1_doc09_033_6835": "Grampanchayat_Bill",
        "receipt pavti doc556121000006204": "Grampanchayat_Receipt_Pavti",
        "shilpkala__bill_064[1]": "Shilpkala_Bill_064",
        "21153809 - entire policy": "HDFC_Entire_Policy",
        "mitc-638559337": "HDFC_MITC",
        "ofltr-638559337": "HDFC_Offer_Letter",
        "adobe scan 24 feb 2025": "Life_Republic_Scan_Feb_2025",
        "index 2": "Index_Document"
    }

    if stem.lower() in overrides:
        return overrides[stem.lower()] + ext

    # 2. General cleaning for everything else
    # Replace hyphens, underscores, and brackets with spaces
    clean_stem = re.sub(r'[\-\_\(\)\[\]]', ' ', stem)

    # Title case it (e.g., "pune gas bill" -> "Pune Gas Bill")
    clean_stem = clean_stem.title()

    # Remove extra spaces and join with underscores
    clean_stem = "_".join(clean_stem.split())

    # 3. Special rule: If it is just numbers (like the Kolte Patil receipts), prefix it
    if clean_stem.isdigit():
        clean_stem = f"Receipt_{clean_stem}"

    return clean_stem + ext

def rename_property_files(target_dir):
    base_dir = Path(target_dir).resolve()
    
    if not base_dir.exists():
        print(f"❌ Error: The path '{base_dir}' does not exist.")
        return

    print(f"🚀 Starting file renaming for: {base_dir}\n")

    # Collect all files, strictly ignoring the archive folder
    all_files = []
    for root, dirs, files in os.walk(base_dir):
        if "_Redundant_Archive" in dirs:
            dirs.remove("_Redundant_Archive") # Don't dive into the trash
            
        for file in files:
            all_files.append(Path(root) / file)

    # Process and Rename every file
    for file_path in all_files:
        clean_name = clean_filename(file_path.name)
        dest_path = file_path.parent / clean_name

        # Skip if the name is already perfect
        if dest_path == file_path:
            continue

        # STRICT RULE: No overwrite. Handle collisions safely.
        if dest_path.exists():
            suffix = 1
            while dest_path.with_name(f"{dest_path.stem}_{suffix}{dest_path.suffix}").exists():
                suffix += 1
            dest_path = dest_path.with_name(f"{dest_path.stem}_{suffix}{dest_path.suffix}")

        try:
            shutil.move(str(file_path), str(dest_path))
            print(f"✅ Renamed: '{file_path.name}' \n   -> '{dest_path.name}'\n")
        except Exception as e:
            print(f"⚠️ Failed to rename {file_path.name}: {e}")

    print("🎉 Renaming complete! Your files look like a developer actually owns them now.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean and rename files in the Property folder.")
    parser.add_argument("path", help="The absolute path to your 04_Property_and_Home folder")
    
    args = parser.parse_args()
    rename_property_files(args.path)