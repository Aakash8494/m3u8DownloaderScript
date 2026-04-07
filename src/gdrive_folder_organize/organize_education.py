import os
import shutil
import argparse
from pathlib import Path

def organize_education_folder(target_dir):
    base_dir = Path(target_dir).resolve()
    
    if not base_dir.exists():
        print(f"❌ Error: The path '{base_dir}' does not exist.")
        return

    print(f"🚀 Starting Education organization for: {base_dir}\n")

    # 1. Define the new, clean folder structure
    new_folders = [
        "01_Schooling_10th_12th",
        "02_Bachelor_of_Engineering/Consolidated_and_Certificates",
        "02_Bachelor_of_Engineering/Semester_Wise",
        "_Redundant_Archive"
    ]
    
    for folder in new_folders:
        (base_dir / folder).mkdir(parents=True, exist_ok=True)

    # 2. Exact mapping: "Old file name (lowercase)" -> ("Target Folder", "Clean New File Name")
    clean_map = {
        "10th std ssc marksheet.pdf": ("01_Schooling_10th_12th", "10th_SSC_Marksheet.pdf"),
        "12th std hsc marksheet.pdf": ("01_Schooling_10th_12th", "12th_HSC_Marksheet.pdf"),
        "3. bachelor of engineering in information technology detailed marksheets and certificates.pdf": 
            ("02_Bachelor_of_Engineering/Consolidated_and_Certificates", "BE_IT_Detailed_Marksheets_and_Certificates.pdf"),
        "bachelor of engineering in information technology all_semester_consolidated_marksheet.pdf": 
            ("02_Bachelor_of_Engineering/Consolidated_and_Certificates", "BE_IT_All_Semester_Consolidated_Marksheet.pdf"),
        "bachelor of engineering in information technology degree_certificate.pdf": 
            ("02_Bachelor_of_Engineering/Consolidated_and_Certificates", "BE_IT_Degree_Certificate.pdf"),
        "bachelor of engineering in information technology fe_certificate.pdf": 
            ("02_Bachelor_of_Engineering/Consolidated_and_Certificates", "BE_IT_FE_Certificate.pdf"),
        "_________marks calculation.pdf": 
            ("02_Bachelor_of_Engineering/Consolidated_and_Certificates", "BE_IT_Marks_Calculation.pdf"),
        "sem 1.pdf": ("02_Bachelor_of_Engineering/Semester_Wise", "BE_IT_Semester_01.pdf"),
        "sem-2.pdf": ("02_Bachelor_of_Engineering/Semester_Wise", "BE_IT_Semester_02.pdf"),
        "sem-3.pdf": ("02_Bachelor_of_Engineering/Semester_Wise", "BE_IT_Semester_03.pdf"),
        "sem-4.pdf": ("02_Bachelor_of_Engineering/Semester_Wise", "BE_IT_Semester_04.pdf"),
        "sem-5.pdf": ("02_Bachelor_of_Engineering/Semester_Wise", "BE_IT_Semester_05.pdf"),
        "sem-6.pdf": ("02_Bachelor_of_Engineering/Semester_Wise", "BE_IT_Semester_06.pdf"),
        "sem-7.pdf": ("02_Bachelor_of_Engineering/Semester_Wise", "BE_IT_Semester_07.pdf"),
        "sem-8.pdf": ("02_Bachelor_of_Engineering/Semester_Wise", "BE_IT_Semester_08.pdf")
    }

    # 3. Collect all files (ignoring the new top-level folders we just made)
    all_files = []
    ignore_dirs = {"01_Schooling_10th_12th", "02_Bachelor_of_Engineering", "_Redundant_Archive"}
    
    for root, dirs, files in os.walk(base_dir):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for file in files:
            all_files.append(Path(root) / file)

    # 4. Process and Rename every file
    for file_path in all_files:
        name_lower = file_path.name.lower()
        
        # Check if this file is in our exact clean map
        if name_lower in clean_map:
            target_folder_name, clean_name = clean_map[name_lower]
            dest_folder = base_dir / target_folder_name
            dest_path = dest_folder / clean_name
        else:
            # If it's not a top-tier file we mapped, dump it in the archive
            dest_folder = base_dir / "_Redundant_Archive"
            dest_path = dest_folder / file_path.name

        # STRICT RULE: No overwrite. Handle collisions safely.
        if dest_path.exists() and dest_path != file_path:
            suffix = 1
            while dest_path.with_name(f"{dest_path.stem}_{suffix}{dest_path.suffix}").exists():
                suffix += 1
            dest_path = dest_path.with_name(f"{dest_path.stem}_{suffix}{dest_path.suffix}")

        if dest_path != file_path:
            try:
                shutil.move(str(file_path), str(dest_path))
                print(f"✅ Moved: {file_path.name} -> {dest_path.relative_to(base_dir)}")
            except Exception as e:
                print(f"⚠️ Failed to move {file_path.name}: {e}")

    # 5. Archive the old root folder to clean up the directory
    old_folder = base_dir / "2. RESULTS OF EXAM"
    if old_folder.exists():
        dest_folder_path = base_dir / "_Redundant_Archive" / "2. RESULTS OF EXAM_old"
        try:
            shutil.move(str(old_folder), str(dest_folder_path))
            print(f"📁 Archived old folder structure: 2. RESULTS OF EXAM")
        except Exception as e:
            pass

    print("\n🎉 Education organization complete! Files renamed cleanly, redundancy archived safely.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Safely organize and rename the Education folder.")
    parser.add_argument("path", help="The absolute path to your 03_Education_and_Academics folder")
    
    args = parser.parse_args()
    organize_education_folder(args.path)