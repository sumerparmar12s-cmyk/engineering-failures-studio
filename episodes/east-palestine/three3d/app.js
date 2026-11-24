// Deterministic 3D scenes for the East Palestine episode. window.renderAt(t) draws clip time t (seconds).
// Generic freight train (no railroad livery). Everything is computed from t, so frames can be rendered in any order.
// Scenes: T1 night pass through town · T2 burning wheelset passes a detector · T3 bearing cutaway heating up
//         T4 derailment pileup + fire · T5 vent and burn (close) · T6 vent and burn (wide, developed column)
import * as THREE from 'three';
import { RoomEnvironment } from './RoomEnvironment.js';

const Q = new URLSearchParams(location.search);
const SCENE = Q.get('scene') || 'T1';
const CFG = JSON.parse(Q.get('cfg') || '{}');
const W = 1920, H = 1080;
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const ease = x => { x = clamp(x); return x * x * (3 - 2 * x); };
const seg = (t, a, d) => ease((t - a) / d);
const lerp = (a, b, k) => a + (b - a) * k;
function rng(seed) { let s = seed >>> 0; return () => { s += 0x6D2B79F5; let r = Math.imul(s ^ (s >>> 15), 1 | s); r ^= r + Math.imul(r ^ (r >>> 7), 61 | r); return ((r ^ (r >>> 14)) >>> 0) / 4294967296; }; }
const NIGHT = ['T1', 'T2', 'T4'].includes(SCENE);

// ---------------- renderer ----------------
const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true, logarithmicDepthBuffer: true });
renderer.setSize(W, H); renderer.setPixelRatio(1);
renderer.shadowMap.enabled = !NIGHT; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = NIGHT ? 1.25 : 1.0;
renderer.outputColorSpace = THREE.SRGBColorSpace;
document.body.prepend(renderer.domElement);
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(38, W / H, SCENE === 'T3' ? 0.02 : 0.3, 20000);
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;

// ---------------- overlay labels ----------------
const ov = document.getElementById('ov'); const fadeEl = document.getElementById('fade');
const labels = [];
function label(text, sub, anchor, at, opts = {}) {
  const el = document.createElement('div'); el.className = 'lab' + (opts.red ? ' red' : '');
  el.innerHTML = text + (sub ? `<small>${sub}</small>` : ''); ov.appendChild(el);
  const dot = document.createElement('div'); dot.className = 'dot'; ov.appendChild(dot);
  const ln = document.createElement('div'); ln.className = 'line'; ov.appendChild(ln);
  const L = { el, dot, ln, anchor, at, until: opts.until ?? 1e9, dx: opts.dx ?? 140, dy: opts.dy ?? -110 };
  labels.push(L); return L;
}
const _v = new THREE.Vector3();
function updateLabels(t) {
  for (const L of labels) {
    const p = typeof L.anchor === 'function' ? L.anchor(t) : L.anchor;
    _v.copy(p).project(camera);
    const x = (_v.x * 0.5 + 0.5) * W, y = (-_v.y * 0.5 + 0.5) * H;
    const a = seg(t, L.at, 0.45) * (1 - seg(t, L.until, 0.4)) * (_v.z < 1 ? 1 : 0);
    const lx = x + L.dx, ly = y + L.dy;
    L.dot.style.left = x + 'px'; L.dot.style.top = y + 'px'; L.dot.style.opacity = a;
    const len = Math.hypot(L.dx, L.dy - 20) * seg(t, L.at, 0.4), ang = Math.atan2(L.dy + 20, L.dx);
    L.ln.style.left = x + 'px'; L.ln.style.top = y + 'px'; L.ln.style.width = len + 'px'; L.ln.style.transform = `rotate(${ang}rad)`; L.ln.style.opacity = a;
    L.el.style.left = (L.dx >= 0 ? lx + 8 : lx - L.el.offsetWidth - 8) + 'px'; L.el.style.top = (ly - 30) + 'px'; L.el.style.opacity = a;
  }
}

// ---------------- textures ----------------
function canvasTex(size, draw) { const c = document.createElement('canvas'); c.width = c.height = size; draw(c.getContext('2d'), size); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t; }
const puffTex = canvasTex(256, (g, s) => {           // soft cloud puff with noisy edge
  const r = rng(7); const img = g.createImageData(s, s);
  const blobs = Array.from({ length: 14 }, () => [s / 2 + (r() - 0.5) * s * 0.36, s / 2 + (r() - 0.5) * s * 0.36, s * (0.16 + r() * 0.16)]);
  for (let y = 0; y < s; y++) for (let x = 0; x < s; x++) {
    let a = 0; for (const [bx, by, br] of blobs) { const d = Math.hypot(x - bx, y - by) / br; a = Math.max(a, 1 - d * d); }
    const edge = clamp(1 - Math.hypot(x - s / 2, y - s / 2) / (s * 0.5)); a = clamp(a) * edge;
    const i = (y * s + x) * 4; const shade = 200 + 55 * (1 - y / s);
    img.data[i] = img.data[i + 1] = img.data[i + 2] = shade; img.data[i + 3] = 255 * Math.pow(a, 1.2);
  }
  g.putImageData(img, 0, 0);
});
const fireTex = canvasTex(128, (g, s) => {
  const gr = g.createRadialGradient(s / 2, s / 2, 0, s / 2, s / 2, s / 2);
  gr.addColorStop(0, 'rgba(255,250,220,1)'); gr.addColorStop(0.25, 'rgba(255,200,90,0.9)'); gr.addColorStop(0.55, 'rgba(255,110,20,0.45)'); gr.addColorStop(1, 'rgba(200,40,0,0)');
  g.fillStyle = gr; g.fillRect(0, 0, s, s);
});
const glowTex = canvasTex(64, (g, s) => {
  const gr = g.createRadialGradient(s / 2, s / 2, 0, s / 2, s / 2, s / 2);
  gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.3, 'rgba(255,255,255,0.5)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = gr; g.fillRect(0, 0, s, s);
});
const grassTex = canvasTex(512, (g, s) => {
  const r = rng(3); g.fillStyle = NIGHT ? '#25301f' : '#5d6b45'; g.fillRect(0, 0, s, s);
  for (let i = 0; i < 9000; i++) { const v = r(); g.fillStyle = NIGHT ? `rgba(${30 + v * 30},${40 + v * 30},${25 + v * 20},0.6)` : `rgba(${80 + v * 50},${95 + v * 45},${55 + v * 30},0.55)`; g.fillRect(r() * s, r() * s, 2 + r() * 3, 2 + r() * 3); }
});
grassTex.wrapS = grassTex.wrapT = THREE.RepeatWrapping; grassTex.repeat.set(120, 120);
const ballastTex = canvasTex(256, (g, s) => {
  const r = rng(5); g.fillStyle = '#6a6560'; g.fillRect(0, 0, s, s);
  for (let i = 0; i < 5000; i++) { const v = 70 + r() * 90; g.fillStyle = `rgb(${v},${v * 0.96},${v * 0.92})`; g.beginPath(); g.arc(r() * s, r() * s, 1 + r() * 2.5, 0, 7); g.fill(); }
});
ballastTex.wrapS = ballastTex.wrapT = THREE.RepeatWrapping;

