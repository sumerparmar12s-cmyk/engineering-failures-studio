"""Kokoro, sentence by sentence; paragraphs starting with [voice] are acted character lines in that voice (louder, faster)."""
import re, json, os, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
M = '/home/user/engineering-failures-studio/.toolchain/kokoro/'
k = Kokoro(M + 'kokoro-v1.0.onnx', M + 'voices-v1.0.bin'); SR = 24000; SPEED = float(os.environ.get('SPEED', 1.2))
txt = open('script.md').read().split('## Narration (final)')[1].split('## Claim')[0].strip()
paras = [p.strip() for p in txt.split('\n\n') if p.strip()]
def sil(s): return np.zeros(int(SR * s), np.float32)
out = [sil(0.05)]; segs = []
for p in paras:
    m = re.match(r'\[(\w+)\]\s*(.*)', p); voice, text, acted = ('am_michael', p, False) if not m else (m.group(1), m.group(2), True)
    sents = [s.strip() for s in re.findall(r'[^.?!:]+(?:\.\.\.|[.?!:"]+)?', text) if s.strip()] if not acted else [text]
    for si, s in enumerate(sents):
        a, _ = k.create(s.replace('"', ''), voice=voice, speed=(1.12 if acted else SPEED), lang='en-gb' if voice.startswith('b') else 'en-us'); a = a.astype(np.float32)
        idx = np.where(np.abs(a) > 0.008)[0]
        if len(idx): a = a[max(0, idx[0] - 240): idx[-1] + 1200]
        if acted: a = np.tanh(a / max(1e-6, np.abs(a).max()) * 1.6) * 0.9 * np.abs(a).max() * 1.25   # a bit punchier
        segs.append(dict(kind='vo' if not acted else 'acted', voice=voice, start=sum(len(x) for x in out) / SR, text=s)); out.append(a)
        g = 0.3 if si == len(sents) - 1 else 0.16
        if s.endswith('...'): g = 0.4
        if acted: g = 0.32
        out.append(sil(g))
out.append(sil(1.0))
sf.write('work/vo_raw.wav', np.concatenate(out), SR); json.dump(segs, open('work/segments.json', 'w'), indent=1)
print('total', round(sum(len(x) for x in out) / SR, 2))
