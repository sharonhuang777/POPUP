# Build a Lottie (bodymovin 5.x JSON) from lottie_sample.js output.
# python3 make_lottie.py <sampleDir> <out.json> <name> [markers "name:sec,name:sec"] [loopFrom-sec]
#
# Every element becomes one shape layer whose transform is the browser's own per-frame matrix (simplified to the fewest
# linear keyframes within ~0.1px / 0.15deg), so timing and easing match the canvas board exactly.
# Looks are converted to features every Lottie player supports (iOS / Android / Web): ellipse / rounded rect, solid and
# gradient fills, strokes, image layers with an ellipse mask. Blurs and glows are baked into radial-gradient profiles
# measured from an isolated render of the element, so no blur effects or blend modes are needed at runtime.
import json, sys, math, re, base64, io
import numpy as np
from PIL import Image

D, OUT, NAME = sys.argv[1], sys.argv[2], sys.argv[3]
MARK = sys.argv[4] if len(sys.argv) > 4 else ''
S_ = json.load(open(f'{D}/sample.json'))
FPS, N, SC, C0 = S_['fps'], S_['N'], S_['scale'], S_['shotCenter']
ITEMS = S_['items']

# ---------------- helpers ----------------
def st(v): return {'a': 0, 'k': v}

def parse_color(s):
    m = re.match(r'rgba?\(([^)]+)\)', s.strip())
    if not m: return None
    p = [float(x) for x in re.split(r'[ ,/]+', m.group(1).strip()) if x]
    if len(p) == 3: p.append(1.0)
    return [p[0] / 255, p[1] / 255, p[2] / 255, p[3]]

def split_top(s):
    out, depth, cur = [], 0, ''
    for ch in s:
        if ch == '(': depth += 1
        if ch == ')': depth -= 1
        if ch == ',' and depth == 0: out.append(cur.strip()); cur = ''
        else: cur += ch
    if cur.strip(): out.append(cur.strip())
    return out

def tr(p=(0, 0), s=(100, 100), r=0, o=100):
    return {'ty': 'tr', 'p': st(list(p)), 'a': st([0, 0]), 's': st(list(s)), 'r': st(r), 'o': st(o), 'sk': st(0), 'sa': st(0)}

def ellipse(cx, cy, w, h): return {'ty': 'el', 'd': 1, 'p': st([cx, cy]), 's': st([w, h])}
def rrect(cx, cy, w, h, r): return {'ty': 'rc', 'd': 1, 'p': st([cx, cy]), 's': st([w, h]), 'r': st(r)}
def fill(c, o=100, rule=1): return {'ty': 'fl', 'c': st([c[0], c[1], c[2], 1]), 'o': st(o), 'r': rule}
def stroke(c, w, o=100): return {'ty': 'st', 'c': st([c[0], c[1], c[2], 1]), 'o': st(o), 'w': st(w), 'lc': 2, 'lj': 2, 'ml': 4}
def group(items, name='g', t=None): return {'ty': 'gr', 'nm': name, 'it': items + [t or tr()]}

def gfill(stops, s, e, kind, o=100, rule=1):
    """stops: [(pos, r,g,b,a)] unpremultiplied, pos 0..1"""
    col, alp = [], []
    for p, r, g, b, a in stops: col += [round(p, 4), round(r, 4), round(g, 4), round(b, 4)]
    for p, r, g, b, a in stops: alp += [round(p, 4), round(a, 4)]
    return {'ty': 'gf', 'o': st(o), 'r': rule, 'g': {'p': len(stops), 'k': st(col + alp)},
            's': st(list(s)), 'e': st(list(e)), 't': kind, 'h': st(0), 'a': st(0)}

def simplify_curve(xs, ys, tol):
    """Greedy: keep the fewest points so linear interpolation stays within tol (ys: list of vectors)."""
    ys = np.asarray(ys, float); keep = [0]; a = 0; n = len(xs)
    while a < n - 1:
        b = a + 1
        while b + 1 < n:
            c = b + 1
            t = (np.asarray(xs[a + 1:c]) - xs[a]) / (xs[c] - xs[a])
            lin = ys[a] + (ys[c] - ys[a]) * t[:, None]
            if np.max(np.abs(lin - ys[a + 1:c])) > tol: break
            b = c
        keep.append(b); a = b
    return keep

