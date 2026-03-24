import sys
from faster_whisper import WhisperModel

# Get audio path from command line
audio_path = sys.argv[1]

model = WhisperModel("large-v3")

segments, info = model.transcribe(audio_path)

for segment in segments:
    print(segment.text)