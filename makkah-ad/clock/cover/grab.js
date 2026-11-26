const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('http://127.0.0.1:8741/index.html'); await p.evaluate(() => window.ready);
  for (const t of process.argv.slice(2)) { await p.evaluate(t => window.render(t), +t); await p.evaluate(() => { const c = document.getElementById('ui'); c.getContext('2d').clearRect(0, 0, c.width, c.height); }); await (await p.$('#gl')).screenshot({ path: `cover/gl_${t}.png` }); }
  await b.close();
})();