def anim(vals, frames, tol):
    vals = np.asarray(vals, float)
    if vals.ndim == 1: vals = vals[:, None]
    if np.max(np.ptp(vals, axis=0)) <= tol:
        v = [round(x, 3) for x in vals[0]]
        return st(v if len(v) > 1 else v[0])
    keep = simplify_curve(frames, vals, tol)
    d = vals.shape[1]; ks = []
    for j, i in enumerate(keep):
        k = {'t': frames[i], 's': [round(x, 3) for x in vals[i]]}
        if j < len(keep) - 1: k['i'] = {'x': [1] * d, 'y': [1] * d}; k['o'] = {'x': [0] * d, 'y': [0] * d}
        ks.append(k)
    return {'a': 1, 'k': ks}

# ---------------- profiles from isolated renders ----------------
def load_premult(name):
    im = np.asarray(Image.open(f'{D}/{name}').convert('RGBA'), float) / 255.0
    a = im[..., 3:4]; return np.concatenate([im[..., :3] * a, a], axis=2)

def radial_profile(img, w, h, step=0.25):
    """Average premultiplied RGBA vs normalized radius (unit = half-width), returns (u array, rgba premult array, uMax)."""
    H, W, _ = img.shape; c = C0 * SC
    yy, xx = np.mgrid[0:H, 0:W]
    dx = (xx + .5 - c) / SC; dy = (yy + .5 - c) / SC
    u = np.sqrt((dx / (w / 2)) ** 2 + (dy / (h / 2)) ** 2) if w != h else np.sqrt(dx * dx + dy * dy) / (w / 2)
    du = step / (w / 2)
    idx = (u / du).astype(int); nb = idx.max() + 1
    cnt = np.bincount(idx.ravel(), minlength=nb)
    prof = np.stack([np.bincount(idx.ravel(), weights=img[..., ch].ravel(), minlength=nb) for ch in range(4)], 1)
    prof = prof / np.maximum(cnt, 1)[:, None]
    us = (np.arange(nb) + .5) * du
    alive = np.where(prof[:, 3] > 0.002)[0]
    if len(alive) == 0: return None
    last = min(alive[-1] + 3, nb - 1)
    us, prof = us[:last + 1], prof[:last + 1]
    us = np.concatenate([[0], us]); prof = np.concatenate([prof[:1], prof])
    prof[-1] = 0
    return us, prof, us[-1]

def profile_stops(us, prof, umax, tol=0.006, maxn=24):
    keep = simplify_curve(list(us), prof, tol)
    while len(keep) > maxn:
        tol *= 1.4; keep = simplify_curve(list(us), prof, tol)
    stops = []
    for i in keep:
        r, g, b, a = prof[i]
        col = (r / a, g / a, b / a) if a > 1e-4 else None
        stops.append([us[i] / umax, col, a])
    # fill colours of near-transparent stops from neighbours (unpremultiplied colour is undefined there)
    cols = [s[1] for s in stops]
    for i, s in enumerate(stops):
        if s[1] is None:
            nb = [cols[j] for j in sorted(range(len(cols)), key=lambda j: abs(j - i)) if cols[j] is not None]
            s[1] = nb[0] if nb else (1, 1, 1)
    return [(p, min(1, c[0]), min(1, c[1]), min(1, c[2]), min(1, a)) for p, c, a in stops]

def radial_group(img, w, h, name, path=None, cx=None, cy=None):
    rp = radial_profile(img, w, h)
    if rp is None: return None
    us, prof, umax = rp
    stops = profile_stops(us, prof, umax)
    cx = w / 2 if cx is None else cx; cy = h / 2 if cy is None else cy
    if path is None:
        shp = ellipse(0, 0, 2 * umax, 2 * umax)
        return group([shp, gfill(stops, (0, 0), (umax, 0), 2)], name, tr((cx, cy), (w / 2 * 100, h / 2 * 100)))
    return group([path, gfill(stops, (0, 0), (umax * w / 2, 0), 2)], name, tr((cx, cy)))

