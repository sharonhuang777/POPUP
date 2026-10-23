// Sample a canvas board for Lottie export.
// node lottie_sample.js <board.html> <outDir> <config.json>
// config: { "duration": s, "fps": 60, "items": [ { "sel": ".m-c", "kind": "shape|radial|polar|soft|avatar", ... } ] }
// Writes <outDir>/sample.json (per-element static info + per-frame affine/opacity) and <outDir>/shot_*.png (isolated element renders).
// Per-frame motion comes from three zero-size probes inside each element, so every ancestor transform and every
// CSS keyframe/easing is captured exactly as the browser plays it.
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const [file, out, cfgPath] = process.argv.slice(2);
  const cfg = JSON.parse(fs.readFileSync(cfgPath, 'utf8'));
  const fps = cfg.fps || 60, N = Math.round(cfg.duration * fps);
  const b = await chromium.launch();

  // ---------- motion ----------
  const p = await b.newPage({ viewport: { width: 402, height: 874 } });
  await p.goto('file://' + file); await p.waitForTimeout(800);
  const meta = await p.evaluate((items) => {
    const root = document.querySelector('[data-ms-root]') || document.querySelector('x-dc > div') || document.body.firstElementChild;
    window.__root = root;
    const list = [];
    items.forEach((it, ii) => {
      document.querySelectorAll(it.sel).forEach((el, k) => {
        if (getComputedStyle(el).position === 'static') el.style.position = 'relative';
        const bl = el.clientLeft, bt = el.clientTop;
        const pr = [[0, 0], [100, 0], [0, 100]].map(([x, y]) => {
          const s = document.createElement('i');
          s.style.cssText = `position:absolute;left:${x - bl}px;top:${y - bt}px;width:0;height:0;padding:0;margin:0;border:0;display:block;animation:none;transform:none`;
          el.appendChild(s); return s;
        });
        el.__probes = pr;
        list.push({ item: ii, k, el });
      });
    });
    window.__list = list;
    document.getAnimations().forEach(a => a.pause());
    return list.map(o => ({ item: o.item, k: o.k, w: o.el.offsetWidth, h: o.el.offsetHeight, order: 0 }));
  }, cfg.items);
  // document order for z-stacking
  const order = await p.evaluate(() => {
    const all = Array.from(document.querySelectorAll('*'));
    return window.__list.map(o => all.indexOf(o.el));
  });
  meta.forEach((m, i) => { m.order = order[i]; m.frames = []; });
  for (let f = 0; f <= N; f++) {
    const rows = await p.evaluate((t) => {
      document.getAnimations().forEach(a => { a.currentTime = t; });
      const R = window.__root.getBoundingClientRect();
      return window.__list.map(o => {
        const q = o.el.__probes.map(s => { const r = s.getBoundingClientRect(); return [r.left - R.left, r.top - R.top]; });
        let op = 1, n = o.el;
        while (n && n !== document.documentElement) { const v = +getComputedStyle(n).opacity; op *= isNaN(v) ? 1 : v;
          if (getComputedStyle(n).visibility === 'hidden' || getComputedStyle(n).display === 'none') op = 0; n = n.parentElement; }
        return [q[0][0], q[0][1], q[1][0], q[1][1], q[2][0], q[2][1], op];
      });
    }, f / fps * 1000);
    rows.forEach((r, i) => meta[i].frames.push(r.map(v => Math.round(v * 1000) / 1000)));
  }
  await p.close();

  // ---------- static looks (isolated clones, transparent bg) ----------
  const S = 4;
  const q = await b.newPage({ viewport: { width: 700, height: 700 }, deviceScaleFactor: S });
  await q.goto('file://' + file); await q.waitForTimeout(800);
  await q.addStyleTag({ content: 'html,body{background:transparent!important} #__ov,#__ov *{animation:none!important} #__ov .__c,#__ov .__c *{transition:none!important}' });
  await q.evaluate(() => {
    const root = document.querySelector('[data-ms-root]') || document.querySelector('x-dc > div') || document.body.firstElementChild;
    root.style.visibility = 'hidden';
    const ov = document.createElement('div'); ov.id = '__ov';
    ov.style.cssText = 'position:fixed;left:0;top:0;width:700px;height:700px;visibility:visible;z-index:99999;background:transparent;font-family:Outfit,sans-serif';
    document.body.appendChild(ov);
  });
  async function shot(selIdx, k, mode, name, child) {
    const box = await q.evaluate(({ sel, k, mode, child }) => {
      const src = document.querySelectorAll(sel)[k];
      const ov = document.getElementById('__ov'); ov.innerHTML = '';
      const c = src.cloneNode(true); c.classList.add('__c');
      const w = src.offsetWidth, h = src.offsetHeight;
      const kill = n => { n.style.setProperty('animation', 'none', 'important'); n.style.setProperty('transform', 'none', 'important'); n.style.setProperty('opacity', '1', 'important'); };
      kill(c); c.querySelectorAll('*').forEach(n => n.style.setProperty('animation', 'none', 'important'));
      c.style.position = 'absolute'; c.style.left = (350 - w / 2) + 'px'; c.style.top = (350 - h / 2) + 'px';
      c.style.right = 'auto'; c.style.bottom = 'auto'; c.style.margin = '0'; c.style.width = w + 'px'; c.style.height = h + 'px';
      if (mode === 'coverage') { c.style.background = '#FFFFFF'; c.style.boxShadow = 'none'; }
      if (mode === 'shadow') { c.style.background = 'none'; }
      if (mode === 'image') { c.style.boxShadow = 'none'; c.style.filter = 'none'; }
      if (mode === 'child') { Array.from(c.children).forEach((n, i) => { if (i !== child) n.style.visibility = 'hidden'; }); }
      ov.appendChild(c);
      return { w, h };
    }, { sel: cfg.items[selIdx].sel, k, mode, child });
    await q.waitForTimeout(30);
    await q.screenshot({ path: `${out}/${name}`, omitBackground: true, clip: { x: 0, y: 0, width: 700, height: 700 } });
    return box;
  }
  const looks = [];
  for (let i = 0; i < meta.length; i++) {
    const m = meta[i], it = cfg.items[m.item];
    const style = await q.evaluate(({ sel, k }) => {
      const el = document.querySelectorAll(sel)[k], cs = getComputedStyle(el);
      return { bg: cs.backgroundColor, bgi: cs.backgroundImage, br: cs.borderTopLeftRadius, bw: parseFloat(cs.borderTopWidth) || 0,
        bc: cs.borderTopColor, bs: cs.boxShadow, filter: cs.filter };
    }, { sel: it.sel, k: m.k });
    const L = { style, shots: {} };
    const tag = `${m.item}_${m.k}`;
    if (it.kind === 'radial') { await shot(m.item, m.k, 'plain', L.shots.plain = `shot_${tag}.png`); }
    if (it.kind === 'polar') {
      for (const [ci, ck] of it.children) { L.shots['c' + ci] = `shot_${tag}_c${ci}.png`; await shot(m.item, m.k, 'child', L.shots['c' + ci], ci); }
    }
    if (it.kind === 'soft') { await shot(m.item, m.k, 'coverage', L.shots.coverage = `shot_${tag}_cov.png`);
      await shot(m.item, m.k, 'shadow', L.shots.shadow = `shot_${tag}_sh.png`); }
    if (it.kind === 'avatar') { await shot(m.item, m.k, 'image', L.shots.image = `shot_${tag}_img.png`); }
    looks.push(L);
  }
  await b.close();
  meta.forEach((m, i) => Object.assign(m, looks[i]));
  fs.writeFileSync(`${out}/sample.json`, JSON.stringify({ fps, N, scale: S, shotCenter: 350, items: cfg.items, els: meta }));
  console.log('elements', meta.length, 'frames', N + 1);
})();
