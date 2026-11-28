import subprocess, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); A = R + '/../tmi/audio/sfx'
END = 66.26
ev = [('braam', 0.0, 0.3), ('whoosh2', 0.9, 0.4), ('pop', 0.9, 0.35), ('rewind', 4.36, 0.35), ('stamp', 4.36, 0.3), ('riser', 5.7, 0.25), ('hit', 7.62, 0.45), ('swell', 7.72, 0.3), ('whoosh', 8.76, 0.45), ('pop', 12.1, 0.3), ('pop', 14.32, 0.3), ('ding', 16.5, 0.35), ('whoosh2', 17.56, 0.4), ('tick', 17.66, 0.4), ('tick', 19.04, 0.4), ('pop', 20.36, 0.3), ('whoosh', 21.46, 0.4), ('splash', 23.72, 0.4), ('pop', 26.76, 0.3), ('whoosh2', 28.8, 0.4), ('splash', 30.58, 0.35), ('pop', 33.32, 0.3), ('rewind', 35.8, 0.35), ('whoosh', 36.9, 0.45), ('braam', 37.1, 0.35), ('explosion_big', 37.85, 0.35), ('boom', 37.85, 0.3), ('whoosh2', 38.14, 0.4), ('pop', 39.22, 0.35), ('pop', 41.16, 0.35), ('pop', 44.86, 0.35), ('whoosh', 47.33, 0.45), ('ding', 48.44, 0.35), ('thud', 52.72, 0.4), ('pop', 55.76, 0.3), ('whoosh2', 57.16, 0.4), ('hit', 59.44, 0.45), ('riser', 62.3, 0.4), ('braam', 63.9, 0.5), ('hit', 63.9, 0.45)]
trim = {}
BEDS = []
CUSTOM = [('flow.wav', 2.64, 25.66, 0.35), ('flow.wav', 29.0, 37.1, 0.25), ('projector.wav', 47.33, 57.16, 0.5)]
inp = ['-i', R + '/vo/vo.mp3', '-ss', '0', '-t', str(END), '-i', R + '/audio/music.mp3']
fc = [f"[0:a]apad=whole_dur={END},asplit=3[vo][sc][sc2]", f"[1:a]aresample=44100,volume=0.30,afade=t=in:d=0.3,afade=t=out:st={END-1.6}:d=1.6[m]",
      "[m][sc]sidechaincompress=threshold=0.04:ratio=6:attack=10:release=300[md]"]
el = []
for i, (nm, t, v) in enumerate(ev):
    inp += ['-i', f'{A}/{nm}.wav']; tr = trim.get((nm, t)); cut = f"atrim=0:{tr},afade=t=out:st={tr-0.4}:d=0.4," if tr else ''
    fc.append(f"[{i+2}:a]aresample=44100,{cut}volume={v*0.45:.3f},adelay={int(t*1000)}|{int(t*1000)}[s{i}]"); el.append(f'[s{i}]')
for j, (a0, b0) in enumerate(BEDS):
    inp += ['-stream_loop', '-1', '-i', R + '/audio/hooves.wav']; n = len(inp) // 2 - 1
    fc.append(f"[{2 + len(ev) + j}:a]aresample=44100,atrim=0:{b0 - a0},afade=t=in:d=0.3,afade=t=out:st={b0 - a0 - 0.4}:d=0.4,volume=0.16,adelay={int(a0 * 1000)}|{int(a0 * 1000)}[h{j}]"); el.append(f'[h{j}]')
for j, (fn, a0, b0, v0) in enumerate(CUSTOM):
    inp += ['-stream_loop', '-1', '-i', R + '/audio/' + fn]
    fc.append(f"[{2 + len(ev) + len(BEDS) + j}:a]aresample=44100,aformat=channel_layouts=stereo,atrim=0:{b0 - a0},afade=t=out:st={max(0, b0 - a0 - 0.15)}:d=0.15,volume={v0},adelay={int(a0 * 1000)}|{int(a0 * 1000)}[cu{j}]"); el.append(f'[cu{j}]')
fc.append(''.join(el) + f"amix=inputs={len(el)}:duration=longest:normalize=0[sfx]")
fc.append("[sfx][sc2]sidechaincompress=threshold=0.05:ratio=4:attack=5:release=250[sfxd]")
fc.append("[vo][md][sfxd]amix=inputs=3:duration=longest:normalize=0,loudnorm=I=-14:TP=-1.5,alimiter=limit=0.84:level=false[a]")
subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inp + ['-filter_complex', ';'.join(fc), '-map', '[a]', '-t', str(END), '-ar', '48000', '-ac', '2', R + '/work/audio.wav'], check=True)
print('audio ok')