// ---------------- materials ----------------
const std = (color, rough = 0.7, metal = 0.1, extra = {}) => new THREE.MeshStandardMaterial({ color, roughness: rough, metalness: metal, ...extra });
const M = {
  grass: std(0xffffff, 1, 0, { map: grassTex }),
  ballast: std(0xffffff, 0.95, 0, { map: ballastTex }),
  tie: std(0x3b2f25, 0.9),
  rail: std(0x8a8d92, 0.35, 0.85),
  steelDark: std(0x2a2b2e, 0.6, 0.5),
  truck: std(0x1c1c1e, 0.7, 0.5),
  loco: std(0x2c3440, 0.5, 0.35),
  locoStripe: std(0xd8d8d0, 0.5, 0.2),
  hopper: std(0x9aa0a6, 0.55, 0.4),
  hopperB: std(0x7e6d5e, 0.65, 0.3),
  tank: std(0x16171a, 0.45, 0.5),
  tankW: std(0xd9d9d4, 0.45, 0.3),
  box: std(0x6d3524, 0.75, 0.2),
  boxB: std(0x3d4c5c, 0.7, 0.25),
  glass: std(0x0c1118, 0.1, 0.8),
  house: [std(0xd8d2c4, 0.85), std(0xb9c3c9, 0.85), std(0xe6dcc0, 0.85), std(0x9a6b55, 0.85), std(0xf0efe8, 0.85)],
  roof: [std(0x3b3b3f, 0.8), std(0x5a3d32, 0.8), std(0x2e3a45, 0.8)],
  window: new THREE.MeshBasicMaterial({ color: 0xffc56b }),
  windowDark: std(0x1a2028, 0.2, 0.6),
  road: std(0x2b2c2e, 0.9),
  dirt: std(0x5b4a39, 1),
  trunk: std(0x3b2b1e, 0.9),
  leaf: std(NIGHT ? 0x1f2b1a : 0x3d4e2c, 0.9),
  bare: std(0x4a3d33, 0.95),
};
function mesh(g, m, cast = true) { const o = new THREE.Mesh(g, m); o.castShadow = cast; o.receiveShadow = true; return o; }

// ---------------- track ----------------
const RAIL_Y = 0.62, GAUGE = 1.435;
function track(x0, x1, z = 0) {
  const g = new THREE.Group(); const len = x1 - x0, cx = (x0 + x1) / 2;
  const bal = new THREE.Shape(); bal.moveTo(-2.9, 0); bal.lineTo(-1.7, 0.38); bal.lineTo(1.7, 0.38); bal.lineTo(2.9, 0); bal.lineTo(-2.9, 0);
  const bg = new THREE.ExtrudeGeometry(bal, { depth: len, bevelEnabled: false }); bg.rotateY(Math.PI / 2); bg.translate(x0, -0.02, 0);
  const uv = bg.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * 0.3, uv.getY(i) * 0.3);
  const b = mesh(bg, M.ballast, false); b.position.z = z; g.add(b);
  const n = Math.floor(len / 0.6); const tg = new THREE.BoxGeometry(0.24, 0.16, 2.6);
  const ties = new THREE.InstancedMesh(tg, M.tie, n); const m4 = new THREE.Matrix4();
  for (let i = 0; i < n; i++) { m4.makeTranslation(x0 + 0.3 + i * 0.6, 0.42, z); ties.setMatrixAt(i, m4); } ties.receiveShadow = true; g.add(ties);
  for (const s of [-1, 1]) {
    const head = mesh(new THREE.BoxGeometry(len, 0.07, 0.075), M.rail, false); head.position.set(cx, RAIL_Y - 0.035, z + s * GAUGE / 2); g.add(head);
    const web = mesh(new THREE.BoxGeometry(len, 0.11, 0.03), M.rail, false); web.position.set(cx, RAIL_Y - 0.125, z + s * GAUGE / 2); g.add(web);
    const foot = mesh(new THREE.BoxGeometry(len, 0.025, 0.14), M.rail, false); foot.position.set(cx, 0.512, z + s * GAUGE / 2); g.add(foot);
  }
  return g;
}

