// Deterministic 3D scenes for the UPS 2976 episode. window.renderAt(t) draws clip time t (seconds).
// Generic three-engine widebody (no airline livery). Everything is computed from t, so frames can be rendered in any order.
import * as THREE from 'three';
import { RoomEnvironment } from './RoomEnvironment.js';

const Q = new URLSearchParams(location.search);
const SCENE = Q.get('scene') || 'C';
const CFG = JSON.parse(Q.get('cfg') || '{}');            // label times etc.
const W = 1920, H = 1080;
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const ease = x => { x = clamp(x); return x * x * (3 - 2 * x); };
const seg = (t, a, d) => ease((t - a) / d);
const lerp = (a, b, k) => a + (b - a) * k;
function rng(seed) { let s = seed >>> 0; return () => { s += 0x6D2B79F5; let r = Math.imul(s ^ (s >>> 15), 1 | s); r ^= r + Math.imul(r ^ (r >>> 7), 61 | r); return ((r ^ (r >>> 14)) >>> 0) / 4294967296; }; }

// ---------------- renderer ----------------
const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setSize(W, H); renderer.setPixelRatio(1);
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.05;
renderer.outputColorSpace = THREE.SRGBColorSpace;
document.body.prepend(renderer.domElement);
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(35, W / H, 0.02, 30000);
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;

// ---------------- overlay labels ----------------
const ov = document.getElementById('ov'); const fade = document.getElementById('fade');
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

// ---------------- materials ----------------
const M = {
  body: new THREE.MeshStandardMaterial({ color: 0xf1f1ee, roughness: 0.42, metalness: 0.15, envMapIntensity: 0.6 }),
  belly: new THREE.MeshStandardMaterial({ color: 0xb9bdc4, roughness: 0.5, metalness: 0.2, envMapIntensity: 0.5 }),
  wing: new THREE.MeshStandardMaterial({ color: 0xc7ccd3, roughness: 0.48, metalness: 0.35, envMapIntensity: 0.6 }),
  nacelle: new THREE.MeshStandardMaterial({ color: 0xe6e7e8, roughness: 0.35, metalness: 0.3, envMapIntensity: 0.7 }),
  dark: new THREE.MeshStandardMaterial({ color: 0x15171b, roughness: 0.6, metalness: 0.4 }),
  glass: new THREE.MeshStandardMaterial({ color: 0x0c1118, roughness: 0.1, metalness: 0.8 }),
  tire: new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.9 }),
  stripe: new THREE.MeshStandardMaterial({ color: 0x3f5d8a, roughness: 0.5, metalness: 0.2 }),
};

// ---------------- the aircraft (generic tri-jet) ----------------
function lathe(profile, seg = 48) { return new THREE.LatheGeometry(profile.map(([r, y]) => new THREE.Vector2(r, y)), seg); }
function along(geom) { geom.rotateZ(-Math.PI / 2); return geom; }       // lathe axis y -> world x
function flatShape(pts, depth) {                                          // pts in (x, z) top view -> horizontal slab
  const s = new THREE.Shape(); pts.forEach(([x, z], i) => i ? s.lineTo(x, z) : s.moveTo(x, z));
  const g = new THREE.ExtrudeGeometry(s, { depth, bevelEnabled: true, bevelThickness: depth * 0.35, bevelSize: 0.12, bevelSegments: 2 });
  g.rotateX(Math.PI / 2); g.translate(0, depth / 2, 0); return g;
}
function sideShape(pts, depth) {                                          // pts in (x, y) side view -> vertical slab
  const s = new THREE.Shape(); pts.forEach(([x, y], i) => i ? s.lineTo(x, y) : s.moveTo(x, y));
  const g = new THREE.ExtrudeGeometry(s, { depth, bevelEnabled: true, bevelThickness: 0.15, bevelSize: 0.1, bevelSegments: 2 });
  g.translate(0, 0, -depth / 2); return g;
}
function mesh(g, m, shadow = true) { const o = new THREE.Mesh(g, m); o.castShadow = shadow; o.receiveShadow = true; return o; }

function makeEngine(len = 6.4, r = 1.5) {
  const g = new THREE.Group();
  const prof = [[0.0, len / 2 + 0.6], [0.55, len / 2 + 0.35], [0.7, len / 2], [r * 0.9, len / 2], [r, len / 2 - 0.4], [r * 1.02, 0], [r * 0.92, -len / 2 + 0.6], [r * 0.62, -len / 2], [0.35, -len / 2 - 0.9], [0, -len / 2 - 1.0]];
  const shell = mesh(along(lathe([[r * 0.88, len / 2], [r, len / 2 - 0.4], [r * 1.02, 0], [r * 0.92, -len / 2 + 0.6], [r * 0.66, -len / 2]])), M.nacelle);
  shell.material = M.nacelle; g.add(shell);
  const inlet = mesh(along(new THREE.CylinderGeometry(r * 0.86, r * 0.86, 0.2, 40)), M.dark); inlet.position.x = len / 2 - 0.25; g.add(inlet);
  const spinner = mesh(along(new THREE.ConeGeometry(0.42, 0.9, 24)), M.nacelle); spinner.position.x = len / 2 - 0.1; g.add(spinner);
  const core = mesh(along(lathe([[r * 0.6, -len / 2 + 0.2], [0.5, -len / 2 - 0.8], [0.05, -len / 2 - 1.1]])), M.belly); g.add(core);
  return g;
}

