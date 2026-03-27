import os
import time
import argparse
import google.generativeai as genai
from docx import Document
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Retrieve your API Key safely
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not found. Please ensure your .env file is set up correctly.")
    exit(1)

genai.configure(api_key=api_key)

# Initialize the updated, active model 
model = genai.GenerativeModel('gemini-2.5-flash')

# Define the Prompt 
PROMPT = """
You are an expert audio transcriber, strict text formatter, and translator. I have provided an MP3 audio file containing speech in either Hindi or English.

If the spoken audio is in Hindi, transcribe and transliterate it directly into Hinglish (Hindi words written using the English alphabet). If the spoken audio is in English, transcribe it exactly in English.
You must transcribe the exact spoken words. Do NOT add, delete, summarize, or skip a single spoken word from the audio. It must be a 100% word-for-word verbatim transcription of the speaker.

Since the audio lacks visible punctuation, you must deduce and add periods (full stops) where sentences naturally end based on the speaker's pauses and intonation. Always capitalize the first letter of the word immediately following a period.

Break the continuous transcription down into readable paragraphs of roughly 150 to 200 words. Additionally, if the speaker takes a significant pause or clearly transitions to a new topic, start a new paragraph.

Create a short, appropriate title/heading for every single paragraph based on what that section of the audio is about. Place the title right above its matching paragraph.

Find the most important keywords, phrases, or main ideas inside each transcribed paragraph and make them bold to make it easier to read.

Return only the final formatted transcription. Do not add any extra introductory or concluding sentences before or after the text.
"""

def process_and_merge_mp3s(folder_path, output_filename):
    folder_path = os.path.abspath(folder_path)

    if not os.path.isdir(folder_path):
        print(f"Error: The directory {folder_path} does not exist.")
        return

    mp3_files = sorted([f for f in os.listdir(folder_path) if f.lower().endswith('.mp3')])
    
    if not mp3_files:
        print(f"No MP3 files found in {folder_path}.")
        return

    print(f"Found {len(mp3_files)} MP3 file(s) in {folder_path}. Starting processing...\n")

    # Create a completely fresh master document from scratch
    master_doc = Document()

    for i, filename in enumerate(mp3_files):
        file_path = os.path.join(folder_path, filename)
        print(f"Uploading and processing: {filename}...")

        try:
            # 1. Upload the audio file to the Gemini API
            audio_file = genai.upload_file(path=file_path)
            
            while audio_file.state.name == "PROCESSING":
                print(".", end="", flush=True)
                time.sleep(2)
                audio_file = genai.get_file(audio_file.name)
            print(" Upload complete.")

            # 2. Generate the transcription
            print("Generating transcription...")
            response = model.generate_content([PROMPT, audio_file])
            raw_text = response.text

            # 3. Format and apply to BOTH individual and master documents
            print("Formatting documents...")
            
            # Create a completely fresh document for this specific MP3
            individual_doc = Document()
            
            # Add a clear separator for the new audio file in the master document
            master_doc.add_heading(f"Source: {filename}", level=1)
            
            # Split the raw text by hidden line breaks
            lines = raw_text.split('\n')
            
            for line in lines:
                text = line.strip()
                if not text:
                    continue # Skip empty lines
                    
                # Handle Headings for both docs
                if text.startswith("### "):
                    clean_text = text[4:].strip()
                    individual_doc.add_heading(clean_text, level=3)
                    master_doc.add_heading(clean_text, level=3)
                elif text.startswith("## "):
                    clean_text = text[3:].strip()
                    individual_doc.add_heading(clean_text, level=2)
                    master_doc.add_heading(clean_text, level=2)
                elif text.startswith("# "):
                    clean_text = text[2:].strip()
                    individual_doc.add_heading(clean_text, level=1)
                    master_doc.add_heading(clean_text, level=1)
                
                # Handle Normal Paragraphs and Bold Text for both docs
                else:
                    ind_para = individual_doc.add_paragraph()
                    mast_para = master_doc.add_paragraph()
                    
                    parts = text.split("**")
                    
                    for idx, part in enumerate(parts):
                        if part: 
                            ind_run = ind_para.add_run(part)
                            mast_run = mast_para.add_run(part)
                            # Odd indexes were wrapped in **
                            if idx % 2 != 0:
                                ind_run.bold = True
                                mast_run.bold = True

            # Save the individual file
            individual_filename = f"{os.path.splitext(filename)[0]}_transcribed.docx"
            individual_path = os.path.join(folder_path, individual_filename)
            individual_doc.save(individual_path)
            print(f"  Saved individual doc: {individual_filename}")

            # Add an empty line spacing between different audio files in the master doc
            if i < len(mp3_files) - 1:
                master_doc.add_paragraph()

            # Clean up the file from Google's servers
            audio_file.delete()
            print("  Done.\n")

        except Exception as e:
            print(f"\nAn error occurred while processing {filename}: {e}\n")

    # 4. Save the final compiled master document
    output_path = os.path.join(folder_path, output_filename)
    master_doc.save(output_path)
    print(f"Success! Master document compiled and saved to: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcribe MP3 files into individual formatted Word docs AND a compiled master doc.")
    parser.add_argument("folder_path", type=str, nargs='?', default=".", help="Path to the folder containing your MP3 files.")
    parser.add_argument("--output", type=str, default="Master_Transcriptions.docx", help="Name of the final compiled master file.")
    
    args = parser.parse_args()
    process_and_merge_mp3s(args.folder_path, args.output)