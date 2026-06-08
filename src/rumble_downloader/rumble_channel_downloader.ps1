python -m yt_dlp `
    -P "C:\Users\aakas\Downloads" `
    -f "bestvideo[height<=480]+bestaudio/best[height<=480]/best" `
    --merge-output-format mkv `
    --playlist-end 40 `
    --concurrent-fragments 4 `
    --download-archive archive.txt `
    -o "%(uploader)s/%(upload_date)s - %(title)s [%(id)s].%(ext)s" `
    --embed-thumbnail `
    --convert-thumbnails jpg `
    --embed-metadata `
    "https://www.youtube.com/@epicmotivation6668"
# "https://www.youtube.com/@IronWilll2026"
# "https://www.youtube.com/@archer2official"
# "https://www.youtube.com/@leonjhendrix"
# "https://www.youtube.com/@ZeroDopamineWorld/popular"


python -m yt_dlp `
    -P "C:\Users\aakas\Downloads" `
    -f "bestvideo[height<=480]+bestaudio/best[height<=480]/best" `
    --merge-output-format mkv `
    --playlist-end 20 `
    --concurrent-fragments 4 `
    --download-archive archive.txt `
    -o "%(uploader)s/%(upload_date)s - %(title)s [%(id)s].%(ext)s" `
    --embed-thumbnail `
    --convert-thumbnails jpg `
    --embed-metadata `
    "https://rumble.com/playlists/f-Ue_cRBhOs"


"https://www.youtube.com/@ZeroDopamineWorld/popular"


python -m yt_dlp `
    -P "C:\Users\aakas\Downloads" `
    -f "bestvideo[height<=360]+bestaudio/best[height<=360]/worst" `
    --merge-output-format mkv `
    --concurrent-fragments 4 `
    --download-archive archive.txt `
    -o "%(uploader)s/%(upload_date)s - %(title)s [%(id)s].%(ext)s" `
    --embed-thumbnail `
    --convert-thumbnails jpg `
    --embed-metadata `
    -a rumble_links.txt

