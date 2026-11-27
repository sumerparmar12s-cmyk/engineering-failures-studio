"""Per-line Kokoro VO placed at fixed times (US English, am_michael). writes vo/vo.wav + vo/lines.json"""
import json, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
M = '/home/user/engineering-failures-studio/.toolchain/kokoro/'
k = Kokoro(M + 'kokoro-v1.0.onnx', M + 'voices-v1.0.bin'); SR = 24000
LINES = [(0.15, "A thorn got stuck deep in this foot."),
         (7.10, "First, press gently around it, to bring it closer to the surface."),
         (13.50, "Then, grip it right at the base, with clean tweezers."),
         (19.80, "Slow and steady."),
         (25.60, "And there it is.")]
END = 29.7; out = np.zeros(int(SR * END), np.float32); meta = []
for t, s in LINES:
    a, _ = k.create(s, voice='am_michael', speed=1.08, lang='en-us'); a = a.astype(np.float32)
    i = int(t * SR); out[i:i + len(a)] += a[:len(out) - i]; meta.append(dict(t=t, d=len(a) / SR, text=s))
sf.write('vo/vo.wav', out, SR); json.dump(meta, open('vo/lines.json', 'w'), indent=1)
for m in meta: print(f"{m['t']:.2f} +{m['d']:.2f}  {m['text']}")
