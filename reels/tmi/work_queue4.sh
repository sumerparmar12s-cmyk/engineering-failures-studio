cd /home/user/engineering-failures-studio/reels/tmi
while ! grep -q "P3 DONE" p3/work/render.log 2>/dev/null; do sleep 10; done
cd comp && VW=1080 VH=1920 python3 reel_edit.py 4 ../p4/work/video.mp4 > ../p4/work/render.log 2>&1 && VW=1080 VH=1920 python3 reel_audio.py 4 ../p4/work/audio.wav >> ../p4/work/render.log 2>&1 && cd .. && ffmpeg -v error -y -i p4/work/video.mp4 -i p4/work/audio.wav -map 0:v -map 1:a -c:v libx264 -preset medium -b:v 7M -maxrate 9M -bufsize 16M -c:a aac -b:a 192k -movflags +faststart out/TMI_Reel_Part4.mp4 && echo P4 DONE >> p4/work/render.log
