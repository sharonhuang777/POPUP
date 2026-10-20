"""Build a Lottie (bodymovin) JSON for the "It's your turn" call animation (VoiceTurn board)."""
import json, math, re

FPS = 60
INTRO = 0.7          # orb pop
LOOP = 14.4          # lcm(1.8 ring period, 1.6 breathe/icon period)
OP = round((INTRO + LOOP) * FPS)   # 906
W = H = 280
CX = CY = 140

def f(t): return round(t * FPS, 3)

# ---------- cubic-bezier easing helpers ----------
def bez(p1x, p1y, p2x, p2y):
    def x_of(s): return 3*(1-s)**2*s*p1x + 3*(1-s)*s*s*p2x + s**3
    def y_of(s): return 3*(1-s)**2*s*p1y + 3*(1-s)*s*s*p2y + s**3
    def ease(x):
        lo, hi = 0.0, 1.0
        for _ in range(60):
            mid = (lo + hi) / 2
            if x_of(mid) < x: lo = mid
            else: hi = mid
        return y_of((lo + hi) / 2)
    return ease

LINEAR = (0, 0, 1, 1)
def kf(t, v, ease=LINEAR, hold=False):
    k = {"t": f(t), "s": v if isinstance(v, list) else [v]}
    if hold:
        k["h"] = 1
    elif ease:
        x1, y1, x2, y2 = ease
        n = len(k["s"])
        k["o"] = {"x": [x1] * n, "y": [y1] * n}
        k["i"] = {"x": [x2] * n, "y": [y2] * n}
    return k

def anim(kfs): return {"a": 1, "k": kfs}
def static(v): return {"a": 0, "k": v}

def tr(p=(0, 0), a=(0, 0), s=(100, 100), r=0, o=100):
    return {"ty": "tr", "p": static(list(p)), "a": static(list(a)), "s": static(list(s)), "r": static(r), "o": static(o), "sk": static(0), "sa": static(0)}

def ks(p=(CX, CY), a=(CX, CY), s=None, r=None, o=None):
    return {"p": static([p[0], p[1], 0]), "a": static([a[0], a[1], 0]),
            "s": s or static([100, 100, 100]), "r": r or static(0), "o": o or static(100)}

def layer(ind, name, shapes, ksv, parent=None):
    L = {"ddd": 0, "ind": ind, "ty": 4, "nm": name, "sr": 1, "ks": ksv, "ao": 0, "shapes": shapes,
         "ip": 0, "op": OP, "st": 0, "bm": 0}
    if parent: L["parent"] = parent
    return L

def ellipse(d, c=(CX, CY)): return {"ty": "el", "p": static(list(c)), "s": static([d, d]), "d": 1}

def rgba(h, a=1.0):
    h = h.lstrip('#'); return [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)], a

def gstops(stops):
    """stops: [(pos, (r,g,b), alpha)] -> lottie gradient array (colour stops then alpha stops)."""
    col = []; al = []
    for pos, c, a in stops:
        col += [pos, *[round(x, 4) for x in c]]; al += [pos, a]
    return {"p": len(stops), "k": static(col + al)}

def gfill(stops, start, end, radial=False):
    return {"ty": "gf", "o": static(100), "r": 1, "bm": 0, "g": gstops(stops),
            "s": static(list(start)), "e": static(list(end)), "t": 2 if radial else 1,
            **({"h": static(0), "a": static(0)} if radial else {})}

def gstroke(stops, start, end, w):
    return {"ty": "gs", "o": static(100), "w": static(w), "lc": 2, "lj": 2, "ml": 4, "bm": 0, "g": gstops(stops),
            "s": static(list(start)), "e": static(list(end)), "t": 1}

def group(name, items): return {"ty": "gr", "nm": name, "it": items + [tr()]}

layers = []

# ---------- rings: 160px, 2px border (stroke centred at r=79), scale .9→1.5, opacity .7→0, 1.8 s ----------
ring_ease = (0.2, 0.7, 0.3, 1)
re_fn = bez(*ring_ease)
ring_defs = [(0.0, '#FF8C6E', 0.55), (0.6, '#BE96F5', 0.55), (1.2, '#FF8C6E', 0.45)]
def ring_layer(ind, delay, colour, alpha):
    P = 1.8
    sk, ok = [], []
    # cycle that is running at t=0 (steady state, so the loop is seamless)
    n0 = math.floor((0 - delay) / P)
    start = delay + n0 * P
    t = 0.0
    while start < (INTRO + LOOP) + 1e-9:
        a_t = max(start, 0.0)
        prog = (a_t - start) / P
        e = re_fn(prog) if prog > 0 else 0.0
        s0 = 90 + 60 * e; o0 = 70 * (1 - e)
        end = start + P
        # remaining portion of the curve from prog→1 keeps the same shape: sample-based split
        if prog > 0:
            # approximate the tail with linear-in-time samples (only for the first, partial cycle)
            steps = 12
            for i in range(steps):
                tt = a_t + (end - a_t) * i / steps
                ee = re_fn((tt - start) / P)
                sk.append(kf(tt, [90 + 60 * ee] * 3)); ok.append(kf(tt, 70 * (1 - ee)))
        else:
            sk.append(kf(start, [90, 90, 100], ring_ease)); ok.append(kf(start, 70, ring_ease))
        e_end = min(end, INTRO + LOOP)
        sk.append(kf(end - 1 / FPS / 10, [150, 150, 100], hold=True)); ok.append(kf(end - 1 / FPS / 10, 0, hold=True))
        start = end
    c, _ = rgba(colour)
    shp = group('ring', [ellipse(158), {"ty": "st", "c": static(c + [1]), "o": static(alpha * 100), "w": static(2), "lc": 2, "lj": 2, "ml": 4, "bm": 0}])
    return layer(ind, f'ring {ind}', [shp], ks(s=anim(sk), o=anim(ok)))

