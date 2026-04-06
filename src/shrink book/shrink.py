import os
import glob
import docx
from docx.shared import Pt

def clean_and_move_doc(input_filepath):
    # Ensure we have the absolute path
    input_filepath = os.path.abspath(input_filepath)
    filename = os.path.basename(input_filepath)
    print(f"\n--- Processing: {filename} ---")
    
    try:
        doc = docx.Document(input_filepath)
    except Exception as e:
        print(f"Error opening document {filename}: {e}")
        return

    empty_paragraph_count = 0
    
    # --- 1. CLEAN THE DOCUMENT SPACING ---
    for paragraph in list(doc.paragraphs):
        
        # Remove manual page breaks
        for run in paragraph.runs:
            page_breaks = run._element.xpath('.//w:br[@w:type="page"]')
            for pb in page_breaks:
                pb.getparent().remove(pb)
                
        # Turn off "Page Break Before" and standardize line spacing
        paragraph.paragraph_format.page_break_before = False
        paragraph.paragraph_format.space_before = Pt(0)
        paragraph.paragraph_format.space_after = Pt(6)
        
        # Remove empty paragraphs
        if not paragraph.text.strip():
            empty_paragraph_count += 1
            if empty_paragraph_count > 0: 
                p_element = paragraph._element
                p_element.getparent().remove(p_element)
        else:
            empty_paragraph_count = 0

    # --- 2. HANDLE FOLDERS AND FILES ---
    base_dir = os.path.dirname(input_filepath)
    
    # Create the 'shrinked' directory in the same folder as the script/files
    shrinked_dir = os.path.join(base_dir, 'shrinked')
    os.makedirs(shrinked_dir, exist_ok=True)
    
    # Define the new file path inside the 'shrinked' folder
    output_filepath = os.path.join(shrinked_dir, filename)
    
    # Save the cleaned document
    doc.save(output_filepath)
    print(f"Saved cleaned version to: shrinked/{filename}")
    
    # Delete the original file
    try:
        os.remove(input_filepath)
        print(f"Deleted original file: {filename}")
    except Exception as e:
        print(f"Warning: Could not delete the original file. Error: {e}")


# --- Run the Batch Script ---
if __name__ == "__main__":
    print("Searching for .docx files in the current directory...")
    
    # Find all .docx files in the folder where the script is located
    # This automatically ignores files already moved into the 'shrinked' subfolder
    docx_files = glob.glob("*.docx")
    
    # Filter out temporary Word files (they start with "~$")
    valid_files = [f for f in docx_files if not f.startswith("~$")]
    
    if not valid_files:
        print("No valid Word documents (.docx) found in this directory.")
    else:
        print(f"Found {len(valid_files)} document(s). Starting cleanup...")
        
        # Loop through every file and run the cleaning function
        for file in valid_files:
            clean_and_move_doc(file)
            
        print("\nAll documents processed successfully!")