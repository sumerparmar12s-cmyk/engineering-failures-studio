#!/bin/bash
# full-bleed vertical crops with false-colour "thermal" palette. args: src ss dur out preset cropx(0-1) scale
mk(){ ffmpeg -v error -y -i "$1" -ss $2 -t $3 -vf "setsar=1,scale=-2:$7,crop=1080:1920:(iw-1080)*$6:(ih-1920)/2,format=gray,format=yuv444p,pseudocolor=preset=$5,eq=contrast=1.05,fps=30,format=yuv420p" -an -c:v libx264 -preset veryfast -crf 16 real/$4.mp4; echo $4; }
D=dl
mk $D/gofast.mp4 1 5.5 gf_a turbo 0.5 2120 &
mk $D/gofast.mp4 22 7 gf_b inferno 0.5 2120 &
mk $D/D111689133.mp4 0 2.2 rel_jet magma 0.5 1920 &
mk $D/D111688954.mp4 18 3.5 rel_orb plasma 0.5 1920 &
mk $D/D111688964.mp4 2 2 rel_sea viridis 0.5 1920 &
mk $D/D111689759.mp4 1 2.5 rel_end inferno 0.5 1920 &
wait
