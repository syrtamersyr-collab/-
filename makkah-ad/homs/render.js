// Renders index.html frame by frame and pipes JPEG frames into ffmpeg.
// usage: node render.js out.mp4 [fps] [start] [end] [stills-only: comma list of times]
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
(async () => {
  const out = process.argv[2] || 'out.mp4';
  const fps = +(process.argv[3] || 30), t0 = +(process.argv[4] || 0), t1 = +(process.argv[5] || 35);
  const stills = process.argv[6];
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  p.on('console', m => console.log('page:', m.text()));
  p.on('pageerror', e => console.log('ERR:', e.message));
  await p.goto('file://' + path.resolve(__dirname, 'index.html'));
  await p.evaluate(() => window.ready);
  const canvas = await p.$('canvas');
  if (stills) {
    for (const s of stills.split(',')) {
      await p.evaluate(t => window.render(t), +s);
      await canvas.screenshot({ path: `${out}_${s}.jpg`, type: 'jpeg', quality: 80 });
    }
    await b.close(); return;
  }
  const ff = spawn('ffmpeg', ['-y', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-', '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], { stdio: ['pipe', 'ignore', 'inherit'] });
  const n = Math.round((t1 - t0) * fps);
  for (let i = 0; i < n; i++) {
    const t = t0 + i / fps;
    await p.evaluate(t => window.render(t), t);
    const buf = await canvas.screenshot({ type: 'jpeg', quality: 95 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 60 === 0) console.log('frame', i, '/', n);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await b.close();
})();
