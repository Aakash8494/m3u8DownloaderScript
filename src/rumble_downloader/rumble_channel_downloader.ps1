python -m yt_dlp `
    -f "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]/best" `
    --playlist-end 60 `
    --concurrent-fragments 4 `
    --download-archive rajneesh_archive.txt `
    -o "%(uploader)s/%(upload_date)s - %(title)s [%(id)s].%(ext)s" `
    --embed-thumbnail `
    --embed-metadata `
    "https://www.youtube.com/@ytRajneeshyt"