# خيط الضوء: إعلان الإنترنت الهوائي لمركز مكة للتقنيات، حمص

- `video/makkah-wireless-reel.mp4`: الفيديو النهائي (ريلز 9:16، 1080×1920، 35 ثانية، موسيقى بدون صوت بشري)
- `bible/index.html`: ملف الإنتاج والستوري بورد
- `video/index.html`: مشاهد الأنيميشن (كل إطار يُرسم من `render(t)`)
- `video/audio.py`: تأليف الموسيقى والمؤثرات (`assets/score.wav`)
- `video/render.js`: تصدير الفيديو

## إعادة التصدير
```bash
cd video
python3 audio.py
NODE_PATH=$(npm root -g) node render.js assets/video_silent.mp4 30 0 35
ffmpeg -y -i assets/video_silent.mp4 -i assets/score.wav -c:v copy -af "loudnorm=I=-14:TP=-1:LRA=9" -c:a aac -b:a 256k -ar 48000 -shortest -movflags +faststart makkah-wireless-reel.mp4
```
