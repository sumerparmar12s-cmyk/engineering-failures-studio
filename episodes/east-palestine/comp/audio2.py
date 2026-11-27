"""v2 sound design + mix: SFX generated from the timeline (typing, transitions, reveals) + story SFX + new music, voice-first.
usage: audio2.py MUSIC_K SFX_K [--mix]   -> work/mix2.wav ; prints voice-over-background stats"""
import sys, os, json, random, subprocess
import numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import edit2
from edit2 import T, END, S
ROOT = edit2.ROOT; A = f'{ROOT}/audio'
MK, SK = float(sys.argv[1]), float(sys.argv[2])
X = lambda f, t, v, **k: dict(file=f'{A}/sfx/{f}.wav', t=round(t, 3), vol=v, **k)
sfx = []; rnd = random.Random(3)
BIG = {26.2, 56.36, 374.68, 487.66}
for sh in T:
    if sh.trans == 'whip': sfx.append(X('whoosh', sh.t0 - 0.12, 0.45))
    elif sh.trans == 'glitch': sfx.append(X('glitch', sh.t0, 0.5))
    elif sh.trans == 'flash': sfx.append(X('braam' if round(sh.t0, 2) in BIG else 'hit', sh.t0, 0.55))
    if sh.grade == 'paper' and sh.src[0] == 'img': sfx.append(X('paper', sh.t0, 0.35))
    if (sh.k.get('src_tag') or '') and 'NTSB photo' in str([o.get('text') for o in sh.ov if o['k'] == 'tag']): sfx.append(X('shutter', sh.t0 + 0.05, 0.25))
    if sh.src[0] == 'route':
        sfx.append(X('whoosh2', sh.t0, 0.35))
        for m in sh.k.get('marks', []):
            if m[3] > sh.t0 + 0.2: sfx.append(X('pop', m[3], 0.4))
    for o in sh.ov:
        k = o['k']
        if k == 'type':
            n = len(o['text']); t = o['at']
            for i, ch in enumerate(o['text']):
                tt = o['at'] + i / o['cps']
                if ch == '\n': sfx.append(X('key_return', tt, 0.22))
                elif ch != ' ': sfx.append(X(f'key{rnd.randint(0, 2)}', tt + rnd.uniform(-0.01, 0.01), 0.16 + rnd.uniform(0, 0.05)))
        elif k == 'quote':
            for i in range(0, len(o['text']), 2): sfx.append(X(f'key{rnd.randint(0, 2)}', o['at'] + i / 34, 0.08))
        elif k == 'punch': sfx.append(X('hit', o['at'], 0.45))
        elif k == 'stamp': sfx.append(X('stamp', o['at'], 0.6))
        elif k == 'counter': sfx.append(X('tick', o['at'], 0.35)); sfx.append(X('pop', o['at'] + o['dur'], 0.3))
        elif k == 'circle': sfx.append(X('marker', o['at'], 0.45))
        elif k == 'chapter': sfx.append(X('swell', o['at'] - 1.9, 0.35)); sfx.append(X('braam', o['at'], 0.4))
        elif k == 'lower': sfx.append(X('whoosh2', o['at'], 0.35))
        elif k == 'label': sfx.append(X('pop', o['at'], 0.2))
