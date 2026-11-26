"""v2 sound design + mix: SFX generated from the timeline (typing, transitions, reveals) + story SFX + new music, voice-first.
usage: audio2.py MUSIC_K SFX_K [--mix]   -> work/mix2.wav ; prints voice-over-background stats"""
import sys, os, json, random, subprocess
import numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import edit4
from edit4 import T, END, S
ROOT = edit4.ROOT; A = f'{ROOT}/audio'
MK, SK = float(sys.argv[1]), float(sys.argv[2])
X = lambda f, t, v, **k: dict(file=f'{A}/sfx/{f}.wav', t=round(t, 3), vol=v, **k)
sfx = []; rnd = random.Random(3)
BIG = {358.47, 320.2}
for sh in T:
    if sh.trans == 'whip': sfx.append(X('whoosh', sh.t0 - 0.12, 0.45))
    elif sh.trans == 'glitch': sfx.append(X('glitch', sh.t0, 0.5))
    elif sh.trans in ('push', 'zoom'): sfx.append(X('whoosh2', sh.t0 - 0.08, 0.4))
    elif sh.trans == 'ping': sfx.append(X('sonar_ping', sh.t0, 0.5))
    elif sh.trans == 'sink': sfx.append(X('whoosh2', sh.t0 - 0.1, 0.35)); sfx.append(X('pressure_rumble', sh.t0, 0.35, dur=3.0))
    elif sh.trans == 'dip': pass
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
        elif k == 'bigtime': sfx.append(X('whoosh2', o['at'] - 0.1, 0.4)); sfx.append(X('hit', o['at'] + 0.05, 0.4))
        elif k == 'stat': sfx.append(X('hit', o['at'], 0.45)); sfx.append(X('tick', o['at'] + 0.1, 0.3))
        elif k == 'cheese':
            for i in range(len(o['names'])): sfx.append(X('whoosh2', o['at'] + i * 0.35, 0.3))
            if o.get('arrow'): sfx.append(X('braam', o['arrow'], 0.45))
        elif k == 'callout': sfx.append(X('pop', o['at'], 0.3))
        elif k == 'names':
            for i in range(len(o['names'])): sfx.append(X('key0', o['at'] + i * o['step'], 0.12))
        elif k == 'lower': sfx.append(X('whoosh2', o['at'], 0.35))
        elif k == 'label': sfx.append(X('pop', o['at'], 0.2))
        elif k == 'chat':
            for (at, who, text, stamp) in o['msgs']:
                sfx.append(X('modem_blip', at - 0.05, 0.45))
                for i, ch in enumerate(text):
                    if ch != ' ': sfx.append(X(f'key{rnd.randint(0, 2)}', at + i * max(0.3, len(text) / 26) / max(1, len(text)), 0.1))
        elif k == 'depthcard': sfx.append(X('pressure_rumble', o['at'], 0.55, dur=3.0)); sfx.append(X('sonar_ping', o['at'] + 0.1, 0.35))
        elif k == 'sonar':
            for j in range(3): sfx.append(X('sonar_ping', o['at'] + j * 1.4, 0.45))
        elif k == 'chart': sfx.append(X('riser', o['at'], 0.3))