function makePlane() {
  const P = new THREE.Group();
  const FY = 5.6, FX = 3.0;                                       // fuselage axis height and x offset (origin = main gear contact)
  const fusProf = [[0, 31], [0.9, 30.7], [1.7, 30.0], [2.4, 28.8], [2.85, 27.2], [3.0, 25.0], [3.0, -17], [2.8, -22], [2.3, -26], [1.6, -29], [0.8, -30.8], [0, -31.3]];
  const fus = mesh(along(lathe(fusProf, 56)), M.body); fus.position.set(FX, FY, 0); P.add(fus);
  const belly = mesh(along(new THREE.CylinderGeometry(2.95, 2.95, 40, 40, 1, true, Math.PI * 0.62, Math.PI * 0.76)), M.belly); belly.position.set(FX + 2, FY - 0.05, 0); P.add(belly);
  const stripe = mesh(along(new THREE.CylinderGeometry(3.02, 3.02, 46, 48, 1, true, Math.PI * 0.08, Math.PI * 0.07)), M.stripe, false); stripe.position.set(FX + 1, FY, 0); P.add(stripe);
  const stripe2 = stripe.clone(); stripe2.rotation.x = Math.PI - 0.0; stripe2.scale.y = 1; stripe2.rotation.set(Math.PI, 0, 0); P.add(stripe2);
  const wind = mesh(new THREE.BoxGeometry(1.6, 0.5, 2.8), M.glass, false); wind.position.set(FX + 28.0, FY + 1.75, 0); wind.rotation.z = -0.55; P.add(wind);
  // wings: root chord 12 m, 35 deg sweep, span 26 m per side
  const wingPts = [[9, 0], [-9.5, 25.5], [-13, 25.5], [-4, 0]];
  for (const side of [1, -1]) {
    const wg = mesh(flatShape(wingPts, 0.6), M.wing); wg.scale.z = side; wg.position.set(FX, FY - 1.7, 0); wg.rotation.x = -side * 0.1; P.add(wg);
    const wl = mesh(sideShape([[0, 0], [-1.8, 2.6], [-3.0, 2.6], [-2.6, 0]], 0.25), M.wing); wl.position.set(FX - 9.6, FY - 1.7 + 2.6, side * 25.5); P.add(wl);
  }
  // horizontal stabilizer and fin
  for (const side of [1, -1]) { const hs = mesh(flatShape([[0, 0], [-5.5, 9.5], [-8, 9.5], [-6.5, 0]], 0.35), M.wing); hs.scale.z = side; hs.position.set(FX - 21, FY + 0.9, 0); P.add(hs); }
  const fin = mesh(sideShape([[-18, 2.6], [-26.5, 11.5], [-30.5, 11.5], [-30.5, 2.6]], 0.6), M.body); fin.position.set(FX, FY, 0); P.add(fin);
  // engines: two on wing pylons, one through the fin base
  const engs = {};
  for (const [name, side] of [['left', -1], ['right', 1]]) {
    const grp = new THREE.Group();
    const e = makeEngine(); grp.add(e);
    const py = mesh(new THREE.BoxGeometry(6.2, 1.9, 0.55), M.wing); py.position.set(-1.2, 1.9, 0); py.rotation.z = -0.08; grp.add(py);
    grp.position.set(FX + 3.6, FY - 3.6, side * 10.2);
    P.add(grp); engs[name] = grp;
  }
  const te = makeEngine(7.0, 1.55); te.position.set(FX - 21.5, FY + 4.4, 0); P.add(te); engs.tail = te;
  const fairing = mesh(along(new THREE.CylinderGeometry(1.6, 1.3, 7, 32)), M.body); fairing.position.set(FX - 21.0, FY + 3.4, 0); P.add(fairing);
  // landing gear
  const gear = (x, z, n) => { const leg = mesh(new THREE.CylinderGeometry(0.18, 0.18, 3.0, 10), M.dark); leg.position.set(x, 1.9, z); P.add(leg);
    for (let i = 0; i < n; i++) { const wh = mesh(new THREE.CylinderGeometry(0.62, 0.62, 0.45, 20), M.tire); wh.rotation.x = Math.PI / 2; wh.position.set(x + (n > 2 ? (i < 2 ? 0.8 : -0.8) : 0), 0.62, z + (i % 2 ? 0.35 : -0.35)); P.add(wh); } };
  gear(0, -4.8, 4); gear(0, 4.8, 4); gear(0, 0, 4); gear(FX + 24, 0, 2);
  P.userData = { FX, FY, engs };
  P.traverse(o => { if (o.isMesh) o.castShadow = true; });
  return P;
}

