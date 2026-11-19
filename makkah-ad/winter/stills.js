// Saves the 8 finished cards (with logo and fixes) as PNG files.
const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('http://127.0.0.1:8733/index.html'); await p.evaluate(() => window.ready); const c = await p.$('canvas');
  for (let i = 1; i <= 8; i++) { await p.evaluate(k => window.render(-k), i); await c.screenshot({ path: `final/card${i}.png` }); }
  await b.close(); })();
