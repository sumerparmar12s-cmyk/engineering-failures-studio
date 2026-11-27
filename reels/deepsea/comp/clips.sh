#!/bin/bash
mk(){ ffmpeg -v error -y -i "$1" -ss $2 -t $3 -filter_complex "[0:v]setsar=1,scale=-2:1920,crop=1080:1920,boxblur=26:2,eq=brightness=-0.08:saturation=1.3[bg];[0:v]setsar=1,scale=-2:$5,crop='min(iw,1080)':$5,eq=saturation=1.15:contrast=1.05,unsharp=5:5:0.5[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2-40,fps=30,format=yuv420p" -an -c:v libx264 -preset veryfast -crf 16 real/$4.mp4; echo $4; }
D=dl
mk $D/glass.mp4 22 6 glass_front 1240 &
mk $D/glass.mp4 13 4.5 glass_side 1240 &
mk $D/dumbo_nc.mp4 3 5 dumbo_red 1240 &
mk $D/casper.mp4 3 5 casper_wide 1240 &
mk $D/casper.mp4 29 4 casper_close 1240 &
mk $D/dumbo_kw.mp4 24 4.5 dumbo_blob 1240 &
wait