# ---- story sounds ----
TE = 217.45 + 2.0
sfx += [X('wind_bed', 0.0, 0.35, dur=11.0), X('explosion_big', 11.2, 1.0), X('fire_bed', 11.5, 0.9, dur=3.4), X('fire_bed', 14.6, 0.3, dur=12.0),
        X('wind_bed', 28.9, 0.3, dur=10.0), X('heartbeat', 47.3, 0.4), X('heartbeat', 48.3, 0.4),
        X('train_rumble', 53.8, 0.35, dur=2.6), X('train_rumble', 59.5, 0.3, dur=14.0), X('horn', 67.6, 0.25), X('train_rumble', 72.4, 0.35, dur=13.0),
        X('train_rumble', 91.0, 0.2, dur=7.3), X('fire_bed', 98.4, 0.2, dur=3.8), X('creak', 118.0, 0.3), X('flame_burst', 121.8, 0.3),
        X('train_rumble', 137.4, 0.3, dur=3.0), X('alarm_beep', 145.95, 0.25), X('alarm_beep', S('hundred', 156.5), 0.35), X('train_rumble', 174.0, 0.3, dur=6.7),
        X('alarm_beep', S('two', 193.5), 0.5), X('drone', 197.5, 0.3, dur=3.0), X('radio_click', 200.3, 0.6), X('radio_click', 208.8, 0.5),
        X('train_rumble', 209.5, 0.3, dur=7.9), X('brake_squeal', 211.0, 0.3), X('snap', TE - 0.1, 0.5), X('derail_crash', TE, 1.0), X('brake_squeal', TE + 0.3, 0.6),
        X('flame_burst', 222.9, 0.45), X('fire_bed', 223.0, 0.3, dur=4.9), X('flame_burst', 226.5, 0.5), X('fire_bed', 227.9, 0.95, dur=2.6),
        X('sirens', 256.8, 0.2, dur=9.0), X('sirens', 265.98, 0.85, dur=2.6), X('sirens', 268.6, 0.18, dur=3.0), X('fire_bed', 268.2, 0.2, dur=9.0),
        X('fire_bed', 293.9, 0.25, dur=6.0), X('fire_bed', 300.3, 0.2, dur=14.0), X('pop', 329.2, 0.3), X('pop', 329.6, 0.3), X('pop', 330.1, 0.3), X('pop', 332.5, 0.35), X('pop', 332.8, 0.3),
        X('boom', S('bursts', 340.5), 0.35), X('fire_bed', 358.5, 0.3, dur=5.6), X('room_bed', 392.9, 0.3, dur=16.5),
        X('heartbeat', 409.6, 0.5), X('heartbeat', 410.6, 0.5), X('sub_drop', 411.4, 0.5), X('room_bed', 414.9, 0.3, dur=12.8),
        X('drone', 455.3, 0.3, dur=10.0), X('drone', 486.4, 0.4, dur=3.6), X('wind_bed', 490.0, 0.3, dur=7.0),
        X('explosion_big', 497.1, 1.0), X('fire_bed', 497.5, 0.9, dur=4.2), X('fire_bed', 501.7, 0.3, dur=15.0), X('wind_bed', 501.4, 0.3, dur=20.0),
        X('train_rumble', 616.7, 0.2, dur=6.8), X('wind_bed', 633.6, 0.25, dur=20.0), X('horn', 656.0, 0.12)]
sfx += [X('clock', 466.1 + i, 0.5) for i in range(8)] + [X('clock', 484.9 + i * 0.5, 0.35) for i in range(3)]
SOLO = [(11.2, 14.4), (TE, TE + 3.4), (227.9, 230.3), (265.98, 268.6), (497.1, 501.3)]
music = [('Dark_Ambient', 0.0, 56.4, 0.32, 0), ('Thinking_Tension_A', 56.2, 81.4, 0.3, 0), ('Pulse', 137.3, 72.4, 0.28, 0),
         ('Overt_Danger_A', 209.4, 65.4, 0.3, 0), ('Thinking_Tension_B', 274.6, 40.8, 0.28, 0), ('Urban_Confused_Mystery', 315.1, 94.4, 0.27, 0),
         ('Thinking_Tension_C', 414.8, 71.4, 0.3, 0), ('Night_Vigil', 490.0, 32.2, 0.3, 0), ('Hope_in_the_Sight_of_Fear', 522.0, 94.8, 0.28, 0),
         ('Sadness_on_White_Keys', 616.6, END - 616.6, 0.4, 0)]