// ---------------- rolling stock ----------------
const WR = 0.46; // wheel radius
function wheelset() {
  const g = new THREE.Group();
  const axle = mesh(new THREE.CylinderGeometry(0.09, 0.09, 2.1, 12), M.steelDark); axle.rotation.x = Math.PI / 2; g.add(axle);
  for (const s of [-1, 1]) {
    const w = mesh(new THREE.CylinderGeometry(WR, WR, 0.14, 28), M.truck); w.rotation.x = Math.PI / 2; w.position.z = s * 0.72; g.add(w);
    const fl = mesh(new THREE.CylinderGeometry(WR + 0.03, WR + 0.03, 0.03, 28), M.truck); fl.rotation.x = Math.PI / 2; fl.position.z = s * 0.64; g.add(fl);
    const brg = mesh(new THREE.CylinderGeometry(0.13, 0.13, 0.24, 16), M.steelDark); brg.rotation.x = Math.PI / 2; brg.position.z = s * 0.95; brg.name = s < 0 ? 'brgL' : 'brgR'; g.add(brg);
    const spoke = mesh(new THREE.BoxGeometry(0.5, 0.06, 0.02), M.steelDark, false); spoke.position.z = s * 0.8; g.add(spoke); // makes rotation visible
  }
  return g;
}
function truckAssy() {
  const g = new THREE.Group(); const ws = [];
  for (const dx of [-0.89, 0.89]) { const w = wheelset(); w.position.set(dx, WR, 0); g.add(w); ws.push(w); }
  for (const s of [-1, 1]) { const sf = mesh(new THREE.BoxGeometry(2.7, 0.32, 0.18), M.truck); sf.position.set(0, WR + 0.05, s * 1.0); g.add(sf); }
  const bol = mesh(new THREE.BoxGeometry(0.42, 0.3, 2.3), M.truck); bol.position.set(0, WR + 0.18, 0); g.add(bol);
  g.userData.ws = ws; return g;
}
// a car: group origin = car center at rail-top level. kinds: loco, hopper, tank, tankW, box
function car(kind, seed = 1) {
  const r = rng(seed); const g = new THREE.Group(); const L = kind === 'loco' ? 22 : kind.startsWith('tank') ? 18 : kind === 'box' ? 17 : 18.3;
  const trucks = []; const tOff = kind === 'loco' ? 7.6 : L / 2 - 2.6;
  for (const s of [1, -1]) { const t = truckAssy(); t.position.x = s * tOff; g.add(t); trucks.push(t); }
  const deckY = 1.15;
  const frame = mesh(new THREE.BoxGeometry(L - 0.6, 0.35, 2.9), M.steelDark); frame.position.y = deckY; g.add(frame);
  for (const s of [-1, 1]) { const cp = mesh(new THREE.BoxGeometry(0.6, 0.25, 0.3), M.steelDark); cp.position.set(s * (L / 2 - 0.15), deckY - 0.05, 0); g.add(cp); }
  if (kind === 'loco') {
    const body = mesh(new THREE.BoxGeometry(14.5, 3.0, 2.9), M.loco); body.position.set(-3.3, deckY + 1.7, 0); g.add(body);
    const cab = mesh(new THREE.BoxGeometry(4.2, 3.6, 3.1), M.loco); cab.position.set(6.4, deckY + 2.0, 0); g.add(cab);
    const nose = mesh(new THREE.BoxGeometry(2.0, 1.9, 2.9), M.loco); nose.position.set(9.6, deckY + 1.15, 0); g.add(nose);
    const ws = mesh(new THREE.BoxGeometry(0.06, 0.9, 2.6), M.glass, false); ws.position.set(8.53, deckY + 3.0, 0); g.add(ws);
    for (const s of [-1, 1]) { const st = mesh(new THREE.BoxGeometry(21, 0.22, 0.02), M.locoStripe, false); st.position.set(0, deckY + 0.6, s * 1.47); g.add(st);
      const sw = mesh(new THREE.BoxGeometry(1.6, 0.8, 0.04), M.glass, false); sw.position.set(6.6, deckY + 3.0, s * 1.56); g.add(sw); }
    const hl = new THREE.Mesh(new THREE.SphereGeometry(0.16, 12, 8), new THREE.MeshBasicMaterial({ color: 0xfff4d0 })); hl.position.set(10.62, deckY + 1.7, 0); g.add(hl);
    for (const s of [-1, 1]) { const dl = hl.clone(); dl.position.set(10.62, deckY + 0.6, s * 0.9); g.add(dl); }
    g.userData.headlight = hl;
  } else if (kind === 'hopper') {
    const prof = new THREE.Shape(); prof.moveTo(-L / 2 + 0.5, 0.2); prof.lineTo(-L / 2 + 0.5, 3.6); prof.lineTo(L / 2 - 0.5, 3.6); prof.lineTo(L / 2 - 0.5, 0.2);
    for (let i = 0; i < 3; i++) { const x = L / 2 - 0.5 - (i + 0.5) * (L - 1) / 3; prof.lineTo(x + 1.6, 0.2); prof.lineTo(x, -0.6); prof.lineTo(x - 1.6, 0.2); }
    prof.lineTo(-L / 2 + 0.5, 0.2);
    const geo = new THREE.ExtrudeGeometry(prof, { depth: 3.1, bevelEnabled: true, bevelSize: 0.06, bevelThickness: 0.06, bevelSegments: 1 }); geo.translate(0, 0, -1.55);
    const b = mesh(geo, r() < 0.5 ? M.hopper : M.hopperB); b.position.y = deckY + 0.3; g.add(b);
    const roof = mesh(new THREE.CylinderGeometry(1.55, 1.55, L - 1, 24, 1, false, 0, Math.PI), b.material); roof.rotation.z = Math.PI / 2; roof.rotation.y = Math.PI / 2; roof.rotation.set(0, 0, Math.PI / 2); roof.scale.set(1, 1, 1);
    const rg = new THREE.CylinderGeometry(1.55, 1.55, L - 1, 24, 1, false, -Math.PI / 2, Math.PI); rg.rotateZ(Math.PI / 2); rg.scale(1, 0.3, 1);
    const rf = mesh(rg, b.material); rf.position.y = deckY + 3.9; g.add(rf);
    for (let i = -3; i <= 3; i++) { const rib = mesh(new THREE.BoxGeometry(0.12, 3.4, 3.24), M.steelDark); rib.position.set(i * 2.4, deckY + 2.1, 0); g.add(rib); }
  } else if (kind.startsWith('tank')) {
    const mat = kind === 'tankW' ? M.tankW : M.tank;
    const tg = new THREE.CylinderGeometry(1.5, 1.5, L - 3.2, 40); tg.rotateZ(Math.PI / 2);
    const tb = mesh(tg, mat); tb.position.y = deckY + 1.75; g.add(tb);
    for (const s of [-1, 1]) { const hd = mesh(new THREE.SphereGeometry(1.5, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2), mat); hd.scale.set(1, 0.45, 1); hd.rotation.z = -s * Math.PI / 2; hd.position.set(s * (L / 2 - 1.6), deckY + 1.75, 0); g.add(hd); }
    const dome = mesh(new THREE.CylinderGeometry(0.55, 0.6, 0.5, 20), M.steelDark); dome.position.y = deckY + 3.4; g.add(dome);
    const walk = mesh(new THREE.BoxGeometry(1.8, 0.06, 1.8), M.steelDark); walk.position.y = deckY + 3.15; g.add(walk);
    for (const s of [-1, 1]) { const sad = mesh(new THREE.BoxGeometry(0.8, 0.9, 2.2), M.steelDark); sad.position.set(s * tOff, deckY + 0.45, 0); g.add(sad); }
    const plac = mesh(new THREE.BoxGeometry(0.5, 0.5, 0.02), std(0xd02020, 0.6), false); plac.rotation.x = 0; plac.rotation.z = Math.PI / 4; plac.position.set(-L / 2 + 2.4, deckY + 1.6, 1.52); g.add(plac);
  } else {
    const b = mesh(new THREE.BoxGeometry(L - 0.4, 3.6, 3.0), r() < 0.5 ? M.box : M.boxB); b.position.y = deckY + 2.0; g.add(b);
    for (let i = -4; i <= 4; i++) { const rib = mesh(new THREE.BoxGeometry(0.08, 3.4, 3.08), M.steelDark); rib.position.set(i * 1.8, deckY + 2.0, 0); g.add(rib); }
    const door = mesh(new THREE.BoxGeometry(3.0, 3.0, 3.1), M.steelDark); door.position.set(0, deckY + 1.9, 0); g.add(door);
  }
  g.userData.L = L; g.userData.trucks = trucks; g.userData.kind = kind;
  return g;
}
const GAP = 1.0; // coupler gap between car bodies
// consist: 3 locos, then a mix; index 25 = the hopper (23rd railcar after 2 distributed... we simply make it index 25 counting locos)
function consist(n, seed = 11) {
  const r = rng(seed); const list = ['loco', 'loco', 'loco'];
  for (let i = 3; i < n; i++) {
    const v = r(); list.push(v < 0.38 ? 'hopper' : v < 0.62 ? 'box' : v < 0.85 ? 'tank' : 'tankW');
  }
  list[HOT] = 'hopper';
  for (const i of [HOT + 5, HOT + 9, HOT + 10, HOT + 13, HOT + 16]) if (i < n) list[i] = 'tank';   // the vinyl chloride tank cars, behind the hot car
  return list;
}
const HOT = 25;  // array index of the hopper car with the failing bearing (23rd railcar; 3 locos ahead)

