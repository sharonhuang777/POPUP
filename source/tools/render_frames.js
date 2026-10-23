// Render frames of a board with Playwright (animations paused and scrubbed), transparent background.
// node render_frames.js <html> <outDir> <t0> <t1> <fps> <scale> [keepSelectorsCSV|ALL]
// keep = only these selectors (and their children) stay visible, everything else is hidden → effect overlay.
const { chromium } = require('playwright');
(async () => {
  const [file, out, t0s, t1s, fpss, scs, keep] = process.argv.slice(2);
  const t0 = +t0s, t1 = +t1s, fps = +fpss, sc = +scs;
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 402, height: 874 }, deviceScaleFactor: sc });
  await p.goto('file://' + file); await p.waitForTimeout(700);
  if (keep && keep !== 'ALL') {
    const sel = keep.split(',').map(s => s.trim());
    const css = 'html,body{background:transparent!important}*{visibility:hidden!important}' +
      sel.map(s => s + ',' + s + ' *').join(',') + '{visibility:visible!important}';
    await p.addStyleTag({ content: css });
  }
  await p.evaluate(() => document.getAnimations().forEach(a => a.pause()));
  const n = Math.round((t1 - t0) * fps);
  for (let i = 0; i <= n; i++) {
    const t = (t0 + i / fps) * 1000;
    await p.evaluate(t => document.getAnimations().forEach(a => { a.currentTime = t; }), t);
    await p.screenshot({ path: `${out}/f_${String(i).padStart(4, '0')}.png`, omitBackground: keep && keep !== 'ALL' });
  }
  await b.close();
  console.log(n + 1);
})();
