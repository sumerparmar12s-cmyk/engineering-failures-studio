#!/bin/bash
# portrait 1080x1920 clips: sharp foreground band over blurred fill. args: src ss dur out fgh [eqopts]
mk(){ ffmpeg -v error -y -i "$1" -ss $2 -t $3 -filter_complex "[0:v]setsar=1,scale=-2:1920,crop=1080:1920,boxblur=24:2,eq=brightness=-0.12[bg];[0:v]setsar=1,scale=-2:$5,crop='min(iw,1080)':$5,unsharp=5:5:0.6[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2-60,fps=30,format=yuv420p" -an -c:v libx264 -preset veryfast -crf 16 real/$4.mp4; echo $4; }
D=dl
mk $D/tacoma_cep176.mpg 63 10 t_center 1240
mk $D/tacoma_cep176.mpg 22 9 t_road 1240
mk $D/tacoma_cep176.mpg 55 8 t_side 1100
mk $D/tacoma_cep176.mpg 73.3 6 t_tilt 1240
mk $D/tacoma_cep176.mpg 108 17 t_fall 1240
mk $D/tacoma_cep176.mpg 78 9 t_far 1240
