"""Wrecklore v2 compositor: footage-first documentary editing, rendered frame by frame with numpy + PIL and piped to ffmpeg.
A timeline is a list of Shot objects (absolute VO seconds). Each shot = one base layer (AI clip / video / photo with
Ken Burns / map with animated route / report page zoom) + overlays (typewriter text, punch words, counters, circles,
lower thirds, source tag) + an entry transition (cut, flash, whip, glitch, fade). Global: color grade, grain, vignette."""
import os, subprocess, math, random, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

W, H, FPS = int(os.environ.get('VW', 1920)), int(os.environ.get('VH', 1080)), 30
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = '/home/user/engineering-failures-studio/.toolchain/fonts'
_fc = {}
def font(name, size):
    k = (name, size)
    if k not in _fc:
        path = {'bebas': 'BebasNeue-Regular.ttf', 'oswald': 'Oswald.ttf', 'play': 'PlayfairDisplay.ttf', 'mono': 'CourierPrime-Regular.ttf',
                'monob': 'CourierPrime-Bold.ttf'}.get(name)
        f = ImageFont.truetype(f'{FONTS}/{path}', size) if path else ImageFont.truetype(f'/usr/share/fonts/opentype/inter/Inter-{name}.otf', size)
        if name == 'play':
            try: f.set_variation_by_axes([900])
            except Exception: pass
        if name == 'oswald':
            try: f.set_variation_by_axes([600])
            except Exception: pass
        _fc[k] = f
    return _fc[k]

clamp = lambda x, a=0.0, b=1.0: max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def eout(x): x = clamp(x); return 1 - (1 - x) ** 3
def lerp(a, b, k): return a + (b - a) * k