# ---------- pop + breathe null (parent of orb and icon) ----------
pop_ease = (0.34, 1.4, 0.64, 1)
io = (0.42, 0, 0.58, 1)
pop_s = [kf(0, [60, 60, 100], pop_ease), kf(0.42, [106, 106, 100], pop_ease), kf(INTRO, [100, 100, 100], io)]
t = INTRO
while t < INTRO + LOOP - 1e-6:
    pop_s.append(kf(t + 0.8, [107, 107, 100], io)); pop_s.append(kf(t + 1.6, [100, 100, 100], io)); t += 1.6
pop_o = [kf(0, 0, pop_ease), kf(0.42, 100)]
null = {"ddd": 0, "ind": 1, "ty": 3, "nm": "orb pop + breathe", "sr": 1,
        "ks": ks(s=anim(pop_s), o=anim(pop_o)), "ao": 0, "ip": 0, "op": OP, "st": 0}

# ---------- phone icon ----------
PATH = "M7.6737 0.539717C8.26329 0.628959 8.57534 0.774166 8.87628 1.08871C9.13241 1.35649 9.38833 1.75413 9.73637 2.38744L10.1234 3.11422C11.8053 6.15337 11.704 7.42782 11.5562 8.04087C11.2891 9.11441 10.6463 9.49976 9.91836 9.91528C9.72461 10.0206 9.52945 10.1459 9.38051 10.2393L9.30329 10.2997C8.8091 10.7666 8.12467 11.4447 8.17984 12.7182C8.23196 13.9197 8.9407 15.5627 10.7994 18.0202L10.8103 18.0345C14.0191 21.9713 16.0558 22.7948 17.1133 22.863C17.5272 22.8931 17.8512 22.8137 18.1005 22.6918C18.3194 22.5847 18.4662 22.4484 18.5265 22.393L18.5945 22.3352C19.4131 21.487 19.9035 21.0161 20.3387 20.7434C20.7365 20.4941 21.1007 20.4044 21.7038 20.3949C22.2572 20.383 22.637 20.4737 23.176 20.7953C23.7555 21.1412 24.4872 21.7347 25.7344 22.7519C26.8476 23.6618 27.5946 24.3604 28.0152 24.995C28.4124 25.5943 28.5034 26.1113 28.3232 26.7153L28.3102 26.7677C28.1727 27.5104 27.7268 28.3953 27.096 29.2083C26.4669 30.019 25.6913 30.7084 24.9478 31.0892C23.9324 31.5807 22.5489 31.7424 20.9028 31.5184C19.453 31.3211 17.8467 30.8305 16.181 30.0697C12.1857 28.242 8.41987 25.0358 5.59355 21.0343C1.33886 14.9972 -0.246029 9.43057 0.82331 4.89806C1.10758 3.80581 1.63496 2.51055 3.45084 1.63858L3.48897 1.61913C4.98279 0.737721 6.56197 0.370778 7.6737 0.539717Z"
S = min(46 / 29, 52 / 33)
OX = CX - 23 + (46 - 29 * S) / 2
OY = CY - 26 + (52 - 33 * S) / 2
def P(x, y): return [round(OX + x * S, 3), round(OY + y * S, 3)]
def svg_to_lottie(d):
    toks = re.findall(r'[MCLZ]|-?\d*\.?\d+(?:e-?\d+)?', d)
    v, i_, o_ = [], [], []
    k = 0; cmd = None; cur = None
    nums = lambda n: [float(x) for x in toks[k:k + n]]
    while k < len(toks):
        tkn = toks[k]
        if tkn in 'MCLZ':
            cmd = tkn; k += 1
            if cmd == 'Z': break
            continue
        if cmd == 'M':
            x, y = nums(2); k += 2; cur = P(x, y); v.append(cur); i_.append([0, 0]); o_.append([0, 0])
        elif cmd == 'L':
            x, y = nums(2); k += 2; cur = P(x, y); v.append(cur); i_.append([0, 0]); o_.append([0, 0])
        elif cmd == 'C':
            x1, y1, x2, y2, x, y = nums(6); k += 6
            c1, c2, nv = P(x1, y1), P(x2, y2), P(x, y)
            o_[-1] = [round(c1[0] - v[-1][0], 3), round(c1[1] - v[-1][1], 3)]
            v.append(nv); i_.append([round(c2[0] - nv[0], 3), round(c2[1] - nv[1], 3)]); o_.append([0, 0])
    # closing: last vertex equals first → merge
    if abs(v[-1][0] - v[0][0]) < 1e-3 and abs(v[-1][1] - v[0][1]) < 1e-3:
        i_[0] = i_[-1]; v.pop(); i_.pop(); o_.pop()
    return {"ty": "sh", "ks": static({"i": i_, "o": o_, "v": v, "c": True})}

