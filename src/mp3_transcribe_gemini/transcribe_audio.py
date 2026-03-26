import os
import time
import argparse
import google.generativeai as genai
from docx import Document
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# 1. Retrieve your API Key safely
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not found. Please ensure your .env file is set up correctly.")
    exit(1)

genai.configure(api_key=api_key)

# Initialize the model 
model = genai.GenerativeModel('gemini-2.5-flash')

# 2. Define the Prompt 
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

def process_mp3_files(folder_path, template_path):
    # Ensure paths are absolute or correctly resolved
    folder_path = os.path.abspath(folder_path)
    template_path = os.path.abspath(template_path)

    if not os.path.exists(template_path):
        print(f"Error: Template file not found at {template_path}")
        return

    if not os.path.isdir(folder_path):
        print(f"Error: The directory {folder_path} does not exist.")
        return

    mp3_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.mp3')]
    
    if not mp3_files:
        print(f"No MP3 files found in {folder_path}.")
        return

    print(f"Found {len(mp3_files)} MP3 file(s) in {folder_path}. Starting processing...\n")

    for filename in mp3_files:
        file_path = os.path.join(folder_path, filename)
        print(f"Uploading and processing: {filename}...")

        try:
            # 3. Upload the audio file to the Gemini API
            audio_file = genai.upload_file(path=file_path)
            
            while audio_file.state.name == "PROCESSING":
                print(".", end="", flush=True)
                time.sleep(2)
                audio_file = genai.get_file(audio_file.name)
            print(" Upload complete.")

            # 4. Generate the transcription
            print("Generating transcription...")
            response = model.generate_content([PROMPT, audio_file])
            transcription_text = response.text

            # 5. Write to the Word Document Template
            doc = Document(template_path)
            doc.add_paragraph(transcription_text)
            
            output_filename = f"{os.path.splitext(filename)[0]}_transcribed.docx"
            output_path = os.path.join(folder_path, output_filename)
            doc.save(output_path)
            
            print(f"Success! Saved to {output_path}\n")

            audio_file.delete()

        except Exception as e:
            print(f"\nAn error occurred while processing {filename}: {e}\n")

if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Transcribe MP3 files in a folder and save them to Word documents.")
    
    # Required argument: The folder containing the MP3s
    parser.add_argument("folder_path", type=str, help="Path to the folder containing your MP3 files.")
    
    # Optional argument: The template file (defaults to 'template.docx' in the current directory)
    parser.add_argument("--template", type=str, default="template.docx", help="Path to your Word template file (default: template.docx).")
    
    args = parser.parse_args()
    
    process_mp3_files(args.folder_path, args.template)