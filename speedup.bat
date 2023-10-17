for %%f in (.\*.mkv) do (
    "ffmpeg/ffmpeg" -n -i "%%f" -filter:v "setpts=PTS/60" -an -b:v 4000k "%%~nf (60x).mp4"
)
pause