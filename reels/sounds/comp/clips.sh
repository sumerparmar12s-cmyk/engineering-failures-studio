#!/bin/bash
# top-panel layout: footage fills 1080x1150 at top, rest black (lab panel drawn later). args: src ss dur out cx
mk(){ ffmpeg -v error -y -i "$1" -ss $2 -t $3 -vf "setsar=1,scale=-2:1150,crop=1080:1150:(iw-1080)*$5:0,eq=saturation=1.2:contrast=1.05,pad=1080:1920:0:0:black,fps=30,format=yuv420p" -an -c:v libx264 -preset veryfast -crf 16 real/$4.mp4; echo $4; }
D=dl
mk $D/forest.mp4 5 5.2 ocean_a 0.5 &
mk $D/forest.mp4 30 4.2 ocean_b 0.5 &
mk $D/pig.mp4 0.3 2.2 ice_a 0.35 &
mk $D/pig.mp4 11.2 1.6 ice_b 0.4 &
mk $D/mars_audio.mp4 9 5 mars 0.5 &
wait
