@echo off

if "%1"=="" goto no_param
if "%2"=="" goto one_param 
goto two_param

:no_param
set /p start=start:
set /p end=end:
goto yt-dlp

:one_param
set start=%~1
set end=%~1
goto yt-dlp

:two_param
set start=%~1
set end=%~2
goto yt-dlp

:yt-dlp
yt-dlp -I %start%:%end% --lazy-playlist -P C:\Users\ACER\Music -o "%%(title)s.%%(ext)s" --no-write-playlist-metafiles ^
-f ba --write-subs --sub-format "best" --sub-langs "en.*,zh.*,ja" -x --audio-quality 0 --embed-thumbnail ^
--embed-metadata --no-add-chapters --convert-subs lrc --sponsorblock-remove intro,outro,music_offtopic ^
--no-overwrites https://www.youtube.com/playlist?list=PL_fjS67M7JRdaw9GD4CG7OjBCchTMdBAT
