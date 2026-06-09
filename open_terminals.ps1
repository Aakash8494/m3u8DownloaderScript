# open_terminals.ps1

# Terminal 1
Start-Process powershell -ArgumentList "-NoExit -Command `"cd .\src\transcribe_mp3; & C:\m3u8\venv\Scripts\Activate.ps1`""

# Terminal 2
Start-Process powershell -ArgumentList "-NoExit -Command `"cd .\src\youtube_transcript_download; & C:\m3u8\venv\Scripts\Activate.ps1`""

# Terminal 3
Start-Process powershell -ArgumentList "-NoExit -Command `"cd .\src\video_to_audio; & C:\m3u8\venv\Scripts\Activate.ps1`""