def wedge_path(a0, a1, R):
    pts = [[0, 0]]
    n = max(2, int(math.ceil((a1 - a0) / 2)))
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        pts.append([round(R * math.sin(a), 3), round(-R * math.cos(a), 3)])
    z = [[0, 0]] * len(pts)
    return {'ty': 'sh', 'ks': st({'c': True, 'v': pts, 'i': z, 'o': z})}

def polar_groups(img, w, name, binw=3.0):
    """Angle-dependent soft ring (e.g. conic-gradient arc): one radial-gradient wedge per run of similar angles."""
    H, W, _ = img.shape; c = C0 * SC
    yy, xx = np.mgrid[0:H, 0:W]
    dx = (xx + .5 - c) / SC; dy = (yy + .5 - c) / SC
    rr = np.sqrt(dx * dx + dy * dy); ang = (np.degrees(np.arctan2(dx, -dy)) + 360) % 360
    step = 0.5; ri = (rr / step).astype(int); nr = ri.max() + 1
    nbins = int(360 / binw); ai = (ang / binw).astype(int) % nbins
    key = ai * nr + ri
    cnt = np.bincount(key.ravel(), minlength=nbins * nr).reshape(nbins, nr)
    prof = np.stack([np.bincount(key.ravel(), weights=img[..., ch].ravel(), minlength=nbins * nr).reshape(nbins, nr) for ch in range(4)], 2)
    prof = prof / np.maximum(cnt, 1)[..., None]
    alive = np.where(prof[..., 3].max(0) > 0.002)[0]
    rmax = (alive[-1] + 3) * step; nrr = alive[-1] + 4
    prof = prof[:, :nrr]; rs = (np.arange(nrr) + .5) * step
    rs = np.concatenate([[0], rs]); prof = np.concatenate([prof[:, :1], prof], 1); prof[:, -1] = 0
    runs, i = [], 0
    while i < nbins:
        if prof[i, :, 3].max() < 0.004: i += 1; continue
        j = i + 1
        while j < nbins and prof[j, :, 3].max() >= 0.004 and np.max(np.abs(prof[j] - prof[i])) < 0.012: j += 1
        runs.append((i, j)); i = j
    out = []
    for i, j in runs:
        p = prof[i:j].mean(0)
        stops = profile_stops(list(rs), p, rmax)
        out.append(group([wedge_path(i * binw - 0.15, j * binw + 0.15, rmax + 1), gfill(stops, (0, 0), (rmax, 0), 2)],
                         f'{name} {i * binw:.0f}-{j * binw:.0f}deg', tr((w / 2, w / 2))))
    return out