// ---------------- world: ground, town, trees ----------------
function ground(size = 6000, mat = M.grass) { const g = mesh(new THREE.PlaneGeometry(size, size), mat, false); g.rotation.x = -Math.PI / 2; g.position.y = -0.4; return g; }
function house(x, z, rot, seed, lit) {
  const r = rng(seed); const g = new THREE.Group();
  const w = 7 + r() * 4, d = 8 + r() * 4, h = 3 + (r() < 0.4 ? 2.8 : 0) + r() * 0.6;
  const b = mesh(new THREE.BoxGeometry(w, h, d), M.house[Math.floor(r() * M.house.length)]); b.position.y = h / 2 - 0.4; g.add(b);
  const rs = new THREE.Shape(); rs.moveTo(-w / 2 - 0.4, 0); rs.lineTo(0, 2.2 + r()); rs.lineTo(w / 2 + 0.4, 0); rs.lineTo(-w / 2 - 0.4, 0);
  const rg = new THREE.ExtrudeGeometry(rs, { depth: d + 0.8, bevelEnabled: false }); rg.translate(0, 0, -d / 2 - 0.4);
  const rf = mesh(rg, M.roof[Math.floor(r() * M.roof.length)]); rf.position.y = h - 0.4; g.add(rf);
  const nw = Math.floor(w / 2.4);
  for (let fl = 0; fl < (h > 5 ? 2 : 1); fl++) for (let i = 0; i < nw; i++) {
    const on = lit && r() < 0.55;
    const wi = mesh(new THREE.BoxGeometry(1.0, 1.2, 0.06), on ? M.window : M.windowDark, false); wi.position.set(-w / 2 + 1.3 + i * (w - 2.6) / Math.max(1, nw - 1), 1.2 + fl * 2.8, d / 2 + 0.02); g.add(wi);
    const wb = wi.clone(); wb.position.z = -d / 2 - 0.02; g.add(wb);
  }
  g.position.set(x, 0, z); g.rotation.y = rot; return g;
}
function tree(x, z, seed, bare = false) {
  const r = rng(seed); const g = new THREE.Group(); const h = 6 + r() * 7;
  const tr = mesh(new THREE.CylinderGeometry(0.18, 0.3, h * 0.5, 7), M.trunk); tr.position.y = h * 0.25 - 0.4; g.add(tr);
  if (bare) { // winter tree: a few branches
    for (let i = 0; i < 6; i++) { const br = mesh(new THREE.CylinderGeometry(0.04, 0.12, h * 0.45, 5), M.bare); br.position.y = h * 0.5; br.rotation.set((r() - 0.5) * 1.4, r() * 6, (r() - 0.5) * 1.4); br.translateY(h * 0.2); g.add(br); }
  } else { const c = mesh(new THREE.ConeGeometry(2 + r() * 1.5, h * 0.75, 8), M.leaf); c.position.y = h * 0.6; g.add(c); }
  g.position.set(x, 0, z); return g;
}
function town(lit, seedBase = 100, zSide = 1, x0 = -300, x1 = 300, zNear = 28) {
  const g = new THREE.Group(); const r = rng(seedBase);
  for (let row = 0; row < 3; row++) {
    for (let x = x0; x < x1; x += 16 + r() * 10) {
      const z = zSide * (zNear + row * 22 + r() * 5);
      g.add(house(x, z, zSide > 0 ? 0 : Math.PI, seedBase + Math.floor(x * 7) + row * 1000, lit));
      if (r() < 0.5) g.add(tree(x + 8, z + zSide * 9, seedBase + x + row, true));
    }
    const road = mesh(new THREE.BoxGeometry(x1 - x0, 0.06, 7), M.road, false); road.position.set((x0 + x1) / 2, -0.37, zSide * (zNear - 9 + row * 22)); g.add(road);
  }
  return g;
}

// ---------------- particles (fire additive, smoke normal) ----------------
function fireSprites(n, seed) {
  const arr = []; const r = rng(seed);
  for (let i = 0; i < n; i++) { const m = new THREE.SpriteMaterial({ map: fireTex, blending: THREE.AdditiveBlending, depthWrite: false, transparent: true, color: 0xffffff });
    const s = new THREE.Sprite(m); s.userData = { ph: r(), sp: 0.6 + r() * 0.8, ox: (r() - 0.5), oz: (r() - 0.5), sz: 0.6 + r() * 0.8 }; scene.add(s); arr.push(s); }
  return arr;
}
// a flame source: base point, radius, height, intensity(t). Each sprite cycles: rises, shrinks, fades.
function updateFire(sprites, base, rad, hgt, k, t, size = 1, alpha = 0.85) {
  for (const s of sprites) {
    const u = s.userData; const life = ((t * u.sp + u.ph) % 1);
    s.position.set(base.x + u.ox * rad * (1 - life * 0.6), base.y + life * hgt * k, base.z + u.oz * rad * (1 - life * 0.6));
    const sc = size * u.sz * (rad * 0.9 + 0.4) * (1 - life * 0.55) * (0.4 + 0.6 * k);
    s.scale.set(sc, sc * 1.35, 1);
    s.material.opacity = k * Math.sin(Math.PI * Math.min(1, life * 1.15)) * alpha;
    s.material.color.setRGB(1, 0.75 - life * 0.35, 0.45 - life * 0.4);
    s.visible = k > 0.01;
  }
}
function smokeSprites(n, seed, color = 0x151515) {
  const arr = []; const r = rng(seed);
  for (let i = 0; i < n; i++) { const m = new THREE.SpriteMaterial({ map: puffTex, depthWrite: false, transparent: true, color, fog: true });
    const s = new THREE.Sprite(m); s.userData = { r1: r(), r2: r(), r3: r(), r4: r(), rot: r() * 6.28 }; m.rotation = s.userData.rot; scene.add(s); arr.push(s); }
  return arr;
}