// ---------------- airport world ----------------
function world() {
  // sky dome with sunset gradient
  const sky = new THREE.Mesh(new THREE.SphereGeometry(15000, 32, 16), new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false, fog: false,
    uniforms: { top: { value: new THREE.Color(0x1b2a55) }, mid: { value: new THREE.Color(0x6d6fa8) }, hor: { value: new THREE.Color(0xffa25c) }, sun: { value: new THREE.Vector3(-0.85, 0.07, 0.52).normalize() } },
    vertexShader: 'varying vec3 vP; void main(){ vP = normalize(position); gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.0); }',
    fragmentShader: `uniform vec3 top,mid,hor,sun; varying vec3 vP;
      float hash(vec2 p){ return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453); }
      float noise(vec2 p){ vec2 i=floor(p), f=fract(p); f=f*f*(3.0-2.0*f); return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x),f.y); }
      float fbm(vec2 p){ float v=0.0, a=0.5; for(int i=0;i<5;i++){ v+=a*noise(p); p*=2.03; a*=0.5; } return v; }
      void main(){ float h = clamp(vP.y,0.0,1.0); vec3 c = mix(hor, mid, smoothstep(0.0,0.16,h)); c = mix(c, top, smoothstep(0.12,0.55,h));
        float s = max(dot(vP, sun),0.0);
        vec2 uv = vP.xz/(vP.y+0.12)*1.6; float cl = smoothstep(0.52,0.85,fbm(uv*vec2(1.0,3.5)+3.0)) * smoothstep(0.02,0.12,h) * (1.0-smoothstep(0.35,0.7,h));
        vec3 cloudCol = mix(vec3(0.95,0.55,0.45), vec3(1.0,0.78,0.55), pow(s,6.0));
        c = mix(c, cloudCol, cl*0.75);
        c += vec3(1.0,0.62,0.3)*pow(s,24.0)*1.2 + vec3(1.0,0.5,0.2)*pow(s,4.0)*0.3 + vec3(1.0,0.9,0.7)*smoothstep(0.9993,0.9997,s)*6.0;
        if (vP.y < 0.0) c = hor*0.55; gl_FragColor = vec4(c,1.0); }` }));
  scene.add(sky);
  scene.fog = new THREE.Fog(0xd39468, 900, 7000);
  const hemi = new THREE.HemisphereLight(0xb6c4ff, 0x5a4230, 1.0); scene.add(hemi);
  const fill = new THREE.DirectionalLight(0xc9d6ff, 0.9); fill.position.set(400, 300, 500); scene.add(fill);
  const fill2 = new THREE.DirectionalLight(0xffd2b0, 0.7); fill2.position.set(200, 150, -600); scene.add(fill2);
  const sun = new THREE.DirectionalLight(0xffbf86, 2.6); sun.position.set(-850, 80, 520); sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048); const sc = sun.shadow.camera; sc.left = -90; sc.right = 90; sc.top = 60; sc.bottom = -60; sc.near = 10; sc.far = 3000; sun.shadow.bias = -0.0004;
  scene.add(sun); scene.add(sun.target);
  // ground with subtle grass variation
  const cv = document.createElement('canvas'); cv.width = cv.height = 512; const g = cv.getContext('2d'); const r = rng(5);
  g.fillStyle = '#5b6340'; g.fillRect(0, 0, 512, 512); g.filter = 'blur(6px)';
  for (let i = 0; i < 700; i++) { g.fillStyle = `rgba(${60 + r() * 50},${70 + r() * 45},${35 + r() * 20},0.25)`; g.beginPath(); g.arc(r() * 512, r() * 512, 8 + r() * 40, 0, 7); g.fill(); }
  g.filter = 'none'; for (let i = 0; i < 6000; i++) { g.fillStyle = `rgba(${30 + r() * 60},${50 + r() * 50},${20 + r() * 20},0.25)`; g.fillRect(r() * 512, r() * 512, 1.5, 1.5); }
  const tex = new THREE.CanvasTexture(cv); tex.wrapS = tex.wrapT = THREE.RepeatWrapping; tex.repeat.set(90, 90); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8;
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(30000, 30000), new THREE.MeshStandardMaterial({ map: tex, roughness: 1 }));
  ground.rotation.x = -Math.PI / 2; ground.receiveShadow = true; scene.add(ground);
  // runway 3,300 m x 45 m from x=-2500 to x=800, markings and edge lights
  const rw = new THREE.Mesh(new THREE.PlaneGeometry(3300, 45), new THREE.MeshStandardMaterial({ color: 0x2c2d31, roughness: 0.95 }));
  rw.rotation.x = -Math.PI / 2; rw.position.set(-850, 0.02, 0); rw.receiveShadow = true; scene.add(rw);
  const white = new THREE.MeshStandardMaterial({ color: 0xe8e6df, roughness: 0.8 });
  const dash = new THREE.InstancedMesh(new THREE.PlaneGeometry(30, 0.9), white, 60);
  const m4 = new THREE.Matrix4(), q = new THREE.Quaternion().setFromEuler(new THREE.Euler(-Math.PI / 2, 0, 0)), s1 = new THREE.Vector3(1, 1, 1);
  for (let i = 0; i < 55; i++) { m4.compose(new THREE.Vector3(-2450 + i * 60, 0.04, 0), q, s1); dash.setMatrixAt(i, m4); } dash.receiveShadow = true; scene.add(dash);
  for (const z of [-21.5, 21.5]) { const e = new THREE.Mesh(new THREE.PlaneGeometry(3300, 0.9), white); e.rotation.x = -Math.PI / 2; e.position.set(-850, 0.04, z); e.receiveShadow = true; scene.add(e); }
  const lightMat = new THREE.MeshBasicMaterial({ color: 0xfff1c9 });
  const lights = new THREE.InstancedMesh(new THREE.SphereGeometry(0.35, 8, 6), lightMat, 240); let li = 0;
  for (let i = 0; i < 110; i++) for (const z of [-24, 24]) { m4.compose(new THREE.Vector3(-2500 + i * 30, 0.35, z), new THREE.Quaternion(), s1); lights.setMatrixAt(li++, m4); }
  lights.count = li; scene.add(lights);
  // blast fence, warehouses, storage yard, tanks, tower, tree lines
  const gray = new THREE.MeshStandardMaterial({ color: 0xa9a59c, roughness: 0.9 }), roof = new THREE.MeshStandardMaterial({ color: 0xc9c7c0, roughness: 0.8 });
  const fence = mesh(new THREE.BoxGeometry(1, 5, 140), new THREE.MeshStandardMaterial({ color: 0x8d8f93, roughness: 0.6, metalness: 0.4 })); fence.position.set(830, 2.5, 0); scene.add(fence);
  const box = (x, z, w, d, h, mat = gray) => { const b = mesh(new THREE.BoxGeometry(w, h, d), mat); b.position.set(x, h / 2, z); scene.add(b); const rf = mesh(new THREE.BoxGeometry(w + 0.5, 0.6, d + 0.5), roof); rf.position.set(x, h + 0.3, z); scene.add(rf); return b; };
  box(960, 10, 160, 120, 11);                                    // warehouse on the departure path
  box(1000, 200, 200, 90, 13); box(1050, -210, 180, 100, 12); box(1300, 260, 140, 120, 9); box(1400, -260, 160, 90, 10);
  const r2 = rng(9); for (let i = 0; i < 40; i++) box(1500 + r2() * 1600, (r2() - 0.5) * 1400, 40 + r2() * 90, 30 + r2() * 80, 6 + r2() * 12);
  const tankM = new THREE.MeshStandardMaterial({ color: 0xd8d4c8, roughness: 0.6, metalness: 0.3 });
  for (let i = 0; i < 6; i++) { const tk = mesh(new THREE.CylinderGeometry(9, 9, 12, 32), tankM); tk.position.set(1560 + (i % 3) * 24, 6, 40 + Math.floor(i / 3) * 24); scene.add(tk); }
  const tw = mesh(new THREE.CylinderGeometry(3, 4, 60, 16), gray); tw.position.set(-700, 30, -900); scene.add(tw);
  const cab = mesh(new THREE.CylinderGeometry(7, 6, 6, 16), M.glass); cab.position.set(-700, 63, -900); scene.add(cab);
  const treeM = new THREE.MeshStandardMaterial({ color: 0x2f3b24, roughness: 1 });
  const trees = new THREE.InstancedMesh(new THREE.ConeGeometry(6, 18, 7), treeM, 900); const r3 = rng(3); let ti = 0;
  for (let i = 0; i < 900; i++) { const a = r3() * Math.PI * 2, d = 2600 + r3() * 1800; m4.compose(new THREE.Vector3(-400 + Math.cos(a) * d, 8, Math.sin(a) * d), new THREE.Quaternion(), new THREE.Vector3(1, 0.7 + r3() * 0.8, 1)); trees.setMatrixAt(ti++, m4); }
  scene.add(trees);
  return { sun };
}

