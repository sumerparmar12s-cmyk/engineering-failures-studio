#!/bin/bash
# rounded "window" layout: 1000x1250 window (cx offset 0-1) over a blurred, warm-tinted fill. args: src ss dur out cx
mk(){ ffmpeg -v error -y -i "$1" -ss $2 -t $3 -filter_complex "[0:v]setsar=1,scale=-2:1920,crop=1080:1920,boxblur=30:2,eq=brightness=-0.15:saturation=1.4[bg];[0:v]setsar=1,scale=-2:1250,crop=1000:1250:(iw-1000)*$5:0,eq=saturation=1.2:contrast=1.06,unsharp=5:5:0.5,format=rgba,geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='if(gt(hypot(max(0,abs(X-W/2)-(W/2-44)),max(0,abs(Y-H/2)-(H/2-44))),44),0,255)'[fg];[bg][fg]overlay=40:330,fps=30,format=yuv420p" -an -c:v libx264 -preset veryfast -crf 16 real/$4.mp4; echo $4; }
D=dl
mk $D/biscuit2025.mp4 10.3 8 blast 0.42 &
mk $D/newpool2026.mp4 0 6 newpool 0.12 &
mk $D/fumaroles.mp4 3 3 fumaroles 0.5 &
mk $D/grand.mp4 20 6.5 grand 0.5 &
wait
