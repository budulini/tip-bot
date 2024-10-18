import youtube_dl

url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'  # Replace with the YouTube URL

ydl_opts = {'format': 'bestaudio'}
with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(url, download=False)
    print(info)