// ---------------- particles (fire + smoke), deterministic ----------------
function glowTex(inner, outer) {
  const c = document.createElement('canvas'); c.width = c.height = 128; const g = c.getContext('2d');
  const gr = g.createRadialGradient(64, 64, 0, 64, 64, 64); gr.addColorStop(0, inner); gr.addColorStop(0.4, outer); gr.addColorStop(1, 'rgba(0,0,0,0)');
  g.fillStyle = gr; g.fillRect(0, 0, 128, 128); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
}
const FIRE_T = glowTex('rgba(255,245,215,0.95)', 'rgba(255,120,25,0.45)'), SMOKE_T = glowTex('rgba(70,66,62,0.85)', 'rgba(50,48,46,0.45)');
function emitter({ n, start, every, life, size, grow, rise, spread, kind, seed, pos }) {
  const r = rng(seed); const P = [];
  for (let i = 0; i < n; i++) {
    const mat = new THREE.SpriteMaterial({ map: kind === 'fire' ? FIRE_T : SMOKE_T, transparent: true, depthWrite: false, blending: kind === 'fire' ? THREE.AdditiveBlending : THREE.NormalBlending, fog: true });
    const s = new THREE.Sprite(mat); s.visible = false; scene.add(s);
    P.push({ s, b: start + i * every, life: life * (0.7 + r() * 0.6), j: new THREE.Vector3((r() - 0.5) * spread, (r() - 0.5) * spread, (r() - 0.5) * spread), k: r() });
  }
  return t => { for (const p of P) { const age = t - p.b; if (age < 0 || age > p.life) { p.s.visible = false; continue; }
      const e = pos(p.b); if (!e) { p.s.visible = false; continue; }
      const a = age / p.life; p.s.visible = true;
      p.s.position.set(e.x + p.j.x * (0.3 + a), e.y + p.j.y * 0.5 + rise * age, e.z + p.j.z * (0.3 + a));
      const sz = size * (1 + grow * a) * (0.8 + p.k * 0.4); p.s.scale.set(sz, sz, 1);
      if (kind === 'fire') { p.s.material.color.setRGB(1, lerp(0.95, 0.35, a), lerp(0.7, 0.1, a)); p.s.material.opacity = (1 - a) * 0.95; }
      else { p.s.material.opacity = Math.sin(Math.PI * a) * 0.55; }
  } };
}

