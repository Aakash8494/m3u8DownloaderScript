# dont forget to add {vid}
python downloader.py template \
  --template "https://video.acharyaprashant.org/jesus-english/jesus-english-video-{vid}/240p.m3u8" \
  --start 1 --end 20

python downloader.py list \
  --url "" \
  --url ""

python downloader.py list --file urls.txt


#example {vid}
# python downloader.py template \
#   --template "https://video.acharyaprashant.org/love-and-lust/love-and-lust-video-{vid}/240p.m3u8" \
#   --start 1 --end 20

	
# python downloader.py template \
#   --template "https://video.acharyaprashant.org/prem-aur-hawas/prem-aur-hawas-video-{vid}/240p.m3u8" \
#   --start 1 --end 20

# python downloader.py template \
#   --template "https://video.acharyaprashant.org/jesus-english/jesus-english-video-{vid}/240p.m3u8" \
#   --start 1 --end 20 