# ---------------- media loading ----------------
_img = {}
def load(path, mode='cover'):
    k = (path, mode)
    if k in _img: return _img[k]
    im = Image.open(path if path.startswith('/') else f'{ROOT}/{path}').convert('RGB')
    if mode == 'contain':      # figure on a blurred, darkened copy of itself (fills 16:9 without bars)
        CW, CH = 2400, 1350
        bg = im.copy(); s = max(CW / bg.width, CH / bg.height); bg = bg.resize((int(bg.width * s) + 1, int(bg.height * s) + 1))
        bg = bg.crop(((bg.width - CW) // 2, (bg.height - CH) // 2, (bg.width - CW) // 2 + CW, (bg.height - CH) // 2 + CH))
        bg = bg.filter(ImageFilter.GaussianBlur(40)); bg = Image.eval(bg, lambda v: int(v * 0.35))
        s = min(CW * 0.9 / im.width, CH * 0.86 / im.height); fg = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
        sh = Image.new('RGBA', (fg.width + 80, fg.height + 80), (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle([40, 40, fg.width + 40, fg.height + 40], fill=(0, 0, 0, 200))
        sh = sh.filter(ImageFilter.GaussianBlur(22)); x, y = (CW - fg.width) // 2, (CH - fg.height) // 2
        bg.paste(sh, (x - 40, y - 30), sh); bg.paste(fg, (x, y)); im = bg
    elif mode == 'portrait':   # document card for vertical video: full width page on a blurred copy of itself
        CW, CH = 1350, 2400
        bg = im.copy(); s = max(CW / bg.width, CH / bg.height); bg = bg.resize((int(bg.width * s) + 1, int(bg.height * s) + 1))
        bg = bg.crop(((bg.width - CW) // 2, (bg.height - CH) // 2, (bg.width - CW) // 2 + CW, (bg.height - CH) // 2 + CH))
        bg = bg.filter(ImageFilter.GaussianBlur(40)); bg = Image.eval(bg, lambda v: int(v * 0.3))
        s = CW * 0.96 / im.width; fg = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
        bg.paste(fg, ((CW - fg.width) // 2, int(CH * 0.24))); im = bg
    elif mode == 'upscale':    # small AI frames / low-res photos
        s = max(W * 1.25 / im.width, H * 1.25 / im.height)
        if s > 1: im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 70, 2))
    _img[k] = im; return im

def view(im, cx, cy, z):
    """Cover-fit view of image centred at (cx,cy) (0..1) with zoom z>=1."""
    s0 = max(W / im.width, H / im.height); vw, vh = W / (s0 * z), H / (s0 * z)
    x0 = clamp(cx * im.width - vw / 2, 0, im.width - vw); y0 = clamp(cy * im.height - vh / 2, 0, im.height - vh)
    return im.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + vw, y0 + vh)), (x0, y0, vw / W)

class VReader:
    """Sequential frame reader for a video segment, scaled to cover 1920x1080, optional slow motion and frame interpolation."""
    def __init__(self, path, ss=0.0, speed=1.0, interp=False):
        vf = f"setpts=PTS/{speed}," + ("minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:vsbmc=1," if interp else "fps=30,") + \
             f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H}"
        self.p = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', str(ss), '-i', path if path.startswith('/') else f'{ROOT}/{path}', '-vf', vf,
                                   '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
        self.last = None
    def next(self):
        b = self.p.stdout.read(W * H * 3)
        if len(b) == W * H * 3: self.last = Image.frombuffer('RGB', (W, H), b, 'raw', 'RGB', 0, 1)
        return self.last if self.last is not None else Image.new('RGB', (W, H))
    def close(self):
        try: self.p.kill()
        except Exception: pass

# ---------------- grades / grain / vignette ----------------
def _lut(r, g, b, lift=0.0, gamma=1.0, gain=1.0, sat=1.0):
    return dict(r=r, g=g, b=b, lift=lift, gamma=gamma, gain=gain, sat=sat)
GRADES = {
    'film':  _lut((1.03, 0.0), (1.0, 0.0), (0.97, 0.01), lift=0.02, gamma=1.0, gain=1.0, sat=0.92),
    'night': _lut((0.94, 0.0), (1.0, 0.01), (1.1, 0.04), lift=0.015, gamma=1.06, gain=1.0, sat=0.9),
    'fire':  _lut((1.08, 0.01), (0.99, 0.0), (0.9, 0.0), lift=0.01, gamma=0.98, gain=1.03, sat=1.05),
    'cold':  _lut((0.95, 0.0), (1.0, 0.0), (1.06, 0.02), lift=0.03, gamma=1.0, gain=0.98, sat=0.75),
    'paper': _lut((1.02, 0.0), (1.0, 0.0), (0.95, 0.0), lift=0.0, gamma=1.0, gain=1.0, sat=0.95),
    'none':  None,
}
_lutc = {}
def grade(arr, name):
    g = GRADES.get(name)
    if g is None: return arr
    if name not in _lutc:
        x = np.arange(256) / 255.0; luts = []
        for ch in 'rgb':
            k, off = g[ch]; y = (x * (1 - g['lift']) + g['lift']) ** g['gamma'] * g['gain'] * k + off
            luts.append(np.clip(y * 255, 0, 255).astype(np.uint8))
        _lutc[name] = luts
    l = _lutc[name]
    out = np.asarray(Image.fromarray(arr).point(list(l[0]) + list(l[1]) + list(l[2])))
    if g['sat'] != 1.0:
        f = out.astype(np.int16); m = (f[..., 0] * 3 + f[..., 1] * 6 + f[..., 2]) // 10
        out = np.clip(m[..., None] + (f - m[..., None]) * g['sat'], 0, 255).astype(np.uint8)
    return out
_rng = np.random.default_rng(5)
GRAIN = [(_rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32)) for _ in range(6)]
yy, xx = np.mgrid[0:H, 0:W]; _r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
VIG = np.clip(1.0 - 0.38 * np.clip(_r - 0.45, 0, None) ** 1.6, 0.45, 1.0).astype(np.float32)[..., None]
def finish_frame(arr, fi, grain=5.0, vig=True):
    f = arr.astype(np.float32)
    if vig: f *= VIG
    if grain:
        g = GRAIN[fi % 6]; g = np.repeat(np.repeat(g, 2, 0), 2, 1)
        f += g[..., None] * grain
    return np.clip(f, 0, 255).astype(np.uint8)

# ---------------- overlay drawing helpers ----------------
def shadow_text(d, xy, text, f, fill, sh=(0, 0, 0, 200), off=3, anchor='la', stroke=0, sfill=None):
    x, y = xy
    d.text((x + off, y + off), text, font=f, fill=sh, anchor=anchor, stroke_width=stroke, stroke_fill=sh)
    d.text((x, y), text, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=sfill or fill)

EXTRA = {}   # extra overlay kinds: name -> fn(img_layer_draw, layer, o, t, a, A, fi)
class O:
    """Overlay factory: each returns dict(kind,..); drawn in draw_overlays."""
    @staticmethod
    def type(text, at, x=90, y=860, size=40, cps=24, box=True, color=(255, 255, 255), until=None, f='monob'):
        return dict(k='type', text=text, at=at, x=x, y=y, size=size, cps=cps, box=box, color=color, until=until, f=f)
    @staticmethod
    def punch(text, at, until=None, size=190, color=(255, 255, 255), y=None, sub=None, shake=True, x=None, anchor='mm', f='bebas'):
        return dict(k='punch', text=text, at=at, until=until, size=size, color=color, y=y, sub=sub, shake=shake, x=x, anchor=anchor, f=f)
    @staticmethod
    def counter(at, v0, v1, dur, label='', prefix='', suffix='', until=None, x=W // 2, y=470, size=230, color=(255, 255, 255)):
        return dict(k='counter', at=at, v0=v0, v1=v1, dur=dur, label=label, prefix=prefix, suffix=suffix, until=until, x=x, y=y, size=size, color=color)
    @staticmethod
    def lower(title, sub, at, until=None):
        return dict(k='lower', title=title, sub=sub, at=at, until=until)
    @staticmethod
    def tag(text): return dict(k='tag', text=text)
    @staticmethod
    def circle(box, at, color=(255, 45, 35), until=None, w=8):   # box in screen px (x0,y0,x1,y1)
        return dict(k='circle', box=box, at=at, color=color, until=until, w=w)
    @staticmethod
    def arrow(p0, p1, at, color=(255, 45, 35), until=None):
        return dict(k='arrow', p0=p0, p1=p1, at=at, color=color, until=until)
    @staticmethod
    def label(text, x, y, at, until=None, color=(255, 214, 64), size=44, anchor='la', bg=True):
        return dict(k='label', text=text, x=x, y=y, at=at, until=until, color=color, size=size, anchor=anchor, bg=bg)
    @staticmethod
    def chapter(no, title, at, until=None):
        return dict(k='chapter', no=no, title=title, at=at, until=until)
    @staticmethod
    def quote(text, at, until=None, who='', hl=None, size=64):
        return dict(k='quote', text=text, at=at, until=until, who=who, hl=hl or [], size=size)
    @staticmethod
    def stamp(text, at, until=None, x=W // 2, y=H // 2, rot=-8, color=(220, 30, 30), size=120):
        return dict(k='stamp', text=text, at=at, until=until, x=x, y=y, rot=rot, color=color, size=size)
    @staticmethod
    def bars(at, until=None):  # letterbox for dramatic moments
        return dict(k='bars', at=at, until=until)
    @staticmethod
    def dark(at, until=None, amount=0.45):  # darken footage behind text
        return dict(k='dark', at=at, until=until, amount=amount)

def _alive(o, t, t1):
    u = o.get('until') or t1
    return o['at'] <= t <= u, u

def wrap(text, f, maxw):
    words, lines, cur = text.split(), [], ''
    for wd in words:
        nxt = (cur + ' ' + wd).strip()
        if f.getlength(nxt) > maxw and cur: lines.append(cur); cur = wd
        else: cur = nxt
    if cur: lines.append(cur)
    return lines

def draw_overlays(img, ovs, t, t1, fi):
    pre = [o for o in ovs if o['k'] in ('dark', 'bars')]
    for o in pre:
        alive, u = _alive(o, t, t1)
        if not alive: continue
        a = min(eout((t - o['at']) / 0.35), eout((u - t) / 0.3))
        if o['k'] == 'dark':
            img = Image.blend(img, Image.new('RGB', img.size, (0, 0, 0)), o['amount'] * a)
        else:
            d = ImageDraw.Draw(img); bh = int(120 * a); d.rectangle([0, 0, W, bh], fill=(0, 0, 0)); d.rectangle([0, H - bh, W, H], fill=(0, 0, 0))
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for o in ovs:
        k = o['k']
        if k in ('dark', 'bars'): continue
        if k == 'tag':
            d.text((W - 60, 50 if W > H else 60), o['text'].upper(), font=font('SemiBold', 24), fill=(255, 255, 255, 190), anchor='ra'); continue
        alive, u = _alive(o, t, t1)
        if not alive: continue
        a = min(eout((t - o['at']) / 0.25), eout((u - t) / 0.25)); A = int(255 * a)
        if k == 'type':
            n = int((t - o['at']) * o['cps']); s = o['text'][:n]
            f = font(o['f'], o['size']); lines = s.split('\n')
            full = o['text'].split('\n'); wmax = max(f.getlength(l) for l in full)
            if o['box'] and s:
                lh = int(o['size'] * 1.35)
                d.rectangle([o['x'] - 22, o['y'] - 16, o['x'] + wmax + 26, o['y'] + lh * len(full) + 4], fill=(8, 8, 10, int(185 * a)))
                d.rectangle([o['x'] - 22, o['y'] - 16, o['x'] - 14, o['y'] + lh * len(full) + 4], fill=(230, 40, 30, A))
            for i, l in enumerate(lines):
                yy_ = o['y'] + i * int(o['size'] * 1.35)
                d.text((o['x'], yy_), l, font=f, fill=o['color'] + (A,))
                if i == len(lines) - 1 and (fi // 8) % 2 == 0 and n < len(o['text']) + 30:
                    cx = o['x'] + f.getlength(l) + 4; d.rectangle([cx, yy_ + 4, cx + o['size'] * 0.5, yy_ + o['size']], fill=o['color'] + (A,))
        elif k == 'punch':
            p = eout((t - o['at']) / 0.18); sc = lerp(1.35, 1.0, p)
            f = font(o['f'], int(o['size'] * sc)); x = o['x'] or W // 2; y = o['y'] or H // 2 - 40
            if o['shake'] and t - o['at'] < 0.35:
                r = random.Random(fi); x += r.randint(-9, 9); y += r.randint(-7, 7)
            lines = o['text'].split('\n'); lh = int(o['size'] * sc * 0.95); y0 = y - lh * (len(lines) - 1) / 2
            for i, l in enumerate(lines):
                col = o['color'] if not isinstance(o['color'], list) else o['color'][i]
                d.text((x + 6, y0 + i * lh + 8), l, font=f, fill=(0, 0, 0, int(160 * a)), anchor=o['anchor'])
                d.text((x, y0 + i * lh), l, font=f, fill=tuple(col) + (A,), anchor=o['anchor'])
            if o['sub']:
                fs = font('SemiBold', 40); ys = y0 + lh * (len(lines) - 1) + o['size'] * 0.62
                sp = eout((t - o['at'] - 0.35) / 0.4); d.text((x, ys), o['sub'], font=fs, fill=(235, 235, 235, int(A * sp)), anchor='ma')
        elif k == 'counter':
            p = eout((t - o['at']) / o['dur']); v = lerp(o['v0'], o['v1'], p)
            txt = f"{o['prefix']}{v:,.0f}{o['suffix']}"; f = font('bebas', o['size'])
            d.text((o['x'] + 6, o['y'] + 8), txt, font=f, fill=(0, 0, 0, int(150 * a)), anchor='mm'); d.text((o['x'], o['y']), txt, font=f, fill=o['color'] + (A,), anchor='mm')
            if o['label']:
                fl = font('oswald', 50); lp = eout((t - o['at'] - 0.3) / 0.4)
                d.text((o['x'], o['y'] + o['size'] * 0.55), o['label'].upper(), font=fl, fill=(255, 214, 64, int(A * lp)), anchor='ma')
        elif k == 'lower':
            p = eout((t - o['at']) / 0.45); x = int(lerp(-700, 80, p)); y = 800
            ft, fs = font('oswald', 54), font('SemiBold', 32)
            wt = max(ft.getlength(o['title'].upper()), fs.getlength(o['sub'])) + 60
            d.rectangle([x, y, x + wt, y + 80], fill=(12, 12, 14, int(215 * a))); d.rectangle([x, y, x + 10, y + 128], fill=(230, 40, 30, A))
            d.text((x + 34, y + 8), o['title'].upper(), font=ft, fill=(255, 255, 255, A))
            d.rectangle([x, y + 80, x + wt, y + 128], fill=(230, 40, 30, int(225 * a))); d.text((x + 34, y + 86), o['sub'], font=fs, fill=(255, 255, 255, A))
        elif k == 'circle':
            p = eout((t - o['at']) / 0.55); x0, y0, x1, y1 = o['box']
            n = int(64 * p)
            pts = [((x0 + x1) / 2 + (x1 - x0) / 2 * math.cos(-1.9 + 2 * math.pi * 1.05 * i / 64) * (1 + 0.03 * math.sin(i)), (y0 + y1) / 2 + (y1 - y0) / 2 * math.sin(-1.9 + 2 * math.pi * 1.05 * i / 64)) for i in range(n + 1)]
            if len(pts) > 1: d.line(pts, fill=o['color'] + (A,), width=o['w'], joint='curve')
        elif k == 'arrow':
            p = eout((t - o['at']) / 0.4); (x0, y0), (x1, y1) = o['p0'], o['p1']; xe, ye = lerp(x0, x1, p), lerp(y0, y1, p)
            d.line([(x0, y0), (xe, ye)], fill=o['color'] + (A,), width=8)
            if p > 0.95:
                ang = math.atan2(y1 - y0, x1 - x0)
                d.polygon([(x1, y1), (x1 - 34 * math.cos(ang - 0.45), y1 - 34 * math.sin(ang - 0.45)), (x1 - 34 * math.cos(ang + 0.45), y1 - 34 * math.sin(ang + 0.45))], fill=o['color'] + (A,))
        elif k == 'label':
            f = font('oswald', o['size']); p = eout((t - o['at']) / 0.3)
            x, y = o['x'], o['y'] + (1 - p) * 20
            if o['bg']:
                bb = d.textbbox((x, y), o['text'], font=f, anchor=o['anchor']); d.rectangle([bb[0] - 14, bb[1] - 10, bb[2] + 14, bb[3] + 10], fill=(10, 10, 12, int(200 * a)))
            d.text((x, y), o['text'], font=f, fill=o['color'] + (A,), anchor=o['anchor'])
        elif k == 'chapter':
            p = eout((t - o['at']) / 0.6); fn, ft = font('oswald', 40), font('play', 110)
            d.text((110, 640), f"CHAPTER {o['no']}", font=fn, fill=(230, 60, 45, A))
            d.rectangle([110, 700, 110 + int(500 * p), 704], fill=(255, 255, 255, A))
            n = int(len(o['title']) * clamp((t - o['at'] - 0.2) / 0.7))
            d.text((106, 720), o['title'][:n], font=ft, fill=(255, 255, 255, A))
        elif k == 'quote':
            f = font('play', o['size']); lines = wrap(o['text'], f, 1500); lh = int(o['size'] * 1.3)
            y0 = H // 2 - lh * len(lines) // 2 - 30; n = int((t - o['at']) * 34); c = 0
            for i, l in enumerate(lines):
                vis = l[:max(0, n - c)]; c += len(l) + 1
                x = 210
                for hw in o['hl']:
                    j = l.find(hw)
                    if j >= 0 and len(vis) > j:
                        xa = x + f.getlength(l[:j]); xb = x + f.getlength(l[:min(len(vis), j + len(hw))])
                        d.rectangle([xa - 6, y0 + i * lh + o['size'] * 0.25, xb + 6, y0 + i * lh + o['size'] * 1.12], fill=(220, 30, 30, int(230 * a)))
                d.text((x, y0 + i * lh), vis, font=f, fill=(255, 255, 255, A))
            d.text((210, y0 - 120), '“', font=font('play', 160), fill=(230, 60, 45, A))
            if o['who'] and n > len(o['text']):
                d.text((214, y0 + lh * len(lines) + 30), '— ' + o['who'], font=font('SemiBold', 36), fill=(255, 214, 64, A))
        elif k == 'stamp':
            p = eout((t - o['at']) / 0.12); sc = lerp(1.8, 1.0, p)
            f = font('bebas', int(o['size'] * sc)); tw = f.getlength(o['text'])
            st = Image.new('RGBA', (int(tw + 80), int(o['size'] * sc * 1.25)), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
            sd.rectangle([6, 6, st.width - 6, st.height - 6], outline=o['color'] + (A,), width=10)
            sd.text((st.width / 2, st.height / 2), o['text'], font=f, fill=o['color'] + (A,), anchor='mm')
            st = st.rotate(o['rot'], expand=True, resample=Image.BICUBIC)
            lay.alpha_composite(st, (int(o['x'] - st.width / 2), int(o['y'] - st.height / 2)))
        elif k in EXTRA:
            EXTRA[k](d, lay, o, t, a, A, fi)
    img = img.convert('RGBA'); img.alpha_composite(lay); return img.convert('RGB')

# ---------------- shots ----------------
class Shot:
    def __init__(self, t0, src, grade='film', trans='cut', ov=None, src_tag=None, ai=False, grain=5.0, **k):
        self.t0, self.src, self.grade, self.trans, self.ov, self.k, self.grain = t0, src, grade, trans, list(ov or []), k, grain
        tagtext = 'AI visualization' if ai else src_tag
        if tagtext and not any(o['k'] == 'tag' for o in self.ov): self.ov.append(O.tag(tagtext))
        self.r = None

    def setup(self, t1):
        self.t1 = t1; s, k = self.src, self.k
        if s[0] in ('ai', 'vid'):
            path = f'{ROOT}/comp/cache/{s[1]}.mp4' if s[0] == 'ai' else s[1]
            self.r = VReader(path, k.get('ss', 0.0), k.get('speed', 1.0), interp=False)
        elif s[0] == 'img':
            self.im = load(s[1], k.get('mode', 'cover'))
        elif s[0] == 'route':
            self.base = load(s[1], 'contain')
    def close(self):
        if self.r: self.r.close()

    def frame(self, t, fi):
        s, k = self.src, self.k; u = clamp((t - self.t0) / max(0.01, self.t1 - self.t0))
        if s[0] in ('ai', 'vid'):
            img = self.r.next()
            z0, z1 = k.get('zoom', (1.0, 1.06)); z = lerp(z0, z1, ease(u))
            if abs(z - 1) > 0.002:
                cx, cy = k.get('c', (0.5, 0.5)); img, _ = view(img, cx, cy, z)
        elif s[0] == 'img':
            a, b = k.get('kb', ((0.5, 0.5, 1.0), (0.5, 0.5, 1.12)))
            e = ease(u) if k.get('smooth', True) else u
            img, _ = view(self.im, lerp(a[0], b[0], e), lerp(a[1], b[1], e), lerp(a[2], b[2], e))
        elif s[0] == 'route':
            img = self.route_frame(t, u)
        elif s[0] == 'black':
            img = Image.new('RGB', (W, H), (0, 0, 0))
        else:
            raise ValueError(s)
        return img

    def route_frame(self, t, u):
        """Animated map: the orange route is hidden, then revealed along its path with a glowing head; camera follows."""
        k = self.k; base = self.base
        if not hasattr(self, 'mask'):
            a = np.asarray(base).astype(np.int16)
            m = (a[..., 0] > 170) & (a[..., 1] > 90) & (a[..., 1] < 200) & (a[..., 2] < 110) & (a[..., 0] - a[..., 2] > 90)
            self.m = m; self.ys, self.xs = np.nonzero(m)
            hidden = a.copy(); mm = m.copy()
            for _ in range(3): mm = mm | np.roll(mm, 1, 0) | np.roll(mm, -1, 0) | np.roll(mm, 1, 1) | np.roll(mm, -1, 1)
            up = np.roll(a, 16, axis=0); hidden[mm] = up[mm]; self.m = mm
            self.hidden = hidden.astype(np.uint8); self.full = a.astype(np.uint8)
        rv = clamp((t - k['rev'][0]) / (k['rev'][1] - k['rev'][0]))
        xs = self.xs; xmin, xmax = k.get('xr', (xs.min(), xs.max())); xr = xmin + (xmax - xmin) * ease(rv)
        out = self.hidden.copy(); sel = self.m & (np.arange(self.m.shape[1])[None, :] <= xr)
        out[sel] = self.full[sel]
        im = Image.fromarray(out)
        # glowing head
        col = self.ys[np.abs(xs - xr) < 4]
        if len(col): self.lastcol = col
        elif hasattr(self, 'lastcol'): col = self.lastcol
        if len(col) and rv < 1:
            hy = col.mean(); d = ImageDraw.Draw(im)
            for r, a in ((26, 60), (16, 120), (8, 255)): d.ellipse([xr - r, hy - r, xr + r, hy + r], fill=(255, 220, 120))
        d = ImageDraw.Draw(im)
        for (mx, my, text, at, colr) in k.get('marks', []):      # map-space markers: pulsing ring + label, move with the map
            if t < at: continue
            p = eout((t - at) / 0.35); pr = 18 + 10 * (0.5 + 0.5 * math.sin((t - at) * 6))
            d.ellipse([mx - pr, my - pr, mx + pr, my + pr], outline=colr, width=6)
            f = font('oswald', 46); lines = text.split('\n'); ly = my - 70 - 56 * (len(lines) - 1)
            wmax = max(f.getlength(l) for l in lines)
            d.rectangle([mx - wmax / 2 - 16, ly - 10, mx + wmax / 2 + 16, ly + 56 * len(lines) + 4], fill=(15, 15, 18))
            for i, l in enumerate(lines): d.text((mx, ly + 56 * i + (1 - p) * 12), l, font=f, fill=colr if i == 0 else (255, 255, 255), anchor='ma')
        a, b = k.get('kb', ((0.5, 0.5, 1.0), (0.5, 0.5, 1.1)))
        if k.get('follow') and len(col):
            fx = xr / im.width; fy = col.mean() / im.height; z = lerp(a[2], b[2], ease(u))
            img, _ = view(im, fx, fy, z)
        else:
            img, _ = view(im, lerp(a[0], b[0], ease(u)), lerp(a[1], b[1], ease(u)), lerp(a[2], b[2], ease(u)))
        return img

# ---------------- transitions ----------------
def transition(img, prev, sh, t, fi):
    dt = t - sh.t0
    if sh.trans == 'flash' and dt < 0.3:
        img = Image.blend(img, Image.new('RGB', img.size, (255, 255, 255)), (1 - dt / 0.3) ** 2 * 0.9)
    elif sh.trans == 'fade' and dt < 0.5:
        img = Image.blend(Image.new('RGB', img.size), img, ease(dt / 0.5))
    elif sh.trans == 'whip' and dt < 0.22:
        p = dt / 0.22; off = int((1 - eout(p)) * 500)
        sm = img.resize((W // 4, H // 4)).filter(ImageFilter.BoxBlur(int(14 * (1 - p)) + 1)).resize((W, H))
        img = Image.blend(img, sm, 1 - p); img = ImageChops.offset(img, off, 0)
    elif sh.trans == 'glitch' and dt < 0.35:
        a = np.asarray(img).copy(); r = random.Random(fi)
        for _ in range(9):
            y = r.randint(0, H - 60); hgt = r.randint(8, 60); a[y:y + hgt] = np.roll(a[y:y + hgt], r.randint(-120, 120), axis=1)
        a[..., 0] = np.roll(a[..., 0], 14, axis=1); a[..., 2] = np.roll(a[..., 2], -14, axis=1)
        img = Image.fromarray(a)
    elif sh.trans == 'dip' and dt < 0.6:
        img = Image.blend(Image.new('RGB', img.size), img, ease(max(0, dt - 0.15) / 0.45))
    elif sh.trans == 'push' and dt < 0.3:
        p = eout(dt / 0.3); off = int((1 - p) * W)
        base = Image.new('RGB', img.size, (8, 10, 14)); base.paste(img, (off, 0)); img = base
    elif sh.trans == 'zoom' and dt < 0.35:
        p = eout(dt / 0.35); z = lerp(1.35, 1.0, p); img, _ = view(img, 0.5, 0.5, z)
        if p < 0.7: img = img.filter(ImageFilter.GaussianBlur(int((0.7 - p) * 18)))
    elif sh.trans == 'leak' and dt < 0.7:
        p = dt / 0.7; a = np.asarray(img).astype(np.float32)
        xs = np.linspace(-1, 2, W)[None, :] - p * 3; g = np.exp(-(xs ** 2) * 2.5)[..., None]
        a = a + g * np.array([255, 150, 60], np.float32) * 0.85 * math.sin(math.pi * p)
        img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    if sh.k.get('outfade') and sh.t1 - t < 0.45:
        img = Image.blend(Image.new('RGB', img.size), img, ease((sh.t1 - t) / 0.45))
    return img

# ---------------- render ----------------
def render(shots, end, out, t_from=0.0, t_to=None, log=None, post=None):
    t_to = end if t_to is None else t_to
    shots = sorted(shots, key=lambda s: s.t0)
    for i, s in enumerate(shots): s.t1n = shots[i + 1].t0 if i + 1 < len(shots) else end
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '16', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    n0, n1 = int(round(t_from * FPS)), int(round(t_to * FPS)); cur = None; prev = None
    for fi in range(n0, n1):
        t = fi / FPS
        sh = next(s for s in reversed(shots) if s.t0 <= t + 1e-6)
        if sh is not cur:
            if cur: cur.close()
            sh.setup(sh.t1n)
            if sh.src[0] in ('ai', 'vid') and t > sh.t0 + 0.05:      # starting mid-shot (segment render): skip frames
                for _ in range(int((t - sh.t0) * FPS)): sh.r.next()
            cur = sh
        img = sh.frame(t, fi)
        img = transition(img, prev, sh, t, fi)
        arr = grade(np.asarray(img), sh.grade)
        img = draw_overlays(Image.fromarray(arr), sh.ov, t, sh.t1, fi)
        if post: img = post(img, t, fi, sh)
        arr = finish_frame(np.asarray(img), fi, grain=sh.grain)
        enc.stdin.write(arr.tobytes())
        if log and fi % 300 == 0: print(f'{out}: {t:.1f}s', flush=True)
    if cur: cur.close()
    enc.stdin.close(); enc.wait()