// ---------------- lights ----------------
let sun, hemi;
if (NIGHT) {
  scene.background = new THREE.Color(0x070b14); scene.fog = new THREE.FogExp2(0x0a0f1a, 0.0032);
  hemi = new THREE.HemisphereLight(0x6a7daa, 0x22222a, 0.9); scene.add(hemi);
  const moon = new THREE.DirectionalLight(0x9fb4e0, 1.1); moon.position.set(-200, 300, 150); scene.add(moon);
} else {
  scene.background = new THREE.Color(0x9aa3ab); scene.fog = new THREE.Fog(0xa3abb2, 400, 3200);
  hemi = new THREE.HemisphereLight(0xc9d3dc, 0x4b4a3e, 1.0); scene.add(hemi);
  sun = new THREE.DirectionalLight(0xfff1dc, 1.5); sun.position.set(-260, 320, 220); sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048); Object.assign(sun.shadow.camera, { left: -140, right: 140, top: 140, bottom: -140, near: 10, far: 1400 }); sun.shadow.bias = -0.0004; sun.shadow.normalBias = 0.05;
  scene.add(sun); scene.add(sun.target);
}
function streetLamp(x, z) {
  const g = new THREE.Group();
  const pole = mesh(new THREE.CylinderGeometry(0.08, 0.1, 7, 8), M.steelDark, false); pole.position.y = 3.1; g.add(pole);
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.3, 10, 8), new THREE.MeshBasicMaterial({ color: 0xffd7a0 })); head.position.y = 6.6; g.add(head);
  const gl = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowTex, color: 0xffb060, blending: THREE.AdditiveBlending, depthWrite: false, transparent: true, opacity: 0.55 })); gl.scale.set(5, 5, 1); gl.position.y = 6.6; g.add(gl);
  const pl = new THREE.PointLight(0xffb36b, 60, 40, 1.6); pl.position.y = 6.3; g.add(pl);
  g.position.set(x, 0, z); return g;
}

// ---------------- train placement ----------------
// s = along-track coordinate of a car's center (x). Cars placed behind the head with car lengths + gaps.
function buildTrain(kinds) {
  const cars = kinds.map((k, i) => car(k, 1000 + i)); let off = 0; const offs = [];
  cars.forEach((c, i) => { if (i) off += cars[i - 1].userData.L / 2 + GAP + c.userData.L / 2; offs.push(off); scene.add(c); });
  return { cars, offs };
}
function spinWheels(c, dist) { for (const t of c.userData.trucks) for (const w of t.userData.ws) w.rotation.z = -dist / WR; }

// =====================================================================
// SCENES
// =====================================================================
const S = {};
let fadeIn = 0.4, fadeOut = 0.4, DUR = Number(CFG.dur || 10);

// ---- T1: night, train rolls through a small town (camera low beside the track, slow dolly) ----
S.T1 = () => {
  scene.add(ground()); scene.add(track(-900, 900)); scene.add(track(-900, 900, 4.6));
  scene.add(town(true, 300, 1, -260, 260, 30)); scene.add(town(true, 500, -1, -260, 260, 34));
  for (let x = -240; x <= 240; x += 48) { scene.add(streetLamp(x, -12)); }
  const kinds = consist(60); const T = buildTrain(kinds);
  const v = 19.2; // 43 mph
  const head = new THREE.SpotLight(0xfff1d0, 900, 260, 0.32, 0.5, 1.2); scene.add(head); scene.add(head.target);
  return t => {
    const hx = -60 + v * (t + 0.0);
    T.cars.forEach((c, i) => { const x = hx - T.offs[i]; c.position.set(x, 0, 0); c.visible = x > -330 && x < 330; spinWheels(c, x); });
    const lc = T.cars[0]; head.position.set(lc.position.x + 11, 2.9, 0); head.target.position.set(lc.position.x + 80, 0, 0);
    const k = t / DUR;
    camera.position.set(lerp(-40, 6, k), 2.6, 24); camera.lookAt(lerp(-10, 26, k), 3.0, -2);
  };
};

// ---- T2: tracking shot on the burning wheelset of the hopper car, passing a hot bearing detector ----
S.T2 = () => {
  scene.add(ground()); scene.add(track(-1200, 1200));
  scene.add(town(true, 700, 1, -500, 500, 40));
  for (let x = -480; x <= 480; x += 60) scene.add(streetLamp(x, 22));
  const kinds = consist(40); const T = buildTrain(kinds);
  // detector box between the rails + wayside bungalow
  const DX = CFG.det ?? 96;
  const det = mesh(new THREE.BoxGeometry(0.5, 0.18, 0.35), std(0x8a8f30, 0.5, 0.3)); det.position.set(DX, RAIL_Y - 0.02, -GAUGE / 2 - 0.25); scene.add(det);
  const bung = mesh(new THREE.BoxGeometry(2.4, 2.6, 2.4), std(0x9da3a8, 0.8)); bung.position.set(DX + 6, 0.9, -7); scene.add(bung);
  const beam = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.12, 0.9, 8, 1, true), new THREE.MeshBasicMaterial({ color: 0xff3030, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false })); scene.add(beam);
  const fire = fireSprites(36, 21); const sparks = fireSprites(24, 22);
  const fl = new THREE.PointLight(0xff7a2a, 0, 14, 1.5); scene.add(fl);
  const v = 19.2; const hc = T.cars[HOT];
  if (CFG.label) label('L1 bearing', '23rd railcar · hopper car', () => { const b = hc.userData.trucks[0].userData.ws[1].getObjectByName('brgL'); return b.getWorldPosition(new THREE.Vector3()); }, CFG.label, { dx: -160, dy: -150 });
  return t => {
    const sHot = -6 + v * t;                 // hot car center position
    const hx = sHot + T.offs[HOT];
    T.cars.forEach((c, i) => { const x = hx - T.offs[i]; c.position.set(x, 0, 0); c.visible = Math.abs(x - sHot) < 260; spinWheels(c, x); });
    // the failing L1 bearing: on the leading truck's front wheelset, left (south, -z) side
    const ws = hc.userData.trucks[0].userData.ws[1]; const brg = ws.getObjectByName('brgL');
    const heat = CFG.heat ?? 1;
    brg.material = brg.material.clone(); brg.material.emissive = new THREE.Color(0xff5a10); brg.material.emissiveIntensity = 2.2 * heat;
    const bp = brg.getWorldPosition(new THREE.Vector3());
    updateFire(fire, bp.clone().add(new THREE.Vector3(-0.15, 0.05, -0.12)), 0.4, 2.0, heat * (0.85 + 0.15 * Math.sin(t * 23)), t * 1.6, 1.2);
    for (const s of fire) s.position.x -= (s.position.y - bp.y) * 1.2;   // flame trails backward in the wind of motion
    updateFire(sparks, bp, 0.2, 0.5, heat * 0.8, t * 3.1, 0.25);
    for (const s of sparks) { const u = s.userData; const life = ((t * 3.1 * u.sp + u.ph) % 1); s.position.x = bp.x - life * 5 - u.ox; s.position.y = bp.y - 0.1 - life * life * 0.4; }
    fl.position.copy(bp).add(new THREE.Vector3(0, 0.4, -0.6)); fl.intensity = 50 * heat * (0.8 + 0.2 * Math.sin(t * 31));
    // detector beam flashes as the hot wheel passes over it
    const near = 1 - clamp(Math.abs(bp.x - DX) / 3);
    beam.position.set(DX, RAIL_Y + 0.25, -GAUGE / 2 - 0.25); beam.material.opacity = near * 0.8;
    det.material.emissive = new THREE.Color(0xff2020); det.material.emissiveIntensity = near * 1.5;
    // camera rides alongside the hopper's leading truck, then lets it pass the detector
    const camX = bp.x + (CFG.camLead ?? -3.2);
    camera.position.set(camX - 0.6, 1.5, -8.2); camera.lookAt(camX + 2.6, 1.0, 0);
  };
};