// ---------------- takeoff kinematics (shared by A scenes and D) ----------------
const TR = 6.0, TS = Number(CFG.ts ?? 7.25);                                      // rotation start, engine separation (sim seconds)
function planeX(t) { return -420 + 56 * t + 1.6 * t * t; }
function planeState(t) {
  const x = planeX(t);
  const pitch = 0.15 * seg(t, TR, 1.6) - 0.06 * seg(t, TS + 4.5, 3);
  const y = 9.1 * seg(t, TR + 1.0, 3.2) - 6 * seg(t, TS + 6.5, 3);
  const roll = -0.12 * seg(t, TS + 3.5, 4);
  return { x, y, pitch, roll };
}
const _m = new THREE.Matrix4(), _q = new THREE.Quaternion(), _e = new THREE.Euler();
function planeMatrix(t) { const s = planeState(t); _e.set(s.roll, 0, s.pitch, 'XYZ'); _q.setFromEuler(_e); return new THREE.Matrix4().compose(new THREE.Vector3(s.x, s.y, 0), _q, new THREE.Vector3(1, 1, 1)); }
let ENG_LOCAL = null;
function engineWorld(t) {                                        // world matrix of the left engine+pylon group
  if (t < TS) return planeMatrix(t).multiply(ENG_LOCAL);
  const m0 = planeMatrix(TS).multiply(ENG_LOCAL); const p0 = new THREE.Vector3().setFromMatrixPosition(m0);
  const tau = t - TS; const T_HIT = 2.75; const tt = Math.min(tau, T_HIT);
  const p = new THREE.Vector3(p0.x + 70 * tt - 9 * tt * tt, p0.y + 13 * tt - 4.9 * tt * tt, p0.z + 9.5 * tt);
  if (tau > T_HIT) { const k = 1 - Math.exp(-(tau - T_HIT) * 2.2); p.x += 30 * k; p.y = 1.5; }
  p.y = Math.max(p.y, 1.5);
  const spin = tau > T_HIT ? T_HIT + (tau - T_HIT) * 0.15 : tau;
  _e.set(2.2 * spin, 0.4 * spin, 1.5 * spin + 0.15, 'XYZ'); _q.setFromEuler(_e);
  return new THREE.Matrix4().compose(p, _q, new THREE.Vector3(1, 1, 1));
}
function pylonRootWorld(t) { return new THREE.Vector3(3.0 + 2.4, 5.6 - 2.0, -10.2).applyMatrix4(planeMatrix(t)); }

// ---------------- scenes ----------------
let draw = () => {};
const camAt = (p, look, fov) => { camera.position.copy(p); camera.lookAt(look); if (fov) { camera.fov = fov; camera.updateProjectionMatrix(); } };

function takeoffScene(simOf, camFn, fadeAt) {
  const { sun } = world(); const plane = makePlane(); scene.add(plane);
  const left = plane.userData.engs.left; ENG_LOCAL = left.matrix.clone().compose(left.position, left.quaternion, left.scale);
  plane.remove(left); scene.add(left); left.matrixAutoUpdate = false;
  const fireEng = emitter({ n: 800, start: TS, every: 0.012, life: 0.6, size: 2.4, grow: 2.0, rise: 2.5, spread: 1.8, kind: 'fire', seed: 1, pos: b => new THREE.Vector3().setFromMatrixPosition(engineWorld(b)) });
  const smokeEng = emitter({ n: 220, start: TS + 0.1, every: 0.05, life: 3.2, size: 4, grow: 3.5, rise: 3.5, spread: 3, kind: 'smoke', seed: 2, pos: b => new THREE.Vector3().setFromMatrixPosition(engineWorld(b)) });
  const fireWing = emitter({ n: 800, start: TS + 0.05, every: 0.012, life: 0.55, size: 2.0, grow: 1.8, rise: 1.5, spread: 1.3, kind: 'fire', seed: 3, pos: b => pylonRootWorld(b) });
  const smokeWing = emitter({ n: 200, start: TS + 0.2, every: 0.05, life: 3.5, size: 4, grow: 4, rise: 2.5, spread: 3, kind: 'smoke', seed: 4, pos: b => pylonRootWorld(b) });
  draw = t => {
    const s = simOf(t); const st = planeState(s);
    plane.position.set(st.x, st.y, 0); plane.rotation.set(st.roll, 0, st.pitch);
    left.matrix.copy(engineWorld(s));
    fireEng(s); smokeEng(s); fireWing(s); smokeWing(s);
    camFn(t, s, st);
    sun.target.position.set(st.x, 0, 0); sun.position.set(st.x - 850, 80, 520);
    fade.style.opacity = fadeAt ? seg(t, fadeAt, 1.2) : 0;
  };
  return plane;
}

const SC = {
  // A1: wide broadside, real time; separation at clip ~7.7 s
  A1: () => takeoffScene(t => t + Number(CFG.off ?? -0.45), (t, s, st) => {
      const look = new THREE.Vector3(st.x + 25, 6 + st.y * 0.6, 0);
      camAt(new THREE.Vector3(150, 4, 200), look, 21 - 4 * seg(t, 6.6, 2.5));
    }),
  // A3: from behind, the jet staggers on, low, trailing fire, toward the fence; fades out
  A3: () => takeoffScene(t => TS + 1.6 + t, (t, s, st) => {
      camAt(new THREE.Vector3(st.x - 150 - 20 * t, 10 + st.y * 0.5, 38), new THREE.Vector3(st.x + 60, 6 + st.y, 0), 34);
    }, Number(CFG.fade ?? 3.4)),
  // A2: slow motion, close, from the left and slightly below
  A2: () => takeoffScene(t => TR - 1.2 + t * Number(CFG.k ?? 0.42), (t, s, st) => {
      const hold = seg(s, TS + 0.4, 1.6);
      const follow = new THREE.Vector3(st.x - 30, 3.2, -46);
      const fixed = new THREE.Vector3(planeX(TS + 0.4) - 30, 3.2, -46).add(new THREE.Vector3(30 * hold, 6 * hold, -10 * hold));
      const pos = follow.clone().lerp(fixed, hold);
      const lookPlane = new THREE.Vector3(st.x + 4, 5.5 + st.y, -4);
      const lookEng = new THREE.Vector3().setFromMatrixPosition(engineWorld(s));
      camAt(pos, lookPlane.clone().lerp(lookEng, 0.55 * hold), 40);
    }),
};

