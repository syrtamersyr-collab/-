#!/bin/bash
# Renders the 36s film in 4 parallel segments, joins them, and muxes the sound-effects track.
cd "$(dirname "$0")"
pgrep -f "http.server 8731" >/dev/null || (python3 -m http.server 8731 --bind 127.0.0.1 >/dev/null 2>&1 &)
sleep 1; mkdir -p seg; export NODE_PATH=$(npm root -g)
for i in 0 1 2 3; do node render.js seg/s$i.mp4 30 $((i*9)) $((i*9+9)) > seg/log$i.txt 2>&1 & done
wait
printf "file 's0.mp4'\nfile 's1.mp4'\nfile 's2.mp4'\nfile 's3.mp4'\n" > seg/list.txt
ffmpeg -y -loglevel error -f concat -safe 0 -i seg/list.txt -c copy assets/video_silent.mp4 &&
ffmpeg -y -loglevel error -i assets/video_silent.mp4 -i assets/score.wav -c:v copy -af "loudnorm=I=-16:TP=-1:LRA=11" -c:a aac -b:a 256k -ar 48000 -shortest -movflags +faststart makkah-3d-reel.mp4
ffprobe -v error -show_entries format=duration,size -of compact makkah-3d-reel.mp4; grep -h "ERR\|page:" seg/log*.txt | head -5; echo BUILD_EXIT $?
