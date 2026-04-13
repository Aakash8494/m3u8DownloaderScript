import argparse
from pathlib import Path
from docx import Document

def extract_to_single_column(input_path: Path):
    print(f"Reading document: {input_path.name}...")
    
    try:
        doc = Document(input_path)
    except Exception as e:
        print(f"Error opening document: {e}")
        return

    # 1. Create the new document and table
    new_doc = Document()
    new_doc.add_heading(f'Extracted: {input_path.stem}', level=1)
    
    # Create a table with 0 rows (we will add them dynamically) and 1 column
    table = new_doc.add_table(rows=0, cols=1)
    table.style = 'Table Grid' 

    blocks_processed = 0

    # 2. Process every single paragraph one by one
    for para in doc.paragraphs:
        if not para.text.strip():
            continue # Skip blank lines

        # Add a new row for this specific paragraph/title
        row = table.add_row()
        cell = row.cells[0]
        
        # Word tables always put an empty paragraph in a new cell by default
        new_para = cell.paragraphs[0]
        
        # 3. Attempt to preserve the paragraph's overall style (like 'Heading 3' or 'Normal')
        try:
            new_para.style = para.style.name
        except KeyError:
            pass # Fallback to standard text if the new blank doc doesn't have that specific style

        # 4. Copy the text chunk-by-chunk (Run-by-Run) to preserve BOLD formatting
        for run in para.runs:
            if run.text:
                new_run = new_para.add_run(run.text)
                new_run.bold = run.bold
                new_run.italic = run.italic
                # You can also add new_run.underline = run.underline here if needed

        blocks_processed += 1

    print(f"Processed {blocks_processed} individual blocks into the single-column table.")

    # 5. Generate dynamic output path and save
    output_path = input_path.parent / f"{input_path.stem}_SingleCol{input_path.suffix}"
    
    new_doc.save(output_path)
    print(f"\n✅ Success! Saved formatted table to:\n📁 {output_path}")

if __name__ == "__main__":
    # Setup Command Line Interface
    parser = argparse.ArgumentParser(description="Convert Word doc into a 1-column table while preserving bold text.")
    parser.add_argument("filepath", type=str, help="Full path to the .docx file")
    
    args = parser.parse_args()
    
    # Clean the path
    clean_path_str = args.filepath.strip('"').strip("'")
    input_path = Path(clean_path_str).resolve()
    
    # Validate the file
    if not input_path.exists():
        print(f"❌ Error: Could not find file at '{input_path}'")
    elif input_path.suffix.lower() != '.docx':
        print(f"❌ Error: The file must be a standard Word Document (.docx). You provided: '{input_path.suffix}'")
    else:
        extract_to_single_column(input_path)