// ---- T3: bearing cutaway, rollers spinning, heat rising (studio look) ----
S.T3 = () => {
  scene.background = new THREE.Color(0x0b1016); scene.fog = null;
  const key = new THREE.DirectionalLight(0xffffff, 2.0); key.position.set(3, 5, 4); scene.add(key);
  const rim = new THREE.DirectionalLight(0x88aaff, 1.0); rim.position.set(-4, 2, -3); scene.add(rim);
  const steel = std(0xb8bcc2, 0.28, 0.95);
  const cupMat = std(0x9a9ea4, 0.3, 0.9, { side: THREE.DoubleSide });
  const G = new THREE.Group(); scene.add(G);
  // axle (journal) along x
  const ax = mesh(new THREE.CylinderGeometry(0.08, 0.08, 1.2, 40), steel); ax.rotation.z = Math.PI / 2; ax.position.x = -0.35; G.add(ax);
  // outer cup, cut open (270 degrees) to show rollers
  const cup = mesh(new THREE.CylinderGeometry(0.17, 0.17, 0.32, 64, 1, true, 0.6, Math.PI * 1.5), cupMat); cup.rotation.z = Math.PI / 2; G.add(cup);
  for (const s of [-1, 1]) { const ring = mesh(new THREE.TorusGeometry(0.165, 0.012, 10, 64, Math.PI * 1.5), cupMat); ring.rotation.y = Math.PI / 2; ring.rotation.x = 0.6; ring.position.x = s * 0.16; G.add(ring); }
  const cone = mesh(new THREE.CylinderGeometry(0.105, 0.105, 0.3, 48), steel); cone.rotation.z = Math.PI / 2; G.add(cone);
  const rollers = new THREE.Group(); G.add(rollers); const rmat = std(0xd0d3d8, 0.22, 0.95);
  for (let row = 0; row < 2; row++) for (let i = 0; i < 18; i++) { const a = i / 18 * Math.PI * 2; const rl = mesh(new THREE.CylinderGeometry(0.026, 0.03, 0.11, 18), rmat); rl.rotation.z = Math.PI / 2; rl.position.set(row ? 0.07 : -0.07, Math.cos(a) * 0.138, Math.sin(a) * 0.138); rollers.add(rl); }
  const glow = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowTex, color: 0xff5010, blending: THREE.AdditiveBlending, depthWrite: false, transparent: true, opacity: 0 })); glow.scale.set(0.9, 0.9, 1); scene.add(glow);
  const heatPL = new THREE.PointLight(0xff5a1a, 0, 3, 1.5); heatPL.position.set(0.1, 0.1, 0.4); scene.add(heatPL);
  const smoke = smokeSprites(40, 33, 0x8a8a8a);
  const H0 = CFG.heatAt ?? 3.0;
  if (CFG.lab1) label('Rollers', 'they let the axle spin smoothly', new THREE.Vector3(0.07, 0.15, 0.0), CFG.lab1, { dx: 160, dy: -140, until: CFG.lab1u ?? 1e9 });
  if (CFG.lab2) label('Friction → heat', 'a failing bearing gets very hot', new THREE.Vector3(0.0, -0.1, 0.12), CFG.lab2, { dx: 170, dy: 120, red: true });
  return t => {
    const heat = seg(t, H0, DUR - H0 - 0.5);
    rollers.rotation.x = t * 5.5; cone.rotation.x = t * 5.5; ax.rotation.x = t * 5.5;
    const hc = new THREE.Color().setRGB(1, lerp(0.35, 0.75, heat), lerp(0.05, 0.4, heat));
    for (const m of [cupMat, rmat]) { m.emissive = hc; m.emissiveIntensity = heat * 1.6; }
    glow.position.set(0.0, 0.0, 0.15); glow.material.opacity = heat * 0.8; heatPL.intensity = heat * 8;
    smoke.forEach((s, i) => { const u = s.userData; const life = (t * 0.35 + u.r1) % 1; s.position.set(-0.1 + u.r2 * 0.25, 0.15 + life * 0.6, 0.05 + u.r3 * 0.15); const sc = 0.08 + life * 0.25; s.scale.set(sc, sc, 1); s.material.opacity = heat * 0.35 * Math.sin(Math.PI * life); });
    const a = 0.9 + t * 0.06;
    camera.position.set(Math.cos(a) * 0.95, 0.38 + 0.03 * Math.sin(t * 0.5), Math.sin(a) * 0.95); camera.lookAt(-0.04, 0, 0);
  };
};

