"""Raised (extruded) countries on the self-drawn globe, with the national flag on top. Drawn with cairo over a globe3d render."""
import math, cairo, numpy as np
from shapely.geometry import Polygon, MultiPolygon
import globe3d as G
RE = G.RE
def project_alt(cam, lon, lat, alt, W, H):
    C, f, r, u = cam.basis(); P = G.unit(np.asarray(lon, float), np.asarray(lat, float)) * (RE + np.asarray(alt, float))[..., None] if np.ndim(alt) else G.unit(np.asarray(lon, float), np.asarray(lat, float)) * (RE + alt)
    v = P - C; z = v @ f; th = math.tan(math.radians(cam.fov / 2))
    return (v @ r) / (z * th * W / H) * W / 2 + W / 2, H / 2 - (v @ u) / (z * th) * H / 2, z, ((P * (C - P)).sum(-1) > 0)
def polys(g, min_area=0.0):
    gs = list(g.geoms) if isinstance(g, MultiPolygon) else [g]
    return [p for p in gs if p.area >= min_area]
def raised(c, cam, geom, alt, flag=None, W=1080, H=1920, tol=0.05, wall=(0.42, 0.38, 0.34), min_area=0.02, outline=(1, 1, 1), shadow=True):
    """alt in km (height of the plateau). flag: cairo ImageSurface. Draws shadow, side walls (depth-sorted), flag-textured top."""
    if alt <= 0.01: return
    ps = [p.simplify(tol, preserve_topology=True) for p in polys(geom, min_area)]
    ps = [p for p in ps if not p.is_empty and p.geom_type == 'Polygon']
    if not ps: return
    # light from upper-left (screen space)
    for p in ps:
        lo, la = np.array(p.exterior.xy)
        bx, by, bz, bok = project_alt(cam, lo, la, 0, W, H); tx, ty, tz, tok = project_alt(cam, lo, la, alt, W, H)
        if not (tok.mean() > 0.6): continue
        if shadow:   # soft contact shadow, offset down-right
            off = min(60, (ty - by).__abs__().mean() * 0.6 + 6)
            c.new_path(); [(c.move_to if i == 0 else c.line_to)(x + off * 0.6, y + off) for i, (x, y) in enumerate(zip(bx, by))]; c.close_path()
            c.set_source_rgba(0, 0, 0, 0.28); c.fill()
        quads = []
        for i in range(len(lo) - 1):
            d = (bz[i] + bz[i + 1]) / 2
            ex, ey = bx[i + 1] - bx[i], by[i + 1] - by[i]; nx, ny = ey, -ex; L = math.hypot(nx, ny) + 1e-6
            light = 0.55 + 0.45 * max(0, (-nx * 0.6 - ny * 0.8) / L)
            quads.append((d, i, light))
        quads.sort(key=lambda q: -q[0])
        for d, i, light in quads:
            c.new_path(); c.move_to(bx[i], by[i]); c.line_to(bx[i + 1], by[i + 1]); c.line_to(tx[i + 1], ty[i + 1]); c.line_to(tx[i], ty[i]); c.close_path()
            c.set_source_rgb(*(v * light for v in wall)); c.fill_preserve(); c.set_source_rgba(0, 0, 0, 0.25); c.set_line_width(0.8); c.stroke()
        # top face
        c.new_path(); [(c.move_to if i == 0 else c.line_to)(x, y) for i, (x, y) in enumerate(zip(tx, ty))]; c.close_path()
        c.save(); c.clip_preserve()
        if flag is not None:
            x0, y0, x1, y1 = geom.bounds   # flag covers the whole country's bbox (shared across islands)
            fw, fh = flag.get_width(), flag.get_height(); cw, ch = (x1 - x0) * math.cos(math.radians((y0 + y1) / 2)), (y1 - y0)
            sc = max(cw / fw, ch / fh); gw, gh = fw * sc / math.cos(math.radians((y0 + y1) / 2)), fh * sc
            cxl, cyl = (x0 + x1) / 2, (y0 + y1) / 2
            A = project_alt(cam, np.array([cxl - gw / 2, cxl + gw / 2, cxl - gw / 2]), np.array([cyl + gh / 2, cyl + gh / 2, cyl - gh / 2]), alt, W, H)
            (ax, bx_, cx_), (ay, by_, cy_) = A[0], A[1]
            m = cairo.Matrix((bx_ - ax) / fw, (by_ - ay) / fw, (cx_ - ax) / fh, (cy_ - ay) / fh, ax, ay)
            try:
                c.save(); c.transform(m); c.set_source_surface(flag, 0, 0); c.get_source().set_filter(cairo.FILTER_BEST); c.paint(); c.restore()
            except cairo.Error:
                c.restore()
        g = cairo.LinearGradient(0, ty.min(), 0, ty.max()); g.add_color_stop_rgba(0, 1, 1, 1, 0.18); g.add_color_stop_rgba(1, 0, 0, 0, 0.12); c.set_source(g); c.paint()
        c.restore()
        c.set_source_rgba(*outline, 0.95); c.set_line_width(3); c.stroke()
def raised_label_pos(cam, geom, alt, W=1080, H=1920):
    p = geom.representative_point(); x, y, z, ok = project_alt(cam, np.array([p.x]), np.array([p.y]), alt, W, H); return float(x[0]), float(y[0])
def arc3d(c, cam, a, b, peak, frac=1.0, col=(1, 0.85, 0.2), lw=8, W=1080, H=1920, head=True):
    """great-circle-ish arrow from a to b rising to `peak` km, drawn up to frac."""
    n = 60; ts = np.linspace(0, frac, n)
    A, B = G.unit(a[0], a[1]), G.unit(b[0], b[1]); om = math.acos(max(-1, min(1, float(A @ B))))
    V = np.array([(math.sin((1 - t) * om) * A + math.sin(t * om) * B) / math.sin(om) for t in ts])
    lo = np.degrees(np.arctan2(V[:, 1], V[:, 0])); la = np.degrees(np.arcsin(np.clip(V[:, 2], -1, 1))); alt = peak * np.sin(np.pi * ts)
    x, y, z, ok = project_alt(cam, lo, la, alt, W, H)
    c.new_path(); c.move_to(x[0], y[0]); [c.line_to(xx, yy) for xx, yy in zip(x[1:], y[1:])]
    c.set_source_rgba(0, 0, 0, 0.35); c.set_line_width(lw + 6); c.stroke_preserve(); c.set_source_rgb(*col); c.set_line_width(lw); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke()
    if head and frac > 0.05:
        ang = math.atan2(y[-1] - y[-2], x[-1] - x[-2]); L = lw * 3.2
        c.new_path(); c.move_to(x[-1] + math.cos(ang) * L * 0.6, y[-1] + math.sin(ang) * L * 0.6)
        c.line_to(x[-1] + math.cos(ang + 2.5) * L, y[-1] + math.sin(ang + 2.5) * L); c.line_to(x[-1] + math.cos(ang - 2.5) * L, y[-1] + math.sin(ang - 2.5) * L); c.close_path()
        c.set_source_rgb(*col); c.fill()