ic_ease = io
keys = [(0, 0, 100), (.05, -14, 110), (.10, 12, 110), (.15, -10, 110), (.20, 8, 108), (.25, -5, 105), (.30, 3, 102), (.40, 0, 100)]
r_k, s_k = [kf(0, 0, ic_ease)], [kf(0, [100, 100, 100], ic_ease)]
t = INTRO
while t < INTRO + LOOP - 1e-6:
    for pct, rot, sc in keys:
        r_k.append(kf(t + pct * 1.6, rot, ic_ease)); s_k.append(kf(t + pct * 1.6, [sc, sc, 100], ic_ease))
    t += 1.6
r_k.append(kf(INTRO + LOOP, 0)); s_k.append(kf(INTRO + LOOP, [100, 100, 100]))
pivot = (CX, CY - 26 + 0.55 * 52)
icon_grad = [(0, rgba('#A68DF5')[0], 1), (1, rgba('#6247C9')[0], 1)]
icon = layer(10, 'phone icon', [group('phone', [svg_to_lottie(PATH), gfill(icon_grad, P(12.8, -0.9), P(14.3, 38))])],
             ks(p=pivot, a=pivot, s=anim(s_k), r=anim(r_k), o=anim(pop_o)), parent=1)

# ---------- orb (128 px) ----------
R = 64
c1 = (CX, CY - R + 0.28 * 128)
far = math.hypot(64, 128 - 0.28 * 128)
orb_fill = gfill([(0, [1, 1, 1], .92), (.55, [246/255, 238/255, 1], .6), (1, [226/255, 214/255, 252/255], .45)], c1, (c1[0] + far, c1[1]), radial=True)
inner_shade = gfill([(0, [110/255, 90/255, 170/255], 0), (.72, [110/255, 90/255, 170/255], 0), (1, [110/255, 90/255, 170/255], .16)], (CX, CY - 14), (CX + 78, CY - 14), radial=True)
top_gloss = gfill([(0, [1, 1, 1], .55), (1, [1, 1, 1], 0)], (CX, CY - R), (CX, CY - R + 26))
ang = math.radians(150); dx, dy = math.sin(ang), -math.cos(ang); L = 128 * (abs(math.sin(ang)) + abs(math.cos(ang)))
rim = gstroke([(0, [1, 1, 1], 1), (.45, [1, 1, 1], .4), (1, [130/255, 110/255, 190/255], .45)],
              (CX - dx * L / 2, CY - dy * L / 2), (CX + dx * L / 2, CY + dy * L / 2), 1.5)
orb = layer(11, 'orb', [group('gloss', [ellipse(124), top_gloss]), group('rim', [ellipse(126.5), rim]),
                        group('inner shade', [ellipse(128), inner_shade]), group('body', [ellipse(128), orb_fill])],
            ks(o=anim(pop_o)), parent=1)
shadow = layer(12, 'orb shadow (0 18 40 rgba(130,100,210,.28))',
               [group('shadow', [ellipse(208, (CX, CY + 18)), gfill([(0, [130/255, 100/255, 210/255], .26), (.5, [130/255, 100/255, 210/255], .2), (1, [130/255, 100/255, 210/255], 0)], (CX, CY + 18), (CX + 104, CY + 18), radial=True)])],
               ks(o=anim(pop_o)), parent=1)

rings = [ring_layer(20 + i, d, c, a) for i, (d, c, a) in enumerate(ring_defs)]
anim_json = {"v": "5.12.2", "fr": FPS, "ip": 0, "op": OP, "w": W, "h": H, "nm": "voice_match_your_turn_call", "ddd": 0,
             "assets": [], "markers": [{"tm": 0, "cm": "intro", "dr": f(INTRO)}, {"tm": f(INTRO), "cm": "loop", "dr": f(LOOP)}],
             "layers": [icon, orb, shadow, null] + rings}
json.dump(anim_json, open('voice_turn_call.json', 'w'), separators=(',', ':'))
print('frames', OP, 'bytes', len(json.dumps(anim_json, separators=(',', ':'))))