# ---- story sounds ----
RA = lambda f, t, v, ss, dur: dict(file=f'{ROOT}/{f}', t=t, vol=v, ss=ss, dur=dur)
sfx += [X('underwater_bed', 0.0, 0.45, dur=50.0), X('modem_blip', 10.3, 0.5), X('braam', 12.72, 0.4), X('sonar_ping', 18.66, 1.0), X('heartbeat', 20.0, 0.25),
        X('sub_drop', 38.1, 0.4), X('braam', 46.1, 0.5), X('sonar_ping', 49.74, 1.0),
        X('ocean_bed', 50.3, 0.35, dur=12.0), X('ocean_bed', 62.3, 0.3, dur=17.0), X('wind_bed', 55.9, 0.25, dur=6.5), X('underwater_bed', 109.2, 0.35, dur=17.0),
        X('room_bed', 126.0, 0.3, dur=113.0), X('typewriter', 147.9, 0.3), X('thud', 161.36, 0.5), X('clock', 154.1, 0.3, dur=7.0),
        X('underwater_bed', 239.0, 0.45, dur=34.5), X('heartbeat', 255.6, 0.4), X('heartbeat', 256.6, 0.4), X('heartbeat', 257.6, 0.45),
        X('room_bed', 273.5, 0.25, dur=56.0), X('boom', S('bang', 284.9), 0.5), X('creak', 289.2, 0.4), X('boom', 292.4, 0.35),
        X('creak', 329.34, 1.0), X('groan', 329.6, 0.8), X('wind_bed', 330.6, 0.55, dur=23.0),
        X('underwater_bed', 353.8, 0.45, dur=19.5), X('pressure_rumble', 368.2, 0.55, dur=5.0), X('creak', 370.5, 0.4),
        X('room_bed', 373.3, 0.2, dur=47.0), X('clank', 397.2, 0.5), X('thud', 397.9, 0.6), X('clank', 399.3, 0.5), X('thud', 400.1, 0.6), X('thud', 401.8, 0.5),
        X('underwater_bed', 420.5, 0.5, dur=25.2), X('heartbeat', 437.8, 0.5), X('heartbeat', 438.8, 0.55), X('heartbeat', 439.8, 0.6), X('heartbeat', 440.8, 0.65), X('heartbeat', 441.8, 0.7),
        RA('real/DOD_110804017.mp4', 445.74, 2.6, 9.6, 4.5), X('sub_drop', 445.8, 1.0), X('boom', 445.76, 0.7),
        RA('real/DOD_111016570.mp4', 457.9, 0.6, 20.0, 12.0), X('ocean_bed', 473.3, 0.3, dur=8.0),
        X('jet_pass', 487.9, 0.35), X('ocean_bed', 481.3, 0.3, dur=21.0), X('sonar_ping', 504.38, 1.0),
        X('underwater_bed', 505.4, 0.45, dur=18.3), X('rig_hum', 505.4, 0.15, dur=18.3), X('sub_drop', 515.9, 0.45),
        X('room_bed', 523.7, 0.2, dur=63.0), X('underwater_bed', 586.7, 0.35, dur=36.0), X('bell', 614.2, 0.6), X('ocean_bed', 622.6, 0.3, dur=33.0)]
SOLO = [(18.66, 20.66), (49.74, 50.94), (329.34, 330.74), (445.74, 448.74), (504.38, 505.88), (614.18, 616.18)]
music = [('Chill_Deep', 0.0, 50.6, 0.32, 0), ('Mysterions', 50.3, 76.0, 0.3, 20), ('The_Mysterious_Body', 126.0, 113.4, 0.3, 0),
         ('Electronic_K_Deep_Nyah', 239.0, 34.8, 0.3, 0), ('Creepy_Setting_A', 273.5, 80.6, 0.3, 0), ('Ambient_H_Spaced_Out', 353.7, 19.8, 0.32, 0),
         ('Dark_Hallway', 373.2, 47.3, 0.3, 0), ('Horror_Suspense', 420.5, 25.3, 0.32, 0), ('Horror_Suspense', 449.0, 74.8, 0.3, 40),
         ('Piece_for_Disaffected_Piano_One', 523.6, 63.2, 0.32, 0), ('Nostalgic_Piano', 586.6, END - 586.6, 0.36, 0)]

def graph(stem):
    inputs, fc = [], []; idx = [0]
    def ain(path, extra=None): inputs.extend((extra or []) + ['-i', path]); idx[0] += 1; return idx[0] - 1
    vo = ain(f'{ROOT}/vo/vo.mp3'); fc.append(f"[{vo}:a]apad=whole_dur={END},asplit=2[vo][sc]")
    ml = []
    for i, (n, st, du, v, ss) in enumerate(music):
        j = ain(f'{A}/m4/{n}.mp3', ['-ss', str(ss), '-t', str(du)])
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
render('vo', f'{W}/st4_vo.wav'); render('bg', f'{W}/st4_bg.wav')
v, sr = sf.read(f'{W}/st4_vo.wav'); b, _ = sf.read(f'{W}/st4_bg.wav'); v = v.mean(1); b = b.mean(1); n = min(len(v), len(b)); rows = []
for i in range(0, n - sr * 5, sr * 5):
    vv, bb = v[i:i + sr * 5], b[i:i + sr * 5]; vr = np.sqrt((vv ** 2).mean())
    if vr < 0.01: continue
    rows.append((i / sr, 20 * np.log10(vr / max(1e-6, np.sqrt((bb ** 2).mean())))))
d = np.array([r[1] for r in rows])
print(f'MK={MK} SK={SK}: voice over background median {np.median(d):.1f} dB, 10th pct {np.percentile(d, 10):.1f}')
print('worst:', [(round(t), round(x, 1)) for t, x in sorted(rows, key=lambda r: r[1])[:8]])
if '--mix' in sys.argv: render('mix', f'{W}/mix4.wav'); print('wrote work/mix4.wav')