// C: parked jet at golden hour, slow orbit, engine labels
SC.C = () => {
  world(); const plane = makePlane(); scene.add(plane); plane.position.set(0, 0, 0);
  const e = plane.userData.engs;
  const wp = o => () => new THREE.Vector3().setFromMatrixPosition(o.matrixWorld);
  if (!CFG.nolabels) {
  label('ENGINE 1', 'left wing', wp(e.left), CFG.l1 ?? 3.5, { dx: -170, dy: -150 });
  label('ENGINE 3', 'right wing', wp(e.right), CFG.l1 ?? 3.5, { dx: -120, dy: 150 });
  label('ENGINE 2', 'in the tail', wp(e.tail), CFG.l2 ?? 6.2, { dx: 160, dy: -120 });
  }
  draw = t => { const a = 0.62 + t * 0.045; camAt(new THREE.Vector3(Math.cos(a) * 82, 24 - t * 0.6, Math.sin(a) * 82), new THREE.Vector3(-2, 4, 0), 36); plane.updateMatrixWorld(); };
};

// D: aerial view of the path past the fence, warehouse and storage yard (no wreckage shown)
SC.D = () => {
  world();
  const path = []; for (let i = 0; i <= 200; i++) { const x = 765 + i * 4.7; const y = x < 830 ? 9 : x < 1000 ? lerp(9, 12.5, (x - 830) / 170) : Math.max(0.5, 12.5 - (x - 1000) * 0.018); path.push(new THREE.Vector3(x, y, (x > 900 ? (x - 900) * 0.06 : 0))); }
  const curve = new THREE.CatmullRomCurve3(path);
  const trail = new THREE.Mesh(new THREE.TubeGeometry(curve, 400, 1.6, 8), new THREE.MeshBasicMaterial({ color: 0xff3b3b, transparent: true, opacity: 0.95, fog: false }));
  scene.add(trail); trail.geometry.setDrawRange(0, 0);
  const plane = makePlane(); plane.scale.setScalar(1.6); scene.add(plane);
  const glow = new THREE.PointLight(0xff7a2a, 0, 600, 1.6); glow.position.set(1600, 30, 40); scene.add(glow);
  const smoke = emitter({ n: 220, start: CFG.impact ?? 7.4, every: 0.035, life: 6, size: 14, grow: 5, rise: 16, spread: 30, kind: 'smoke', seed: 7, pos: () => new THREE.Vector3(1610, 10, 40) });
  const fireTrail = emitter({ n: 700, start: 0, every: 0.018, life: 0.7, size: 5, grow: 1.4, rise: 2, spread: 3, kind: 'fire', seed: 8, pos: b => b < (CFG.impact ?? 7.4) ? curve.getPointAt(clamp(b / (CFG.impact ?? 7.4))).add(new THREE.Vector3(-4, 0, -9)) : null });
  label('BLAST FENCE', null, new THREE.Vector3(830, 5, -60), CFG.fence ?? 0.6, { dx: -160, dy: -120 });
  label('WAREHOUSE', 'landing gear strikes the roof', new THREE.Vector3(960, 12, 10), CFG.roof ?? 3.9, { dx: 140, dy: -170 });
  label('STORAGE YARD &amp; RECYCLING FACILITY', null, new THREE.Vector3(1600, 14, 40), CFG.yard ?? 7.0, { dx: 90, dy: -110, red: true });
  draw = t => {
    const T = CFG.impact ?? 7.4, k = clamp(t / T);
    trail.geometry.setDrawRange(0, Math.floor(400 * 8 * 6 * k));
    const p = curve.getPointAt(k), p2 = curve.getPointAt(Math.min(1, k + 0.01));
    plane.visible = t < T; plane.position.copy(p).add(new THREE.Vector3(0, -2, 0)); plane.rotation.set(-0.12, 0, Math.atan2(p2.y - p.y, p2.x - p.x) + 0.08);
    glow.intensity = 1600 * seg(t, T, 0.6) * (0.85 + 0.15 * Math.sin(t * 9));
    smoke(t); fireTrail(t);
    camAt(new THREE.Vector3(620 + t * 34, 150 - t * 3, -330 + t * 4), new THREE.Vector3(980 + t * 40, 0, 10), 40);
  };
};