// ---- T4: derailment — axle separates, cars pile up, fire ----
S.T4 = () => {
  scene.add(ground()); scene.add(track(-1200, 1200)); scene.add(track(-1200, 1200, 4.6));
  scene.add(town(true, 900, 1, -400, 400, 46)); scene.add(town(true, 1100, -1, -400, 200, 52));
  for (let x = -380; x <= 380; x += 56) scene.add(streetLamp(x, 30));
  const kinds = consist(75); const T = buildTrain(kinds);
  const v = 19.2, TE = CFG.te ?? 2.2;               // derailment begins at TE
  const NDER = 38, last = HOT + NDER - 1;
  const r = rng(77); const P = [];                  // per derailed car: final displacement and pose
  let pile = 0;
  for (let i = HOT; i < T.cars.length; i++) {
    const k = i - HOT; const der = i <= last;
    if (der) { const D = 10 + k * (T.cars[i].userData.L + GAP) * 0.62 - Math.min(k, 14) * 0.4;   // cars squeeze into ~62% of their length
      const sgn = (k % 2 ? 1 : -1) * (r() < 0.8 ? 1 : -1);
      P[i] = { D, yaw: sgn * (0.35 + r() * 0.9) * (k < 22 ? 1 : 0.5), lat: sgn * (1.5 + r() * 6) * (k < 22 ? 1 : 0.5), roll: (r() < 0.45 ? sgn * (0.6 + r() * 0.9) : sgn * r() * 0.25), up: k > 2 && k < 20 && r() < 0.35 ? 1.5 + r() * 2.5 : 0 };
      pile = Math.max(pile, k);
    } else P[i] = { D: 10 + NDER * (18.6) * 0.62 + (k - NDER) * 0.0 + 8, yaw: 0, lat: 0, roll: 0, up: 0 };
  }
  const fireGroups = []; for (let f = 0; f < 10; f++) fireGroups.push({ sp: fireSprites(60, 400 + f), k: HOT + 1 + f * 3 });
  const ditch = fireSprites(60, 499);
  const lights = [0, 1, 2].map(() => { const l = new THREE.PointLight(0xff7a2a, 0, 120, 1.4); scene.add(l); return l; });
  const smoke = smokeSprites(90, 501, 0x1a1715);
  const dust = smokeSprites(50, 502, 0x2e2a26);
  const head = new THREE.SpotLight(0xfff1d0, 900, 260, 0.32, 0.5, 1.2); scene.add(head); scene.add(head.target);
  return t => {
    const X0 = -45 - v * TE + T.offs[HOT]; const hx0 = X0 + v * t;                           // head position if no derailment (front part keeps going)
    const sHotTE = -20 + v * TE - T.offs[HOT] + T.offs[0];
    T.cars.forEach((c, i) => {
      let x = hx0 - T.offs[i], y = 0, z = 0, yaw = 0, roll = 0, pitch = 0;
      if (i >= HOT) {
        const p = P[i]; const xTE = X0 + v * TE - T.offs[i];
        if (t > TE) { const Tm = 2 * p.D / v; const u = clamp((t - TE) / Tm); const f = 1 - (1 - u) * (1 - u); x = xTE + p.D * f;
          const g = ease(clamp((u - 0.15) / 0.85)); yaw = p.yaw * g; z = p.lat * g; roll = p.roll * g * g; y = (p.up * Math.sin(Math.PI * Math.min(1, u * 1.3)) * 0.6 + p.up * 0.4 * g) - (p.yaw ? 0.35 * g : 0);
          if (i === HOT) { pitch = -0.12 * seg(t, TE, 0.4); y -= 0.5 * seg(t, TE, 0.4); }
        } else x = xTE + v * (t - TE);
      }
      c.position.set(x, y, z); c.rotation.set(roll, yaw, pitch); c.visible = x > -260 && x < 300; spinWheels(c, i < HOT ? x : Math.min(x, x));
    });
    const lc = T.cars[0]; head.position.set(lc.position.x + 11, 2.9, 0); head.target.position.set(lc.position.x + 80, 0, 0);
    // fires
    let li = 0;
    for (const fg of fireGroups) { const c = T.cars[Math.min(fg.k, T.cars.length - 1)]; const k = seg(t, TE + 1.4 + (fg.k - HOT) * 0.08, 1.6);
      updateFire(fg.sp, c.position.clone().add(new THREE.Vector3(0, 1.0, 0)), 7, 14 + (fg.k % 3) * 4, k * (0.85 + 0.15 * Math.sin(t * 7 + fg.k)), t * 0.9 + fg.k, 1.5, 0.4);
      if (li < 3 && fg.k % 3 === 0) { lights[li].position.copy(c.position).add(new THREE.Vector3(0, 6, 8)); lights[li].intensity = 2600 * k * (0.85 + 0.15 * Math.sin(t * 9 + li)); li++; } }
    const pc = T.cars[HOT + 8].position;
    updateFire(ditch, new THREE.Vector3(pc.x - 20, 0.2, -5.5), 22, 6, seg(t, TE + 2.4, 2.0) * (0.9 + 0.1 * Math.sin(t * 5)), t * 0.8, 2.0, 0.45);
    for (const s of ditch) s.position.x += s.userData.ox * 60;
    smoke.forEach(s => { const u = s.userData; const age = t - (TE + 2.0) - u.r1 * 6; const life = age / 7; s.visible = age > 0;
      s.position.set(pc.x - 40 + u.r2 * 80 + age * 1.6, 6 + age * 5.5, -6 + u.r3 * 12); const sc = 8 + age * 5; s.scale.set(sc, sc, 1); s.material.opacity = 0.75 * clamp(age / 1.2) * clamp(1.4 - life * 0.25); });
    dust.forEach(s => { const u = s.userData; const age = t - TE - 0.3 - u.r1 * 2.4; s.visible = age > 0 && age < 5;
      s.position.set(T.cars[HOT + Math.floor(u.r2 * 24)].position.x, 1.5 + age * 1.2, (u.r3 - 0.5) * 14); const sc = 4 + age * 3; s.scale.set(sc, sc, 1); s.material.opacity = 0.5 * Math.sin(Math.PI * clamp(age / 5)); });
    // camera: high, slightly ahead, slow push in, a small shake at impact
    const sh = 0.25 * seg(t, TE, 0.2) * (1 - seg(t, TE + 1.0, 2.0));
    camera.position.set(-40 + t * 1.2 + Math.sin(t * 41) * sh, 32 - t * 0.5 + Math.sin(t * 37) * sh, 78 - t * 1.5); camera.lookAt(-60 + t * 2.0, 2, 0);
  };
};

