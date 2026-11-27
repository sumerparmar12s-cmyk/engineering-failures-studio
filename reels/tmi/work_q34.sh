cd /home/user/engineering-failures-studio/reels/tmi
for n in 3 4; do
 (cd comp && VW=1080 VH=1920 python3 reel_edit.py $n ../p$n/work/video.mp4 > ../p$n/work/render.log 2>&1 && VW=1080 VH=1920 python3 reel_audio.py $n ../p$n/work/audio.wav >> ../p$n/work/render.log 2>&1) && ffmpeg -v error -y -i p$n/work/video.mp4 -i p$n/work/audio.wav -map 0:v -map 1:a -c:v libx264 -preset medium -b:v 7M -maxrate 9M -bufsize 16M -c:a aac -b:a 192k -movflags +faststart out/TMI_Reel_Part$n.mp4 && echo "P$n DONE" >> p$n/work/render.log &
done
wait