// B: the pylon aft mount — lugs, spherical bearing (ball + race), wing clevis
function mountModel() {
  const G = new THREE.Group();
  const alu = new THREE.MeshStandardMaterial({ color: 0xb8bec6, metalness: 0.85, roughness: 0.32, transparent: true });
  const steel = new THREE.MeshStandardMaterial({ color: 0xdfe4ea, metalness: 1.0, roughness: 0.18 });
  const raceM = new THREE.MeshStandardMaterial({ color: 0x6fa8ff, metalness: 0.7, roughness: 0.3, emissive: 0x0a2a66, emissiveIntensity: 0.0 });
  const clevM = new THREE.MeshStandardMaterial({ color: 0x8b9096, metalness: 0.8, roughness: 0.4, transparent: true });
  const plateWithHole = (w, h, th, hy, hr, mat) => { const s = new THREE.Shape(); s.moveTo(-w / 2, 0); s.lineTo(w / 2, 0); s.lineTo(w / 2, hy); s.absarc(0, hy, w / 2, 0, Math.PI, false); s.lineTo(-w / 2, 0);
    const hole = new THREE.Path(); hole.absarc(0, hy, hr, 0, Math.PI * 2, true); s.holes.push(hole);
    const g = new THREE.ExtrudeGeometry(s, { depth: th, bevelEnabled: true, bevelThickness: 0.15, bevelSize: 0.15, bevelSegments: 3, curveSegments: 48 }); g.translate(0, 0, -th / 2); g.rotateY(Math.PI / 2); return mesh(g, mat); };
  // lugs (from the pylon, pointing up), axis of the bearing = x
  const lugF = plateWithHole(6.4, 4.6, 2.2, 4.6, 2.45, alu); lugF.position.set(1.25, -4.6, 0); G.add(lugF);
  const lugA = plateWithHole(6.4, 4.6, 2.2, 4.6, 2.45, alu.clone()); lugA.position.set(-1.25, -4.6, 0); G.add(lugA);
  const base = mesh(new THREE.BoxGeometry(9, 2.2, 7.2), alu.clone()); base.position.set(0, -5.6, 0); G.add(base);
  // wing clevis (from the wing, pointing down), outside the lugs
  const clevF = plateWithHole(6.4, 3.2, 1.3, 1.0, 0.9, clevM); clevF.rotation.x = Math.PI; clevF.position.set(3.4, 1.0, 0); G.add(clevF);
  const clevA = plateWithHole(6.4, 3.2, 1.3, 1.0, 0.9, clevM.clone()); clevA.rotation.x = Math.PI; clevA.position.set(-3.4, 1.0, 0); G.add(clevA);
  const clevTop = mesh(new THREE.BoxGeometry(9.5, 1.4, 7.6), clevM.clone()); clevTop.position.set(0, 4.9, 0); G.add(clevTop);
  // spherical bearing: race (two halves, split plane x=0) and ball, bolt
  const raceProf = (x0, x1) => along(new THREE.LatheGeometry([new THREE.Vector2(2.0, x0), new THREE.Vector2(2.42, x0), new THREE.Vector2(2.42, x1), new THREE.Vector2(2.0, x1), new THREE.Vector2(2.0, x0)], 64));
  const raceF = mesh(raceProf(0.02, 2.5), raceM); G.add(raceF);
  const raceA = mesh(raceProf(-2.5, -0.02), raceM.clone()); G.add(raceA);
  const groove = mesh(along(new THREE.CylinderGeometry(2.02, 2.02, 0.18, 64, 1, true)), new THREE.MeshStandardMaterial({ color: 0x222831, metalness: 0.5, roughness: 0.6, side: THREE.DoubleSide })); G.add(groove);
  const crack = mesh(along(new THREE.CylinderGeometry(2.45, 2.45, 0.2, 96, 1, true, 0, 0.01)), new THREE.MeshBasicMaterial({ color: 0xff3030, side: THREE.DoubleSide, transparent: true }), false); G.add(crack);
  const ball = mesh(new THREE.SphereGeometry(2.05, 64, 32), steel); ball.scale.x = 0.95; G.add(ball);
  const bolt = mesh(along(new THREE.CylinderGeometry(0.85, 0.85, 10.5, 40)), steel); G.add(bolt);
  for (const sx of [5.2, -5.2]) { const nut = mesh(along(new THREE.CylinderGeometry(1.35, 1.35, 0.8, 6)), steel); nut.position.x = sx; G.add(nut); }
  G.userData = { lugF, lugA, base, raceF, raceA, raceM, crack, ball, alu, groove };
  return G;
}