def graph(stem):
    inputs, fc = [], []; idx = [0]
    def ain(path, extra=None): inputs.extend((extra or []) + ['-i', path]); idx[0] += 1; return idx[0] - 1
    vo = ain(f'{ROOT}/vo/vo.mp3'); fc.append(f"[{vo}:a]apad=whole_dur={END},asplit=2[vo][sc]")
    ml = []
    for i, (n, st, du, v, ss) in enumerate(music):
        j = ain(f'{A}/m2/{n}.mp3', ['-ss', str(ss), '-t', str(du)])
        fc.append(f"[{j}:a]aresample=44100,volume={v * MK:.4f},afade=t=in:st=0:d=1.5,afade=t=out:st={max(0, du - 2.5):.2f}:d=2.5,adelay={int(st * 1000)}|{int(st * 1000)}[m{i}]"); ml.append(f'[m{i}]')
    fc.append(''.join(ml) + f"amix=inputs={len(ml)}:duration=longest:normalize=0[mus]")
    fc.append("[mus][sc]sidechaincompress=threshold=0.03:ratio=8:attack=15:release=450[musd]")
    sl = []
    for i, s in enumerate(sfx):
        solo = any(a - 0.2 <= s['t'] <= b for a, b in SOLO)
        j = ain(s['file'], ['-ss', str(s.get('ss', 0))] + (['-t', str(s['dur'])] if s.get('dur') else []))
        fade = f",afade=t=out:st={max(0, s['dur'] - 0.6):.2f}:d=0.6" if s.get('dur') else ''
        fc.append(f"[{j}:a]aresample=44100,volume={s['vol'] * (1.0 if solo else SK):.4f}{fade},adelay={int(s['t'] * 1000)}|{int(s['t'] * 1000)}[s{i}]"); sl.append(f'[s{i}]')
    # mix SFX in groups to keep the graph manageable
    G = 60; grp = []
    for g in range(0, len(sl), G):
        fc.append(''.join(sl[g:g + G]) + f"amix=inputs={len(sl[g:g + G])}:duration=longest:normalize=0[sg{g}]"); grp.append(f'[sg{g}]')
    fc.append(''.join(grp) + f"amix=inputs={len(grp)}:duration=longest:normalize=0[sfx]")
    if stem == 'vo': fc.append("[musd]anullsink;[sfx]anullsink;[vo]anull[aout]")
    elif stem == 'bg': fc.append("[vo]anullsink;[musd][sfx]amix=inputs=2:duration=longest:normalize=0[aout]")
    else: fc.append("[vo][musd][sfx]amix=inputs=3:duration=longest:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.84:attack=2:release=60:level=false[aout]")
    return inputs, fc
def render(stem, out):
    inputs, fc = graph(stem); script = f'{ROOT}/work/fc_{stem}.txt'; open(script, 'w').write(';\n'.join(fc))
    subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inputs + ['-filter_complex_script', script, '-map', '[aout]', '-t', str(END), '-ar', '48000', '-ac', '2', out], check=True)
W = f'{ROOT}/work'
print('sfx events', len(sfx))
render('vo', f'{W}/st2_vo.wav'); render('bg', f'{W}/st2_bg.wav')
v, sr = sf.read(f'{W}/st2_vo.wav'); b, _ = sf.read(f'{W}/st2_bg.wav'); v = v.mean(1); b = b.mean(1); n = min(len(v), len(b)); rows = []
for i in range(0, n - sr * 5, sr * 5):
    vv, bb = v[i:i + sr * 5], b[i:i + sr * 5]; vr = np.sqrt((vv ** 2).mean())
    if vr < 0.01: continue
    rows.append((i / sr, 20 * np.log10(vr / max(1e-6, np.sqrt((bb ** 2).mean())))))
d = np.array([r[1] for r in rows])
print(f'MK={MK} SK={SK}: voice over background median {np.median(d):.1f} dB, 10th pct {np.percentile(d, 10):.1f}')
print('worst:', [(round(t), round(x, 1)) for t, x in sorted(rows, key=lambda r: r[1])[:8]])
if '--mix' in sys.argv: render('mix', f'{W}/mix2.wav'); print('wrote work/mix2.wav')
