"""Glitch check: frame-to-frame difference; flag frames whose diff is >3x both neighbours' diffs. usage: spike.py clip.mp4"""
import sys, subprocess, numpy as np
f = sys.argv[1]; W, H = 192, 108
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-vf', f'scale={W}:{H},format=gray', '-f', 'rawvideo', '-'], capture_output=True).stdout
a = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.float32)
d = np.abs(np.diff(a, axis=0)).mean((1, 2))
bad = []
for i in range(1, len(d) - 1):
    nb = max(d[i - 1], d[i + 1], 0.3)
    if d[i] > 3 * nb and d[i] > 1.0: bad.append((i + 1, round(float(d[i]), 2), round(float(nb), 2)))
r = d / np.maximum(0.3, np.maximum(np.r_[d[1:], 0], np.r_[0, d[:-1]]))
print(f, 'frames', len(a), 'max ratio', round(float(r[1:-1].max()), 2), 'spikes', bad[:10])
