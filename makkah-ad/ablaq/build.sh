#!/bin/bash
# Renders the 36.67s film in 4 parallel segments, joins them, muxes the score, and makes a phone-size copy.
cd "$(dirname "$0")"
pgrep -f "http.server 8739" >/dev/null || (python3 -m http.server 8739 --bind 127.0.0.1 >/dev/null 2>&1 &)
sleep 1; mkdir -p seg; export NODE_PATH=$(npm root -g)
T=(0 9.2 18.4 27.5 36.67)
for i in 0 1 2 3; do node render.js seg/s$i.mp4 30 ${T[$i]} ${T[$((i+1))]} > seg/log$i.txt 2>&1 & done
wait
printf "file 's0.mp4'\nfile 's1.mp4'\nfile 's2.mp4'\nfile 's3.mp4'\n" > seg/list.txt
ffmpeg -y -loglevel error -f concat -safe 0 -i seg/list.txt -c copy assets/video_silent.mp4 &&
ffmpeg -y -loglevel error -i assets/video_silent.mp4 -i assets/mix.wav -c:v copy -c:a aac -b:a 256k -shortest -movflags +faststart makkah-ablaq-reel.mp4 &&
ffmpeg -y -loglevel error -i makkah-ablaq-reel.mp4 -c:v libx264 -preset slow -crf 24 -maxrate 2000k -bufsize 4000k -pix_fmt yuv420p -c:a aac -b:a 128k -movflags +faststart makkah-ablaq-reel-mobile.mp4
ls -la *.mp4; grep -h "ERR\|page:" seg/log*.txt | head -5; echo BUILD_DONE