def blurred_disc(R, sigma, res=0.5):
    """Radial profile (alpha) of a disc of radius R blurred by a gaussian sigma (box-shadow blur = 2 sigma)."""
    ext = R + 4 * sigma + 2; n = int(2 * ext / res) | 1
    ax = (np.arange(n) - n // 2) * res
    X, Y = np.meshgrid(ax, ax); disc = ((X * X + Y * Y) <= R * R).astype(float)
    g = np.exp(-(ax ** 2) / (2 * sigma * sigma)); g /= g.sum()
    b = np.apply_along_axis(lambda v: np.convolve(v, g, 'same'), 0, disc)
    b = np.apply_along_axis(lambda v: np.convolve(v, g, 'same'), 1, b)
    row = b[n // 2, n // 2:]; rs = ax[n // 2:]
    alive = np.where(row > 0.002)[0]; last = alive[-1] + 2
    return rs[:last + 1], row[:last + 1]

def parse_shadows(s):
    if not s or s == 'none': return []
    out = []
    for part in split_top(s):
        col = re.search(r'rgba?\([^)]*\)', part); c = parse_color(col.group(0)) if col else [0, 0, 0, 1]
        nums = [float(x) for x in re.findall(r'(-?[\d.]+)px', part.replace(col.group(0), '') if col else part)]
        nums += [0] * (4 - len(nums))
        out.append({'c': c, 'x': nums[0], 'y': nums[1], 'blur': nums[2], 'spread': nums[3], 'inset': 'inset' in part})
    return out

def shadow_groups(w, h, shadows):
    gs = []
    for sh in reversed([s for s in shadows if not s['inset']]):
        cx, cy, R = w / 2 + sh['x'], h / 2 + sh['y'], w / 2 + sh['spread']
        if sh['blur'] <= 0:
            gs.append(group([ellipse(0, 0, 2 * R, 2 * R), fill(sh['c'], sh['c'][3] * 100)], 'ring', tr((cx, cy))))
        else:
            rs, a = blurred_disc(R, sh['blur'] / 2)
            prof = np.stack([np.full_like(a, sh['c'][0]) * a, np.full_like(a, sh['c'][1]) * a, np.full_like(a, sh['c'][2]) * a, a * sh['c'][3]], 1)
            prof[-1] = 0
            stops = profile_stops(list(rs), prof, rs[-1])
            gs.append(group([ellipse(0, 0, 2 * rs[-1], 2 * rs[-1]), gfill(stops, (0, 0), (rs[-1], 0), 2)], 'shadow', tr((cx, cy))))
    return gs

def sdf_rrect(dx, dy, w, h, r):
    qx = np.abs(dx) - (w / 2 - r); qy = np.abs(dy) - (h / 2 - r)
    return np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2) + np.minimum(np.maximum(qx, qy), 0) - r

def sdf_profile(img, w, h, r, step=0.5):
    H, W, _ = img.shape; c = C0 * SC
    yy, xx = np.mgrid[0:H, 0:W]
    d = sdf_rrect((xx + .5 - c) / SC, (yy + .5 - c) / SC, w, h, r)
    lo = -min(w, h) / 2
    idx = np.clip(((d - lo) / step).astype(int), 0, None); nb = idx.max() + 1
    cnt = np.bincount(idx.ravel(), minlength=nb)
    prof = np.stack([np.bincount(idx.ravel(), weights=img[..., ch].ravel(), minlength=nb) for ch in range(4)], 1) / np.maximum(cnt, 1)[:, None]
    ds = lo + (np.arange(nb) + .5) * step
    return ds, prof, step

def band_groups(w, h, r, ds, alpha, step, paint, name, merge=0.025):
    """Non-overlapping rounded-rect rings (even-odd) whose opacity follows alpha(d) — a portable stand-in for blur."""
    alive = np.where(alpha > 0.003)[0]
    if len(alive) == 0: return []
    bands, i = [], alive[0]
    while i <= alive[-1]:
        j = i + 1
        while j <= alive[-1] and abs(alpha[j] - alpha[i]) < merge: j += 1
        bands.append((ds[i] - step / 2, ds[j - 1] + step / 2, float(alpha[i:j].mean()))); i = j
    out = []
    for d0, d1, a in bands:
        if a < 0.003: continue
        W1, H1 = w + 2 * d1, h + 2 * d1
        if W1 <= 0 or H1 <= 0: continue
        its = [rrect(w / 2, h / 2, W1, H1, max(0, min(r + d1, min(W1, H1) / 2)))]
        W0, H0 = w + 2 * d0, h + 2 * d0
        if W0 > 0.2 and H0 > 0.2: its.append(rrect(w / 2, h / 2, W0, H0, max(0, min(r + d0, min(W0, H0) / 2))))
        out.append(group(its + [paint(min(100, a * 100))], f'{name} {d0:+.1f}..{d1:+.1f}'))
    return out

def parse_linear(bgi, w, h):
    m = re.match(r'linear-gradient\((.*)\)$', bgi.strip())
    parts = split_top(m.group(1)); ang = 180
    if parts and re.match(r'^-?[\d.]+deg$', parts[0]): ang = float(parts[0][:-3]); parts = parts[1:]
    elif parts and parts[0].startswith('to '):
        ang = {'to right': 90, 'to left': 270, 'to top': 0, 'to bottom': 180}.get(parts[0], 180); parts = parts[1:]
    cols = []
    for i, p in enumerate(parts):
        col = re.search(r'rgba?\([^)]*\)', p); pos = re.search(r'([\d.]+)%', p.replace(col.group(0), ''))
        cols.append([float(pos.group(1)) / 100 if pos else None, parse_color(col.group(0))])
    if cols[0][0] is None: cols[0][0] = 0
    if cols[-1][0] is None: cols[-1][0] = 1
    for i, cc in enumerate(cols):
        if cc[0] is None:
            j = next(k for k in range(i + 1, len(cols)) if cols[k][0] is not None)
            cc[0] = cols[i - 1][0] + (cols[j][0] - cols[i - 1][0]) / (j - i + 1)
    a = math.radians(ang); dx, dy = math.sin(a), -math.cos(a)
    L = abs(w * dx) + abs(h * dy)
    s = (w / 2 - dx * L / 2, h / 2 - dy * L / 2); e = (w / 2 + dx * L / 2, h / 2 + dy * L / 2)
    return [(p, c[0], c[1], c[2], c[3]) for p, c in cols], s, e

def radius_px(br, w, h):
    v = br.split()[0]
    return min(w, h) / 2 * float(v[:-1]) / 50 if v.endswith('%') else float(v[:-2] if v.endswith('px') else v)

# ---------------- layers ----------------
assets, layers = [], []
els = sorted(S_['els'], key=lambda e: e['order'])
nameCount = {}
ind = 0
for e in els:
    it = ITEMS[e['item']]; kind = it['kind']; w, h = e['w'], e['h']; sty = e['style']
    fr = np.asarray(e['frames'], float)
    p0 = fr[:, 0:2]; c1 = (fr[:, 2:4] - p0) / 100; c2 = (fr[:, 4:6] - p0) / 100; op = fr[:, 6]
    sx = np.hypot(c1[:, 0], c1[:, 1]); rot = np.degrees(np.arctan2(c1[:, 1], c1[:, 0]))
    sy = (c1[:, 0] * c2[:, 1] - c1[:, 1] * c2[:, 0]) / np.maximum(sx, 1e-6)
    rot = np.degrees(np.unwrap(np.radians(rot)))
    vis = np.where(op > 0.002)[0]
    if len(vis) == 0: continue
    ip = max(0, vis[0] - 1); opf = min(N, vis[-1] + 1)
    sl = slice(ip, opf + 1); frames = list(range(ip, opf + 1))
    ks = {'o': anim(op[sl] * 100, frames, 0.3), 'r': anim(rot[sl], frames, 0.15),
          'p': {'s': True, 'x': anim(p0[sl, 0], frames, 0.08), 'y': anim(p0[sl, 1], frames, 0.08)},
          'a': st([0, 0, 0]), 's': anim(np.stack([sx[sl] * 100, sy[sl] * 100, np.full(len(frames), 100.0)], 1), frames, 0.15)}
    base = it.get('name') or it['sel'].strip('.').replace(' ', '_')
    nameCount[base] = nameCount.get(base, 0) + 1
    nm = base if it.get('name') else f'{base} {nameCount[base]}'
    shapes = []
    if kind == 'shape':
        r = radius_px(sty['br'], w, h); circle = abs(w - h) < .01 and r >= w / 2 - .01
        bg = parse_color(sty['bg']); bw = sty['bw']; bc = parse_color(sty['bc'])
        if bg and bg[3] > 0:
            shapes.append(group([ellipse(w / 2, h / 2, w, h) if circle else rrect(w / 2, h / 2, w, h, min(r, min(w, h) / 2)), fill(bg, bg[3] * 100)], 'fill'))
        if bw > 0 and bc and bc[3] > 0:
            iw, ih = w - bw, h - bw
            shapes.append(group([ellipse(w / 2, h / 2, iw, ih) if circle else rrect(w / 2, h / 2, iw, ih, max(0, r - bw / 2)), stroke(bc, bw, bc[3] * 100)], 'border'))
    elif kind == 'radial':
        g = radial_group(load_premult(e['shots']['plain']), w, h, 'glow')
        if g: shapes.append(g)
    elif kind == 'polar':
        for ci, ck in it['children']:
            img = load_premult(e['shots'][f'c{ci}'])
            if ck == 'radial':
                g = radial_group(img, w, h, f'ring base');  shapes.append(g) if g else None
            else:
                shapes += polar_groups(img, w, 'arc')
    elif kind == 'soft':
        r = radius_px(sty['br'], w, h)
        ds, cov, step = sdf_profile(load_premult(e['shots']['coverage']), w, h, r)
        ds2, shp, _ = sdf_profile(load_premult(e['shots']['shadow']), w, h, r)
        sh_a = shp[:, 3]; tot = np.sum(shp[:, :3], 0); ca = max(np.sum(sh_a), 1e-6)
        shc = [min(1, x / ca) for x in tot]
        shapes += band_groups(w, h, r, ds2, sh_a, step, lambda o: fill(shc, o, 2), 'glow band')
        if sty['bgi'] and sty['bgi'].startswith('linear-gradient'):
            stops, s, e2 = parse_linear(sty['bgi'], w, h)
            paint = lambda o, stops=stops, s=s, e2=e2: gfill(stops, s, e2, 1, o, 2)
        else:
            bg = parse_color(sty['bg']); paint = lambda o, bg=bg: fill(bg, o * bg[3], 2)
        shapes += band_groups(w, h, r, ds, cov[:, 3], step, paint, 'body band')
        shapes.reverse()  # Lottie: first item on top -> body above glow
    elif kind == 'avatar':
        shapes += shadow_groups(w, h, parse_shadows(sty['bs']))
        shapes.reverse()
        im = Image.open(f"{D}/{e['shots']['image']}").convert('RGB')
        c = C0 * SC; box = (int(round((C0 - w / 2) * SC)), int(round((C0 - h / 2) * SC)), int(round((C0 + w / 2) * SC)), int(round((C0 + h / 2) * SC)))
        im = im.crop(box).resize((int(w * 2), int(h * 2)), Image.LANCZOS)
        buf = io.BytesIO(); im.save(buf, 'JPEG', quality=86)
        aid = it.get('name', f'avatar_{ind}')
        assets.append({'id': aid, 'w': w, 'h': h, 'u': '', 'p': 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode(), 'e': 1})
        k = 0.5523 * w / 2; cx, cy, R = w / 2, h / 2, w / 2
        mask = {'c': True, 'v': [[cx, cy - R], [cx + R, cy], [cx, cy + R], [cx - R, cy]],
                'i': [[-k, 0], [0, -k], [k, 0], [0, k]], 'o': [[k, 0], [0, k], [-k, 0], [0, -k]]}
        ind += 1
        layers.append({'ddd': 0, 'ind': ind, 'ty': 2, 'nm': aid, 'refId': aid, 'sr': 1, 'ks': ks, 'ao': 0, 'hasMask': True,
                       'masksProperties': [{'inv': False, 'mode': 'a', 'pt': st(mask), 'o': st(100), 'x': st(0), 'nm': 'circle'}],
                       'ip': ip, 'op': opf + 1, 'st': 0, 'bm': 0, '_z': e['order'] + 0.5})
        nm = aid + ' ring+shadow'
    if not shapes: continue
    ind += 1
    layers.append({'ddd': 0, 'ind': ind, 'ty': 4, 'nm': nm, 'sr': 1, 'ks': ks, 'ao': 0, 'shapes': shapes,
                   'ip': ip, 'op': opf + 1, 'st': 0, 'bm': 0, '_z': e['order']})

layers.sort(key=lambda l: -l['_z'])
for i, l in enumerate(layers): l.pop('_z'); l['ind'] = i + 1
markers = []
for m in [x for x in MARK.split(',') if x]:
    n, t = m.split(':'); a = t.split('-')
    fr0 = round(float(a[0]) * FPS)
    markers.append({'tm': fr0, 'cm': n, 'dr': round(float(a[1]) * FPS) - fr0 if len(a) > 1 else 0})
doc = {'v': '5.7.4', 'fr': FPS, 'ip': 0, 'op': N, 'w': 402, 'h': 874, 'nm': NAME, 'ddd': 0,
       'assets': assets, 'layers': layers, 'markers': markers}
json.dump(doc, open(OUT, 'w'), separators=(',', ':'), default=lambda o: o.item())
import os
print(json.dumps({'out': OUT, 'layers': len(layers), 'kb': os.path.getsize(OUT) // 1024}))
