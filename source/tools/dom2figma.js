// Walk a canvas board at a given moment and describe it as editable Figma layers (JSON).
// node dom2figma.js <board.html> <out.json> <timeSec> [rasterSelectorsCSV]
// - boxes with fills / borders / radius / shadows / blur -> frames (gradients and shadows kept as real paints / effects)
// - text -> text nodes with styled ranges (gradient text, text stroke, counters from CSS counters)
// - <svg> -> SVG markup (currentColor resolved) for figma.createNodeFromSvg
// - raster selectors (avatars) -> frame whose image fill is a PNG render of the element, effects kept separately
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const [file, out, tS, rastS] = process.argv.slice(2);
  const rast = rastS ? rastS.split(',') : [];
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 402, height: 874 }, deviceScaleFactor: 2 });
  await p.goto('file://' + file); await p.waitForTimeout(900);
  await p.evaluate(t => document.getAnimations().forEach(a => { a.pause(); a.currentTime = t; }), +tS * 1000);
  const res = await p.evaluate((rast) => {
    const root = document.querySelector('[data-ms-root]') || document.querySelector('x-dc > div');
    const R = root.getBoundingClientRect();
    const rasters = [];
    const col = s => { const m = s && s.match(/rgba?\(([^)]+)\)/); if (!m) return null; const v = m[1].split(/[ ,\/]+/).filter(Boolean).map(Number); return { r: v[0] / 255, g: v[1] / 255, b: v[2] / 255, a: v.length > 3 ? v[3] : 1 }; };
    const splitTop = s => { const o = []; let d = 0, c = ''; for (const ch of s) { if (ch === '(') d++; if (ch === ')') d--; if (ch === ',' && d === 0) { o.push(c.trim()); c = ''; } else c += ch; } if (c.trim()) o.push(c.trim()); return o; };
    function stops(parts, len) {
      const st = parts.map(pp => { const c = pp.match(/rgba?\([^)]*\)/); const rest = c ? pp.replace(c[0], '') : pp; const m = rest.match(/(-?[\d.]+)(%|px)/);
        return { c: col(c ? c[0] : 'rgb(0,0,0)'), p: m ? (m[2] === '%' ? +m[1] / 100 : +m[1] / len) : null }; });
      if (st[0].p == null) st[0].p = 0; if (st[st.length - 1].p == null) st[st.length - 1].p = 1;
      for (let i = 0; i < st.length; i++) if (st[i].p == null) { let j = i; while (st[j].p == null) j++; const a = st[i - 1].p, bb = st[j].p; for (let k = i; k < j; k++) st[k].p = a + (bb - a) * (k - i + 1) / (j - i + 1); }
      for (let i = 1; i < st.length; i++) if (st[i].p < st[i - 1].p) st[i].p = st[i - 1].p;
      return st.map(s => ({ position: Math.max(0, Math.min(1, s.p)), color: s.c }));
    }
    function gradient(g, w, h) {
      let m;
      if ((m = g.match(/^linear-gradient\((.*)\)$/))) {
        let parts = splitTop(m[1]), ang = 180;
        if (/^-?[\d.]+deg$/.test(parts[0])) { ang = parseFloat(parts[0]); parts = parts.slice(1); }
        else if (/^to /.test(parts[0])) { ang = { 'to right': 90, 'to left': 270, 'to top': 0, 'to bottom': 180 }[parts[0]] ?? 180; parts = parts.slice(1); }
        const a = ang * Math.PI / 180, dx = Math.sin(a), dy = -Math.cos(a), L = Math.abs(w * dx) + Math.abs(h * dy);
        const S = [w / 2 - dx * L / 2, h / 2 - dy * L / 2], d = [dx * L, dy * L], L2 = L * L;
        const M = [[d[0] / L2, d[1] / L2], [-d[1] / L2, d[0] / L2]];
        const T = [[M[0][0] * w, M[0][1] * h, -(M[0][0] * S[0] + M[0][1] * S[1])], [M[1][0] * w, M[1][1] * h, 0.5 - (M[1][0] * S[0] + M[1][1] * S[1])]];
        return { type: 'GRADIENT_LINEAR', gradientTransform: T, gradientStops: stops(parts, L) };
      }
      if ((m = g.match(/^radial-gradient\((.*)\)$/))) {
        let parts = splitTop(m[1]), shape = parts[0], cx = w / 2, cy = h / 2, rx, ry, circle = false, sized = null;
        const isStop = s => /^(rgba?|#|transparent)/.test(s);
        if (!isStop(shape)) {
          parts = parts.slice(1);
          const at = shape.split(/(?:^|\s)at\s/);
          const pos = at[1] ? at[1].trim().split(/\s+/) : null;
          if (pos) { const pv = (v, L) => v.endsWith('%') ? parseFloat(v) / 100 * L : parseFloat(v); cx = pv(pos[0], w); cy = pv(pos[1] || '50%', h); }
          const sz = at[0].trim().split(/\s+/).filter(x => x && x !== 'ellipse');
          if (sz.includes('circle')) circle = true;
          const nums = sz.filter(x => /^[\d.]+(%|px)$/.test(x));
          if (nums.length === 2) sized = [nums[0].endsWith('%') ? parseFloat(nums[0]) / 100 * w : parseFloat(nums[0]), nums[1].endsWith('%') ? parseFloat(nums[1]) / 100 * h : parseFloat(nums[1])];
          if (nums.length === 1) { const r = parseFloat(nums[0]); sized = [r, r]; circle = true; }
        }
        const fx = Math.max(cx, w - cx), fy = Math.max(cy, h - cy);
        if (sized) { rx = sized[0]; ry = sized[1]; }
        else if (circle) { rx = ry = Math.hypot(fx, fy); }
        else { rx = fx * Math.SQRT2; ry = fy * Math.SQRT2; }
        const T = [[0.5 * w / rx, 0, 0.5 - 0.5 * cx / rx], [0, 0.5 * h / ry, 0.5 - 0.5 * cy / ry]];
        return { type: 'GRADIENT_RADIAL', gradientTransform: T, gradientStops: stops(parts, rx) };
      }
      return null;
    }
    function shadows(s) {
      if (!s || s === 'none') return [];
      return splitTop(s).map(pp => { const c = pp.match(/rgba?\([^)]*\)/); const n = (c ? pp.replace(c[0], '') : pp).match(/-?[\d.]+px/g).map(parseFloat); while (n.length < 4) n.push(0);
        const cc = col(c ? c[0] : 'rgb(0,0,0)');
        return { type: /inset/.test(pp) ? 'INNER_SHADOW' : 'DROP_SHADOW', color: cc, offset: { x: n[0], y: n[1] }, radius: n[2], spread: n[3], visible: true, blendMode: 'NORMAL' }; });
    }
    function visual(el, cs, w, h) {
      const fills = [], strokesPaint = [];
      const bg = col(cs.backgroundColor);
      const imgs = cs.backgroundImage !== 'none' ? splitTop(cs.backgroundImage) : [];
      const clips = cs.backgroundClip.split(',').map(s => s.trim());
      const textClip = clips.includes('text');
      imgs.forEach((g, i) => { const gp = gradient(g, w, h); if (!gp) return; if (clips.includes('padding-box') && clips[i] === 'border-box') strokesPaint.push(gp); else fills.push(gp); });
      fills.reverse();
      if (bg && bg.a > 0) fills.unshift({ type: 'SOLID', color: { r: bg.r, g: bg.g, b: bg.b }, opacity: bg.a });
      const bw = parseFloat(cs.borderTopWidth) || 0, bc = col(cs.borderTopColor);
      let strokes = [];
      if (bw > 0 && bc && bc.a > 0 && cs.borderTopStyle !== 'none') strokes = [{ type: 'SOLID', color: { r: bc.r, g: bc.g, b: bc.b }, opacity: bc.a }];
      if (strokesPaint.length && bw > 0) strokes = strokesPaint;
      const effects = shadows(cs.boxShadow);
      const bd = (cs.backdropFilter || cs.webkitBackdropFilter || '').match(/blur\(([\d.]+)px\)/);
      if (bd) effects.push({ type: 'BACKGROUND_BLUR', radius: +bd[1], visible: true });
      const fb = cs.filter.match(/blur\(([\d.]+)px\)/);
      if (fb) effects.push({ type: 'LAYER_BLUR', radius: +fb[1], visible: true });
      const rr = cs.borderTopLeftRadius;
      const radius = rr.endsWith('%') ? Math.min(w, h) * parseFloat(rr) / 100 : Math.min(parseFloat(rr) || 0, Math.min(w, h) / 2);
      return { fills: textClip ? [] : fills, textFills: textClip ? fills : null, strokes, strokeWeight: bw, effects, radius, clip: cs.overflow === 'hidden' };
    }
    const FW = { 300: 'Light', 400: 'Regular', 500: 'Medium', 600: 'SemiBold', 650: 'SemiBold', 700: 'Bold', 750: 'Bold', 800: 'ExtraBold', 900: 'Black' };
    const famOf = cs => /Montserrat/.test(cs.fontFamily) ? 'Montserrat' : 'Outfit';
    function textRuns(el) {
      const runs = []; let first = true;
      const walk = (n, cs) => {
        for (const c of n.childNodes) {
          if (c.nodeType === 3) { const t = c.textContent.replace(/\s+/g, ' '); if (t.trim() || (runs.length && t === ' ')) runs.push({ t, cs }); }
          else if (c.nodeType === 1 && c.tagName !== 'svg') {
            const ccs = getComputedStyle(c);
            if (ccs.display === 'none') continue;
            if (ccs.display === 'block' && runs.length) runs.push({ t: '\n', cs: ccs });
            const cr = ccs.counterReset.match(/^\S+\s+(-?\d+)/);
            const after = getComputedStyle(c, '::after').content;
            walk(c, ccs);
            if (cr && after && after.includes('counter')) runs.push({ t: cr[1] + ((after.match(/"([^"]*)"\s*$/) || [])[1] || ''), cs: ccs });
          }
        }
      };
      walk(el, getComputedStyle(el));
      let s = runs.map(r => r.t).join('').replace(/ *\n */g, '\n');
      // trim and rebuild ranges
      let out = [], pos = 0, text = '';
      runs.forEach(r => { let t = r.t; if (text === '' ) t = t.replace(/^\s+/, ''); if (text.endsWith('\n')) t = t.replace(/^ +/, ''); if (t === '\n') text = text.replace(/ +$/, ''); if (!t) return;
        out.push({ start: text.length, end: text.length + t.length, size: parseFloat(r.cs.fontSize), weight: FW[r.cs.fontWeight] || 'Regular', family: famOf(r.cs), color: col(r.cs.color), ls: parseFloat(r.cs.letterSpacing) || 0,
          lh: r.cs.lineHeight === 'normal' ? null : parseFloat(r.cs.lineHeight) }); text += t; });
      text = text.replace(/\s+$/, '');
      out.forEach(o => { o.end = Math.min(o.end, text.length); }); out = out.filter(o => o.end > o.start);
      return { text, runs: out };
    }
    let uid = 0;
    function nameOf(el) {
      return el.getAttribute('aria-label') || (el.className && typeof el.className === 'string' && el.className.split(' ')[0]) || el.tagName.toLowerCase();
    }
    function walk(el, parentBox, accOp, outArr) {
      const cs = getComputedStyle(el);
      if (cs.display === 'none' || cs.visibility === 'hidden') return;
      const op = accOp * (+cs.opacity);
      if (op < 0.01) return;
      const r = el.getBoundingClientRect();
      const box = { x: r.left - R.left, y: r.top - R.top, w: r.width, h: r.height };
      if (el.tagName === 'svg' || el.tagName === 'SVG') {
        const c = el.cloneNode(true); const color = cs.color;
        c.setAttribute('width', r.width); c.setAttribute('height', r.height); c.removeAttribute('class'); c.removeAttribute('style');
        const svg = c.outerHTML.replace(/currentColor/g, color);
        outArr.push({ k: 'svg', name: 'icon', x: box.x - parentBox.x, y: box.y - parentBox.y, w: box.w, h: box.h, svg, opacity: op });
        return;
      }
      if (rast.some(s => el.matches(s))) {
        const v = visual(el, cs, box.w, box.h);
        el.setAttribute('data-rast', String(rasters.length));
        rasters.push({ i: rasters.length, w: box.w, h: box.h });
        outArr.push({ k: 'frame', name: 'avatar', x: box.x - parentBox.x, y: box.y - parentBox.y, w: box.w, h: box.h, radius: v.radius, fills: [], strokes: [], effects: v.effects, clip: true, opacity: op, raster: rasters.length - 1, children: [] });
        return;
      }
      const v = visual(el, cs, box.w, box.h);
      const hasDirectText = Array.from(el.childNodes).some(n => n.nodeType === 3 && n.textContent.trim());
      const hasVis = el !== root && (v.fills.length || v.strokes.length || v.effects.length || v.textFills);
      let node = null, kids = outArr, myBox = parentBox, childOp = op;
      if (el === root) { node = null; }
      else if (hasVis && !(v.textFills)) {
        node = { k: 'frame', name: nameOf(el), x: box.x - parentBox.x, y: box.y - parentBox.y, w: box.w, h: box.h, radius: v.radius, fills: v.fills, strokes: v.strokes, strokeWeight: v.strokeWeight, effects: v.effects, clip: v.clip, opacity: op, children: [] };
        outArr.push(node); kids = node.children; myBox = box; childOp = 1;
      }
      if (hasDirectText) {
        const tr = textRuns(el);
        if (tr.text) {
          const rg = document.createRange(); rg.selectNodeContents(el); const rb = rg.getBoundingClientRect();
          const pl = parseFloat(cs.paddingLeft), pr = parseFloat(cs.paddingRight), blw = parseFloat(cs.borderLeftWidth) || 0;
          const center = cs.textAlign === 'center' || cs.textAlign === 'right' || cs.textAlign === 'end';
          const tx = center ? box.x + pl + blw : rb.left - R.left, tw = center ? box.w - pl - pr - 2 * blw : rb.width + 1;
          const t = { k: 'text', name: tr.text.slice(0, 40), x: tx - myBox.x, y: rb.top - R.top - myBox.y, w: tw, h: rb.height, align: center ? (cs.textAlign === 'center' ? 'CENTER' : 'RIGHT') : 'LEFT', wrap: center,
            text: tr.text, runs: tr.runs, opacity: node ? 1 : op, fills: v.textFills };
          const ts = parseFloat(cs.webkitTextStrokeWidth) || 0;
          if (ts > 0) { t.strokeCopy = true; }
          kids.push(t);
          // svgs / visual children inside a text element (e.g. icons in buttons) still need emitting
          for (const c of el.children) if (c.tagName.toLowerCase() === 'svg') walk(c, myBox, childOp, kids);
          return;
        }
      }
      for (const c of el.children) walk(c, myBox, childOp, kids);
    }
    const tree = []; walk(root, { x: 0, y: 0 }, 1, tree);
    // merge stroke copies of gradient text into the gradient text as an outside stroke
    const fix = arr => { for (let i = 0; i < arr.length; i++) { const n = arr[i];
      if (n.k === 'text' && n.strokeCopy && arr[i + 1] && arr[i + 1].k === 'text' && arr[i + 1].text === n.text) { arr[i + 1].outline = { w: parseFloat(getComputedStyle(document.body).fontSize) ? 2 : 2, color: { r: 1, g: 1, b: 1 } }; arr.splice(i, 1); i--; }
      if (n.children) fix(n.children); } };
    fix(tree);
    const rcs = getComputedStyle(root);
    const v = visual(root, rcs, 402, 874);
    return { root: { w: 402, h: 874, fills: v.fills }, tree, rasters };
  }, rast);
  // raster renders: isolate each element (no outer shadow), 2x
  for (const r of res.rasters) {
    const el = await p.$(`[data-rast="${r.i}"]`);
    await p.evaluate(e => { e.__bs = e.style.boxShadow; e.style.boxShadow = 'none'; }, el);
    const png = await el.screenshot({ omitBackground: true });
    r.b64 = png.toString('base64');
    await p.evaluate(e => { e.style.boxShadow = e.__bs; }, el);
  }
  await b.close();
  fs.writeFileSync(out, JSON.stringify(res));
  console.log('nodes', JSON.stringify(res.tree).length, 'rasters', res.rasters.length);
})();