// ---- T5/T6: vent and burn — five tank cars beside a trench and pit; charges; fireball; black column ----
function ventWorld() {
  scene.add(ground());
  scene.add(track(-1500, 1500, -26)); scene.add(track(-1500, 1500, -30.6));
  const pad = mesh(new THREE.BoxGeometry(160, 0.4, 70), M.dirt, false); pad.position.set(0, -0.35, 0); scene.add(pad);
  const pit = mesh(new THREE.BoxGeometry(24, 0.5, 16), std(0x2a241e, 1), false); pit.position.set(-8, -0.3, 22); scene.add(pit);
  for (const [x, z, w, d] of [[-8, 30.5, 26, 1.5], [-8, 13.5, 26, 1.5], [-21.5, 22, 1.5, 18], [5.5, 22, 1.5, 18]]) { const b = mesh(new THREE.BoxGeometry(w, 1.6, d), M.dirt); b.position.set(x, 0.3, z); scene.add(b); }
  const tr = mesh(new THREE.BoxGeometry(60, 0.5, 2.2), std(0x2a241e, 1), false); tr.position.set(0, -0.3, 10.5); scene.add(tr);
  const tanks = []; const r = rng(901);
  for (let i = 0; i < 5; i++) { const c = car('tank', 2000 + i); c.position.set(-34 + i * 15 + r() * 3, -0.9, 2 + (r() - 0.5) * 5); c.rotation.set((r() < 0.5 ? 1 : -1) * (0.15 + r() * 0.45), (r() - 0.5) * 0.7, (r() - 0.5) * 0.08); scene.add(c); tanks.push(c); }
  // other wreck debris
  for (let i = 0; i < 6; i++) { const c = car(i % 2 ? 'hopper' : 'box', 2100 + i); c.position.set(-90 + i * 34 + r() * 6, -0.6, -12 - r() * 6); c.rotation.set((r() - 0.5) * 0.9, (r() - 0.5) * 1.2, (r() - 0.5) * 0.1); scene.add(c); }
  scene.add(town(false, 1300, 1, -500, 500, 120)); scene.add(town(false, 1500, -1, -500, 500, 110));
  for (let i = 0; i < 60; i++) { const a = r() * 6.28, d = 90 + r() * 300; scene.add(tree(Math.cos(a) * d, Math.sin(a) * d * 0.6 + (Math.sin(a) > 0 ? 50 : -50), 3000 + i, true)); }
  return tanks;
}
function ventFX(tanks, TD) {
  const flashes = tanks.map((_, i) => { const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowTex, color: 0xffffff, blending: THREE.AdditiveBlending, depthWrite: false, transparent: true, opacity: 0 })); scene.add(s); return s; });
  const jets = tanks.map((_, i) => fireSprites(34, 700 + i));
  const pitFire = fireSprites(70, 760);
  const fl = new THREE.PointLight(0xff8a3a, 0, 400, 1.2); fl.position.set(-8, 14, 15); scene.add(fl);
  const N = 520; const smoke = smokeSprites(N, 800, 0x111111);
  const wind = new THREE.Vector3(5.5, 0, -1.2);
  return t => {
    const dt = t - TD;
    tanks.forEach((c, i) => { const p = c.position; const f = flashes[i]; const fa = dt > 0 ? Math.exp(-dt * 6) : 0;
      f.position.set(p.x, p.y + 3.5, p.z); f.scale.set(8 + 22 * (1 - fa), 8 + 22 * (1 - fa), 1); f.material.opacity = fa;
      const k = seg(t, TD + 0.05 + i * 0.04, 0.6) * (0.85 + 0.15 * Math.sin(t * 13 + i));
      updateFire(jets[i], p.clone().add(new THREE.Vector3(0, 3.2, 0)), 2.6, 24, k, t * 0.9 + i * 0.3, 2.6);
      for (const s of jets[i]) { s.position.x += (s.position.y - p.y) * 0.25; }
    });
    updateFire(pitFire, new THREE.Vector3(-8, 0.6, 22), 10, 12, seg(t, TD + 1.2, 2.5), t * 0.8, 1.6);
    fl.intensity = dt > 0 ? (5000 * Math.exp(-dt * 3) + 500) * seg(t, TD, 0.05) : 0;
    // smoke column: particles born continuously after TD
    smoke.forEach((s, i) => { const u = s.userData; const born = TD + 0.3 + 60 * Math.pow(i / N, 1.7); const age = t - born;
      s.visible = age > 0; if (!s.visible) return;
      const rise = 26 * Math.pow(age, 0.82) * (0.8 + u.r1 * 0.4);       // buoyant column slowing with height
      const spread = 6 + age * (2.4 + u.r2 * 2.0);
      const src = tanks[i % 5].position;
      const h = Math.min(rise, 420 + u.r3 * 60);
      const cap = clamp((rise - 380) / 200);                              // flatten and drift at the top
      s.position.set(src.x + Math.cos(u.rot) * spread * (0.6 + cap * 2.5) + wind.x * age * (0.3 + cap * 2), 4 + h + cap * u.r4 * 40, src.z + Math.sin(u.rot) * spread * 0.8 + wind.z * age);
      const sc = 15 + age * (4.5 + u.r4 * 3) + cap * 60; s.scale.set(sc, sc, 1);
      s.material.opacity = 0.92 * clamp(age / 0.6);
      const sh = 0.06 + 0.12 * u.r2 + clamp(1 - age / 2) * 0.25;           // a little fire glow at the base
      s.material.color.setRGB(sh + clamp(1 - age / 2) * 0.35, sh + clamp(1 - age / 2) * 0.12, sh);
    });
  };
}
S.T5 = () => {
  const tanks = ventWorld(); const TD = CFG.td ?? 7.0; const fx = ventFX(tanks, TD);
  if (CFG.labTanks) label('5 vinyl chloride tank cars', 'not punctured in the crash', tanks[2].position.clone().add(new THREE.Vector3(0, 3, 0)), CFG.labTanks, { dx: 120, dy: -170, until: TD - 0.6 });
  return t => {
    fx(t);
    const k = t / DUR; const sh = 0.7 * Math.exp(-Math.max(0, t - TD) * 3) * (t > TD ? 1 : 0);
    camera.position.set(lerp(70, 95, k) + Math.sin(t * 43) * sh, lerp(14, 34, ease(k)) + Math.sin(t * 37) * sh, lerp(95, 150, ease(k)));
    camera.lookAt(-6, lerp(4, 40, ease(clamp((t - TD) / 6))), 4);
  };
};
S.T6 = () => {
  const tanks = ventWorld(); const OFF = CFG.off ?? 30; const fx = ventFX(tanks, 0.0);
  scene.fog = new THREE.Fog(0xa3abb2, 600, 4200);
  return t => {
    fx(t + OFF);
    const k = t / DUR;
    camera.position.set(lerp(340, 310, k), lerp(55, 66, k), lerp(480, 440, k)); camera.lookAt(-10, lerp(150, 162, k), 0);
  };
};

// ---------------- run ----------------
const update = S[SCENE]();
window.renderAt = t => {
  update(t);
  updateLabels(t);
  fadeEl.style.opacity = Math.max(1 - clamp(t / fadeIn), seg(t, DUR - fadeOut, fadeOut));
  renderer.render(scene, camera);
};
if (CFG.notag) document.getElementById('tag').style.display = 'none';
window.ready = true;
