python -m yt_dlp `
    -P "C:\Users\aakas\Downloads" `
    -f "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]/best" `
    --playlist-end 20 `
    --concurrent-fragments 4 `
    --download-archive archive.txt `
    -o "%(uploader)s/%(upload_date)s - %(title)s [%(id)s].%(ext)s" `
    --write-thumbnail `
    --embed-thumbnail `
    --convert-thumbnails jpg `
    --embed-metadata `
    "https://www.youtube.com/@archer2official"
# "https://www.youtube.com/@leonjhendrix"