SC.B = (part) => {
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  scene.background = new THREE.Color(0x0b0f1a);
  const key = new THREE.DirectionalLight(0xffffff, 2.2); key.position.set(30, 40, 50); scene.add(key);
  const rim = new THREE.DirectionalLight(0x7fb2ff, 1.4); rim.position.set(-40, 10, -30); scene.add(rim);
  scene.add(new THREE.HemisphereLight(0xbfd4ff, 0x1a1208, 0.5));
  // wing + pylon + engine at full scale (metres); the mount detail sits at the pylon's aft attachment, scaled 0.045
  const wingM = new THREE.MeshStandardMaterial({ color: 0xbcc2ca, metalness: 0.5, roughness: 0.45 });
  const wing = mesh(new THREE.BoxGeometry(12, 0.7, 14), wingM); wing.position.set(-2, 4.2, 0); scene.add(wing);
  const pylonG = new THREE.Group(); scene.add(pylonG);
  const py = mesh(new THREE.BoxGeometry(6.0, 1.9, 0.6), wingM); py.position.set(1.6, 2.85, 0); pylonG.add(py);
  const eng = makeEngine(); eng.position.set(4.6, 0.9, 0); pylonG.add(eng);
  const mount = mountModel(); mount.scale.setScalar(0.045); mount.position.set(-1.9, 3.62, 0); pylonG.add(mount);
  const aftBk = mesh(new THREE.BoxGeometry(0.75, 0.32, 0.34), wingM); aftBk.position.set(-1.45, 3.3, 0); pylonG.add(aftBk);
  const fwdMount = mesh(new THREE.BoxGeometry(0.5, 0.6, 0.5), wingM); fwdMount.position.set(3.8, 3.75, 0); pylonG.add(fwdMount);
  const spot = new THREE.PointLight(0xffffff, 4, 6, 1.5); spot.position.set(-1.3, 3.9, 1.2); scene.add(spot);
  const u = mount.userData;
  const hl = new THREE.Mesh(new THREE.SphereGeometry(0.55, 32, 16), new THREE.MeshBasicMaterial({ color: 0xff3b3b, transparent: true, opacity: 0, depthWrite: false })); hl.position.copy(mount.position); pylonG.add(hl);
  const wpos = (o, off = new THREE.Vector3()) => () => off.clone().applyMatrix4(o.matrixWorld);
  const C = CFG;
  if (part === 1) {
    label('PYLON', 'holds the engine to the wing', new THREE.Vector3(1.5, 2.9, 0.3), C.pylon ?? 0.4, { dx: 160, dy: -150, until: C.joint ?? 2.6 });
    label('AFT MOUNT', 'a single joint', wpos(mount), C.joint ?? 2.9, { dx: -180, dy: -150, red: true, until: (C.lugs ?? 6.6) - 0.3 });
    label('LUGS', 'forward &amp; aft', wpos(mount, new THREE.Vector3(0, -3.0, 3.6)), C.lugs ?? 6.6, { dx: 170, dy: 120, until: 99 });
    label('SPHERICAL BEARING', null, wpos(mount, new THREE.Vector3(0, 2.2, 0)), C.bearing ?? 8.6, { dx: -200, dy: -120, until: (C.ball ?? 10.6) - 0.2 });
    label('STEEL BALL', null, wpos(mount, new THREE.Vector3(0, 1.4, -1.2)), C.ball ?? 10.6, { dx: -200, dy: -130 });
    label('THE RACE', 'the ring around it', wpos(mount, new THREE.Vector3(-1.6, 2.4, 0)), C.race ?? 12.0, { dx: -220, dy: 140 });
  }
  if (part === 2) {
    label('DESIGN GROOVE', 'inside the race', wpos(mount, new THREE.Vector3(0, -2.0, 0)), C.groove ?? 3.5, { dx: 200, dy: 120 });
    label('FATIGUE CRACK', '≈75% of the fracture', wpos(mount, new THREE.Vector3(0, 2.45, 0)), C.crack ?? 1.4, { dx: -260, dy: -130, red: true });
  }
  draw = t => {
    let camPos, look, fov = 32, lugOp = 1, crackK = 0, split = 0, drop = 0, glow = 0, raceGlow = 0;
    const mp = new THREE.Vector3(); mount.updateMatrixWorld(); mp.setFromMatrixPosition(mount.matrixWorld);
    if (part === 1) {
      const d = seg(t, C.joint ?? 2.6, 3.8);                                   // dolly from the engine to the mount
      const a = 0.9 - 0.5 * seg(t, 0, 14);
      const far = new THREE.Vector3(10 * Math.cos(a) + 1, 1.2, 14 * Math.sin(a) + 2), near = mp.clone().add(new THREE.Vector3(0.3, -0.1, 0.95));
      camPos = far.clone().lerp(near, d); look = new THREE.Vector3(1.5, 2.6, 0).lerp(mp, d);
      glow = seg(t, C.joint ?? 2.6, 0.5) * (1 - seg(t, (C.joint ?? 2.6) + 2.5, 1)) * (0.6 + 0.4 * Math.sin(t * 7));
      lugOp = 1 - 0.75 * seg(t, (C.bearing ?? 8.6) - 0.2, 1.0);
      raceGlow = seg(t, C.race ?? 12.0, 0.6);
      const orb = -seg(t, (C.bearing ?? 8.6), 6) * 0.6;
      camPos = camPos.clone().sub(mp).applyAxisAngle(new THREE.Vector3(0, 1, 0), orb).add(mp);
    } else if (part === 2) {
      camPos = mp.clone().add(new THREE.Vector3(-0.42 + 0.08 * seg(t, 0, 10), 0.1, 0.62)); look = mp.clone();
      lugOp = 0.25; raceGlow = 0.6; crackK = seg(t, C.crack ?? 1.4, C.crackDur ?? 4.5); split = seg(t, C.split ?? 7.0, 2.2);
    } else {
      camPos = new THREE.Vector3(0.5 + 1.0 * seg(t, 0, 5), 0.6, 19 + 2 * seg(t, 0, 5)); look = new THREE.Vector3(1.4, 1.6 - 1.0 * seg(t, 1.0, 3), 0); fov = 34;
      lugOp = 1; crackK = 1; split = 1; drop = seg(t, C.drop ?? 1.0, 2.6); fov = 36;
    }
    u.alu.opacity = lugOp; u.lugA.material.opacity = lugOp; u.base.material.opacity = lugOp;
    [u.lugF, u.lugA, u.base].forEach(m => { m.material.depthWrite = lugOp > 0.95; });
    u.raceM.emissiveIntensity = raceGlow * 0.9; u.raceA.material.emissiveIntensity = raceGlow * 0.9;
    u.crack.geometry.dispose(); u.crack.geometry = along(new THREE.CylinderGeometry(2.45, 2.45, 0.22, 96, 1, true, 0, Math.max(0.001, crackK * Math.PI * 2)));
    u.crack.material.opacity = crackK > 0 ? 1 : 0;
    u.raceF.position.x = 0.9 * split; u.raceA.position.x = -0.9 * split; u.crack.position.x = 0.9 * split;
    u.lugF.rotation.z = -0.25 * drop; u.lugA.rotation.z = 0.2 * drop;
    { const ang = 0.55 * drop, Fx = 3.8, Fy = 3.75, c = Math.cos(ang), s2 = Math.sin(ang);
      pylonG.rotation.z = ang; pylonG.position.set(Fx - (Fx * c - Fy * s2), Fy - (Fx * s2 + Fy * c) - 3.0 * drop * drop, 0); }
    hl.material.opacity = glow * 0.55; hl.scale.setScalar(1 + 0.3 * Math.sin(t * 7));
    camAt(camPos, look, fov);
  };
};

// ---------------- boot ----------------
if (SCENE.startsWith('B')) SC.B(Number(SCENE.slice(1)) || 1); else SC[SCENE]();
window.renderAt = t => { draw(t); scene.updateMatrixWorld(); updateLabels(t); renderer.render(scene, camera); return true; };
window.ready = true;
