"""Audio-only remix (same graph as assemble.py) with extra music/SFX gain, voice-vs-background measurement, and mux onto out/final.mp4.
usage: remix.py MUSIC_K SFX_K [--mux]"""
import json, subprocess, sys, os, numpy as np
P = os.path.dirname(os.path.abspath(__file__)); D = json.load(open(f'{P}/shots.json')); END = D['end']
MK, SK = float(sys.argv[1]), float(sys.argv[2])
SOLO = [(19.87, 22.87), (221.49, 224.89), (229.98, 232.38), (268.02, 270.62), (497.31, 501.51)]
def graph(stem):
    inputs, fc = [], []; idx = 0
    def ain(path, extra=None):
        nonlocal idx; inputs.extend((extra or []) + ['-i', path]); idx += 1; return idx - 1
    vo = ain(f'{P}/vo/vo.mp3'); fc.append(f"[{vo}:a]asplit=2[vo][sc]")
    ml = []
    for i, m in enumerate(D['music']):
        dur = min(m['dur'], END - m['start']); j = ain(f"{P}/{m['file']}", ['-ss', str(m.get('ss', 0)), '-t', str(dur)])
        fc.append(f"[{j}:a]volume={m['vol'] * MK:.4f},afade=t=in:st=0:d=1.2,afade=t=out:st={max(0, dur - 1.8):.2f}:d=1.8,adelay={int(m['start'] * 1000)}|{int(m['start'] * 1000)}[m{i}]"); ml.append(f'[m{i}]')
    fc.append(''.join(ml) + f"amix=inputs={len(ml)}:duration=longest:normalize=0[mus]")
    fc.append("[mus][sc]sidechaincompress=threshold=0.04:ratio=6:attack=20:release=400[musd]")
    sl = []
    for i, s in enumerate(D['sfx']):
        solo = any(a - 0.3 <= s['t'] <= b for a, b in SOLO)
        j = ain(f"{P}/{s['file']}", ['-ss', str(s.get('ss', 0))] + (['-t', str(s['dur'])] if s.get('dur') else []))
        fc.append(f"[{j}:a]volume={s['vol'] * (1.0 if solo else SK):.4f},adelay={int(s['t'] * 1000)}|{int(s['t'] * 1000)}[s{i}]"); sl.append(f'[s{i}]')
    fc.append(''.join(sl) + f"amix=inputs={len(sl)}:duration=longest:normalize=0[sfx]")
    if stem == 'vo': fc.append("[musd]anullsink;[sfx]anullsink;[vo]apad[aout]")
    elif stem == 'bg': fc.append("[vo]anullsink;[musd][sfx]amix=inputs=2:duration=longest:normalize=0,apad[aout]")
    else: fc.append("[vo][musd][sfx]amix=inputs=3:duration=longest:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.82:attack=2:release=60:level=false,apad[aout]")
    return inputs, fc
def render(stem, out):
    inputs, fc = graph(stem)
    subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inputs + ['-filter_complex', ';'.join(fc), '-map', '[aout]', '-t', str(END), '-ar', '48000', out], check=True)
W = f'{P}/work'; render('vo', f'{W}/st_vo.wav'); render('bg', f'{W}/st_bg.wav')
import soundfile as sf
v, sr = sf.read(f'{W}/st_vo.wav'); b, _ = sf.read(f'{W}/st_bg.wav'); v = v.mean(1) if v.ndim > 1 else v; b = b.mean(1) if b.ndim > 1 else b
n = min(len(v), len(b)); rows = []; Wn = sr * 5
for i in range(0, n - Wn, Wn):
    vv, bb = v[i:i + Wn], b[i:i + Wn]; vr = np.sqrt((vv ** 2).mean())
    if vr < 0.01: continue
    rows.append((i / sr, 20 * np.log10(vr / max(1e-6, np.sqrt((bb ** 2).mean())))))
d = np.array([r[1] for r in rows])
print(f'MK={MK} SK={SK}  voice over background: median {np.median(d):.1f} dB, 10th pct {np.percentile(d, 10):.1f}, min {d.min():.1f}')
print('worst:', [(round(t), round(x, 1)) for t, x in sorted(rows, key=lambda r: r[1])[:6]])
if '--mux' in sys.argv:
    render('mix', f'{W}/mix.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{P}/out/final.mp4', '-i', f'{W}/mix.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '-t', str(END), f'{P}/out/final_mix.mp4'], check=True)
    print('wrote out/final_mix.mp4')
