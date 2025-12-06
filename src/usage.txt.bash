# dont forget to add {vid}
python downloader.py template \
  --template "https://video.acharyaprashant.org/dar-ka-saamna-kaise/dar-ka-saamna-kaise-video-{vid}/240p.m3u8" \
  --start 1 --end 20

python downloader.py list \
  --folder "असली युद्ध अपने विरुद्ध" \
  --url "https://video1.acharyaprashant.org/courses/2023-12-12/2019-12-21-sangharsh-part1-474b809/240p.m3u8" \
  --url "https://video1.acharyaprashant.org/courses/2023-12-12/2021-08-18-sangharsh-part2-f1f90c6/240p.m3u8" \
  --url "https://video1.acharyaprashant.org/courses/2023-12-12/2019-03-24-sangharsh-part3-996a2a6/240p.m3u8"

python downloader.py list --file urls.txt

# https://video.acharyaprashant.org/advait-vedanta-english-part-one/advait-vedanta-english-part-one-video-1/240p.m3u8
# https://video.acharyaprashant.org/dar-ka-saamna-kaise/dar-ka-saamna-kaise-video-1/240p.m3u8

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