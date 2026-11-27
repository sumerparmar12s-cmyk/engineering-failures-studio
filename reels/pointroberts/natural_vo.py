"""Kokoro am_michael, sentence by sentence (natural intonation reset), varied short pauses. -> work/vo_raw.wav"""
import sys, re, json, os, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
M = '/home/user/engineering-failures-studio/.toolchain/kokoro/'
k = Kokoro(M + 'kokoro-v1.0.onnx', M + 'voices-v1.0.bin'); SR = 24000
SPEED = float(os.environ.get('SPEED', 1.2))
txt = open('script.md').read().split('## Narration (final)')[1].split('## Claim')[0].strip()
paras = [p.strip() for p in txt.split('\n\n') if p.strip()]
def sil(s): return np.zeros(int(SR * s), np.float32)
out = [sil(0.05)]; segs = []
for pi, p in enumerate(paras):
    sents = re.findall(r'[^.?!:]+(?:\.\.\.|[.?!:])?', p)
    sents = [s.strip() for s in sents if s.strip()]
    for si, s in enumerate(sents):
        a, _ = k.create(s, voice='am_michael', speed=SPEED, lang='en-us'); a = a.astype(np.float32)
        idx = np.where(np.abs(a) > 0.008)[0]
        if len(idx): a = a[max(0, idx[0] - 240): idx[-1] + 1200]
        segs.append(dict(kind='vo', start=sum(len(x) for x in out) / SR, text=s)); out.append(a)
        last = si == len(sents) - 1
        g = 0.30 if last else 0.16
        if s.endswith('...'): g = 0.38
        if s.endswith(':'): g = 0.22
        if s.endswith('?'): g = 0.26
        if s.startswith('Nope'): g = 0.2
        out.append(sil(g))
out.append(sil(1.0))
sf.write('work/vo_raw.wav', np.concatenate(out), SR); json.dump(segs, open('work/segments.json', 'w'), indent=1)
print('total', round(sum(len(x) for x in out) / SR, 2))
