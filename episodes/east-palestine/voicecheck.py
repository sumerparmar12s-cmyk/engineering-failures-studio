"""Voice-to-background ratio: align VO to final mix, least-squares gain, residual = music+SFX. usage: voicecheck.py final.mp4 vo.mp3"""
import sys, subprocess, numpy as np
SR = 8000
def load(f): return np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout, np.float32).astype(np.float64)
mix, vo = load(sys.argv[1]), load(sys.argv[2])
n = min(len(mix), len(vo))
a, b = mix[:SR * 60], vo[:SR * 60]
c = np.fft.irfft(np.fft.rfft(a, 2 * len(a)) * np.conj(np.fft.rfft(b, 2 * len(a))))
lag = int(np.argmax(np.r_[c[:SR], c[-SR:]])); lag = lag if lag < SR else lag - 2 * SR
vo = np.roll(vo, lag)[:n]; mix = mix[:n]
W = SR * 10; rows = []
for i in range(0, n - W, W):
    m, v = mix[i:i + W], vo[i:i + W]
    if np.sqrt((v ** 2).mean()) < 1e-3: continue
    g = (m @ v) / (v @ v); r = m - g * v
    rows.append((i / SR, 20 * np.log10(np.sqrt(((g * v) ** 2).mean()) / max(1e-9, np.sqrt((r ** 2).mean())))))
d = np.array([x[1] for x in rows])
print('lag', lag, 'median dB', round(float(np.median(d)), 1), 'min', round(float(d.min()), 1))
print('worst windows:', [(round(t), round(x, 1)) for t, x in sorted(rows, key=lambda r: r[1])[:8]])
