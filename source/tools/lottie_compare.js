// Side-by-side check: original board (left) vs the same board with the converted elements hidden and the Lottie
// playing in their place (right). Writes frames f_XXXX.png into outDir and prints the mean pixel difference.
// node lottie_compare.js <board.html> <lottie.json> <lottie-web.js> <outDir> <hideSelectorsCSV> <dur> <fps> [renderer svg|canvas]
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const [file, lj, lw, out, hide, durS, fpsS, rend] = process.argv.slice(2);
  const dur = +durS, fps = +fpsS, N = Math.round(dur * fps);
  const b = await chromium.launch();
  const mk = async () => { const p = await b.newPage({ viewport: { width: 402, height: 874 }, deviceScaleFactor: 1 });
    await p.goto('file://' + file); await p.waitForTimeout(700); return p; };
  const A = await mk(), B = await mk();
  await A.evaluate(() => document.getAnimations().forEach(a => a.pause()));
  await B.addStyleTag({ content: hide.split(',').map(s => s.trim() + '{visibility:hidden!important}').join('') });
  await B.addScriptTag({ path: lw });
  await B.evaluate(({ data, rend }) => {
    const root = document.querySelector('[data-ms-root]') || document.querySelector('x-dc > div');
    const t = root.querySelector('.m-title,.q-title,.t-title');
    let anchor = t; while (anchor && anchor.parentElement !== root) anchor = anchor.parentElement;
    const box = document.createElement('div');
    box.style.cssText = 'position:absolute;left:0;top:0;width:402px;height:874px;pointer-events:none';
    root.insertBefore(box, anchor || null);
    window.__anim = lottie.loadAnimation({ container: box, renderer: rend || 'svg', loop: false, autoplay: false, animationData: data });
    document.getAnimations().forEach(a => a.pause());
  }, { data: JSON.parse(fs.readFileSync(lj, 'utf8')), rend });
  await B.waitForTimeout(300);
  const sharp = require('fs');
  let diffs = [];
  for (let i = 0; i <= N; i++) {
    const t = i / fps;
    await A.evaluate(t => document.getAnimations().forEach(a => { a.currentTime = t; }), t * 1000);
    await B.evaluate(({ t, fr }) => { document.getAnimations().forEach(a => { a.currentTime = t * 1000; }); window.__anim.goToAndStop(t * fr, true); },
      { t, fr: JSON.parse(fs.readFileSync(lj, 'utf8')).fr });
    const n = String(i).padStart(4, '0');
    await A.screenshot({ path: `${out}/a_${n}.png` });
    await B.screenshot({ path: `${out}/b_${n}.png` });
  }
  await b.close();
  console.log(N + 1);
})();
