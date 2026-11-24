// usage: node render3d.js SCENE DURATION OUT.mp4 '{"cfg":"json"}' [--stills t1,t2,...]
// Renders three3d/index.html?scene=SCENE frame by frame (30 fps) with software WebGL, then encodes with ffmpeg.
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path'), { execFileSync } = require('child_process');
const [scene, dur, out, cfg = '{}'] = process.argv.slice(2);
const stillsArg = process.argv.indexOf('--stills');
const ROOT = path.join(__dirname, 'three3d');
const TYPES = { '.html': 'text/html', '.js': 'text/javascript' };
const srv = http.createServer((q, r) => { const f = path.join(ROOT, decodeURIComponent(q.url.split('?')[0]));
  fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); r.end(); return; } r.writeHead(200, { 'Content-Type': TYPES[path.extname(f)] || 'application/octet-stream' }); r.end(d); }); });
(async () => {
  await new Promise(res => srv.listen(0, res)); const port = srv.address().port;
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  p.on('pageerror', e => console.error('PAGE ERROR', e.message));
  await p.goto(`http://127.0.0.1:${port}/index.html?scene=${scene}&cfg=${encodeURIComponent(cfg)}`);
  await p.waitForFunction(() => window.ready === true, null, { timeout: 60000 });
  await p.evaluate(() => document.fonts.ready);
  if (stillsArg > 0) {
    for (const t of process.argv[stillsArg + 1].split(',').map(Number)) {
      await p.evaluate(t => window.renderAt(t), t);
      await p.screenshot({ path: `${out}_${t}.jpg`, type: 'jpeg', quality: 88 });
    }
  } else {
    const dir = out + '.frames'; fs.mkdirSync(dir, { recursive: true });
    const n = Math.round(Number(dur) * 30); const t0 = Date.now();
    for (let i = 0; i < n; i++) {
      const f = path.join(dir, `f${String(i).padStart(5, '0')}.jpg`);
      if (fs.existsSync(f)) continue;
      await p.evaluate(t => window.renderAt(t), i / 30);
      await p.screenshot({ path: f, type: 'jpeg', quality: 92 });
      if (i % 60 === 0) console.log(scene, i, '/', n, ((Date.now() - t0) / 1000).toFixed(0) + 's');
    }
    execFileSync('ffmpeg', ['-v', 'error', '-y', '-framerate', '30', '-i', path.join(dir, 'f%05d.jpg'), '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', out]);
    fs.rmSync(dir, { recursive: true, force: true });
    console.log('wrote', out);
  }
  await b.close(); srv.close();
})().catch(e => { console.error(e); process.exit(1); });
