"""Lottie for the 'No match this time' visual (VoiceFail board): dashed orbit + 2 dots slowly rotating,
greyed orb floating up and down."""
import json, base64
FPS = 30
L = 27.0                      # 6 float cycles of 4.5 s; orbit 360° per 27 s (web: 26 s, <4% slower, seamless loop)
OP = round(L * FPS)
W = H = 240; CX = CY = 120    # orb/orbit centre
def f(t): return round(t * FPS, 3)
LIN = (0, 0, 1, 1); IO = (0.42, 0, 0.58, 1)
def kf(t, v, e=LIN):
    s = v if isinstance(v, list) else [v]; n = len(s)
    return {"t": f(t), "s": s, "o": {"x": [e[0]] * n, "y": [e[1]] * n}, "i": {"x": [e[2]] * n, "y": [e[3]] * n}}
st = lambda v: {"a": 0, "k": v}; an = lambda k: {"a": 1, "k": k}
def tr(): return {"ty": "tr", "p": st([0, 0]), "a": st([0, 0]), "s": st([100, 100]), "r": st(0), "o": st(100), "sk": st(0), "sa": st(0)}
def ks(p=(CX, CY), a=(CX, CY), s=None, r=None, o=None):
    return {"p": p if isinstance(p, dict) else st([p[0], p[1], 0]), "a": st([a[0], a[1], 0]), "s": s or st([100, 100, 100]), "r": r or st(0), "o": o or st(100)}
def el(d, c): return {"ty": "el", "p": st(list(c)), "s": st([d, d]), "d": 1}
def fill(rgb, a=100): return {"ty": "fl", "c": st(rgb + [1]), "o": st(a), "r": 1, "bm": 0}
def hexc(h): h = h.lstrip('#'); return [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
def grp(n, it): return {"ty": "gr", "nm": n, "it": it + [tr()]}
def lay(ind, nm, shapes, k, ty=4, extra=None):
    d = {"ddd": 0, "ind": ind, "ty": ty, "nm": nm, "sr": 1, "ks": k, "ao": 0, "ip": 0, "op": OP, "st": 0, "bm": 0}
    if ty == 4: d["shapes"] = shapes
    if extra: d.update(extra)
    return d

# orbit: 190 box, 1.5px dashed border (stroke centred at r = 94.25), rgba(130,112,180,.40)
B0 = (CX - 95, CY - 95)
orbit = grp('orbit', [el(188.5, (CX, CY)), {"ty": "st", "c": st(hexc('#8270B4') + [1]), "o": st(40), "w": st(1.5), "lc": 1, "lj": 1, "ml": 4, "bm": 0,
                     "d": [{"n": "d", "nm": "dash", "v": st(3)}, {"n": "g", "nm": "gap", "v": st(3.2)}, {"n": "o", "nm": "offset", "v": st(0)}]}])
dot1 = grp('dot 1', [el(9, (B0[0] + 26.5, B0[1] + 24.5)), fill(hexc('#C9BDE6'))])
dot2 = grp('dot 2', [el(6, (B0[0] + 179, B0[1] + 135)), fill(hexc('#D8CFEA'))])
orbit_layer = lay(3, 'orbit + dots (360° / 27 s)', [dot1, dot2, orbit], ks(r=an([kf(0, 0), kf(L, 360)])))

# orb: 120 px, grayscale(.6) brightness(1.04) baked into the image, opacity .82, floats -5 px every 4.5 s
img = base64.b64encode(open('orb_gray_iq.png', 'rb').read()).decode()
pk = []
t = 0.0
while t < L - 1e-6:
    pk += [kf(t, [CX, CY, 0], IO), kf(t + 2.25, [CX, CY - 5, 0], IO)]; t += 4.5
pk.append(kf(L, [CX, CY, 0]))
IMG = 240   # asset is 240 px (2×); scale 50 % → 120
orb = {"ddd": 0, "ind": 1, "ty": 2, "nm": "orb (greyed)", "refId": "orb", "sr": 1, "ao": 0, "ip": 0, "op": OP, "st": 0, "bm": 0,
       "ks": {"p": an(pk), "a": st([IMG / 2, IMG / 2, 0]), "s": st([50, 50, 100]), "r": st(0), "o": st(82)}}
# shadow 0 16 36 rgba(110,95,160,.22): radial-gradient ellipse, floats with the orb
sc = hexc('#6E5FA0')
shadow_g = {"ty": "gf", "o": st(100), "r": 1, "bm": 0, "t": 2, "h": st(0), "a": st(0),
            "g": {"p": 3, "k": st([0, *sc, .5, *sc, 1, *sc, 0, .16, .5, .11, 1, 0])},
            "s": st([CX, CY + 16]), "e": st([CX + 96, CY + 16])}
shadow = lay(2, 'orb shadow', [grp('shadow', [el(192, (CX, CY + 16)), shadow_g])], ks(p=an([dict(k, s=[k["s"][0], k["s"][1], 0]) for k in pk])))
data = {"v": "5.12.2", "fr": FPS, "ip": 0, "op": OP, "w": W, "h": H, "nm": "voice_match_failed_orb", "ddd": 0,
        "assets": [{"id": "orb", "w": IMG, "h": IMG, "u": "", "p": "data:image/png;base64," + img, "e": 1}],
        "layers": [orb, shadow, orbit_layer]}
json.dump(data, open('voice_fail_orb.json', 'w'), separators=(',', ':'))
print(OP, len(json.dumps(data, separators=(',', ':'))))
