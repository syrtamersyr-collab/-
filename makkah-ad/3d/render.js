// Renders the 3D page frame by frame through headless Chromium (software WebGL) into ffmpeg.
// usage: node render.js out.mp4 fps t0 t1 [stills: comma list of times] [port]
const { chromium } = require('playwright');
const { spawn } = require('child_process');
(async () => {
  const out = process.argv[2], fps = +(process.argv[3] || 30), t0 = +(process.argv[4] || 0), t1 = +(process.argv[5] || 36);
  const stills = process.argv[6] && process.argv[6] !== '-' ? process.argv[6] : null, port = process.argv[7] || 8731;
  const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  p.on('console', m => { if (m.type() === 'error') console.log('page:', m.text()); });
  p.on('pageerror', e => console.log('ERR:', e.message));
  await p.goto(`http://127.0.0.1:${port}/index.html`);
  await p.evaluate(() => window.ready);
  const el = await p.$('#wrap');
  if (stills) { for (const s of stills.split(',')) { const a = Date.now(); await p.evaluate(t => window.render(t), +s); await el.screenshot({ path: `${out}_${s}.jpg`, type: 'jpeg', quality: 85 }); console.log(s, Date.now() - a, 'ms'); } await b.close(); return; }
  const ff = spawn('ffmpeg', ['-y', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', out], { stdio: ['pipe', 'ignore', 'ignore'] });
  const n = Math.round((t1 - t0) * fps);
  for (let i = 0; i < n; i++) {
    await p.evaluate(t => window.render(t), t0 + i / fps);
    const buf = await el.screenshot({ type: 'jpeg', quality: 95 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 30 === 0) console.log('frame', i, '/', n);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close();
})();
