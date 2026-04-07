import os
import shutil
import argparse
from pathlib import Path

def organize_career_folder(target_dir):
    base_dir = Path(target_dir).resolve()
    
    if not base_dir.exists():
        print(f"❌ Error: The path '{base_dir}' does not exist.")
        return

    print(f"🚀 Starting Career & Employment organization for: {base_dir}\n")

    # 1. Define Top-Level Folders
    companies = ["01_Nagarro", "02_Cognizant", "03_Zeki_Software"]
    special_folders = ["04_Misplaced_Education", "_Redundant_Archive"]
    
    # Define standard sub-folders for each company
    sub_categories = [
        "Payslips", 
        "Compensation_and_Tax", 
        "HR_Letters_and_FNF", 
        "Certificates_and_Policies",
        "Other"
    ]

    # Create the directory structure
    for folder in companies + special_folders:
        (base_dir / folder).mkdir(exist_ok=True)
        if folder in companies:
            for sub in sub_categories:
                (base_dir / folder / sub).mkdir(exist_ok=True)

    # 2. Collect all files (ignoring the new folders we just made)
    all_files = []
    ignore_dirs = set(companies + special_folders)
    
    for root, dirs, files in os.walk(base_dir):
        # Prevent walking into the new folders we just created
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for file in files:
            all_files.append(Path(root) / file)

    # Helper function to find a PDF twin for JPGs/DOCXs
    def has_pdf_twin(file_path):
        return file_path.with_suffix('.pdf').exists()

    # 3. Process every file
    for file_path in all_files:
        name_lower = file_path.name.lower()
        ext = file_path.suffix.lower()
        
        target_company = None
        target_sub = "Other"

        # --- REDUNDANCY CHECKS ---
        # If it's an archive file, or a duplicate docx/jpg that has a pdf twin, send to archive
        if ext in ['.zip', '.rar']:
            target_company = "_Redundant_Archive"
        elif ext in ['.jpg', '.docx'] and has_pdf_twin(file_path):
            target_company = "_Redundant_Archive"
        
        # --- COMPANY MATCHING ---
        if not target_company:
            if "nagarro" in name_lower or "3188107" in name_lower or "ctc compensation" in name_lower or "annual payslip" in name_lower:
                target_company = "01_Nagarro"
            elif "cognizant" in name_lower or "703078" in name_lower or "form12ba" in name_lower or "onecognizant" in name_lower:
                target_company = "02_Cognizant"
            elif "zeki" in name_lower or "salary slip(aakash" in name_lower:
                target_company = "03_Zeki_Software"
            elif any(k in name_lower for k in ["transcript", "marksheet", "convocation", "bachelors", "ielts", "semester"]):
                target_company = "04_Misplaced_Education"
                target_sub = "" # No subfolders for education yet
            else:
                # If we really can't guess, put it in archive so you can manually check it
                target_company = "_Redundant_Archive"

        # --- CATEGORY MATCHING (If it's going to a company folder) ---
        if target_company in companies:
            if "payslip" in name_lower or "salary slip" in name_lower:
                target_sub = "Payslips"
            elif any(k in name_lower for k in ["ctc", "form 16", "form16", "form12", "tax", "increment", "revision"]):
                target_sub = "Compensation_and_Tax"
            elif any(k in name_lower for k in ["offer", "relieving", "exp.", "experience", "appointment", "fnf", "separation"]):
                target_sub = "HR_Letters_and_FNF"
            elif any(k in name_lower for k in ["acceptable use", "code of ethics", "gender just", "global data", "misconduct"]):
                target_sub = "Certificates_and_Policies"

        # 4. Build final destination path
        if target_company in ["04_Misplaced_Education", "_Redundant_Archive"]:
            dest_folder = base_dir / target_company
        else:
            dest_folder = base_dir / target_company / target_sub
            
        dest_path = dest_folder / file_path.name

        # STRICT RULE: No overwrite. Handle collisions safely.
        if dest_path.exists() and dest_path != file_path:
            suffix = 1
            while dest_path.with_name(f"{file_path.stem}_{suffix}{file_path.suffix}").exists():
                suffix += 1
            dest_path = dest_path.with_name(f"{file_path.stem}_{suffix}{file_path.suffix}")

        if dest_path != file_path:
            try:
                shutil.move(str(file_path), str(dest_path))
                print(f"✅ Moved: {file_path.name} -> {target_company}/{target_sub if target_sub else ''}")
            except Exception as e:
                print(f"⚠️ Failed to move {file_path.name}: {e}")

    # 5. Archive the old, now-empty root folders
    old_folders = ["1. company documents", "1. Nagarro Documents", "1. ZEKI DOCUMENTS", "Cognizant", "eletters", "Nagarro payslips"]
    for folder_name in old_folders:
        folder_path = base_dir / folder_name
        if folder_path.exists():
            dest_folder_path = base_dir / "_Redundant_Archive" / f"{folder_name}_old"
            try:
                shutil.move(str(folder_path), str(dest_folder_path))
                print(f"📁 Archived old folder structure: {folder_name}")
            except Exception as e:
                pass

    print("\n🎉 Career organization complete! All files sorted and redundancy minimized safely.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Safely organize the Career folder.")
    parser.add_argument("path", help="The absolute path to your 02_Career_and_Employment folder")
    
    args = parser.parse_args()
    organize_career_folder(args.path)