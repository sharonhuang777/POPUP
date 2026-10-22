# Text match success, North America (mist blue). The matching itself is the orb thinking page (TextThink), so this
# page is only the success beat: the two anonymous avatars rush in from the sides and collide (slow rebound), then
# "86% Match degree" fills (#FF57A8 → #F55E67) and "Chat now!" pops with falling confetti.
# Run from the canvas root: writes project/TextMatchSuccess.dc.html
import math, random

D = 4.6          # canvas loop length
LAND = .5        # avatars touch
def p(t): return f'{t / D * 100:.2f}%'

# Anonymous 3D avatars (the app's avatar set) — no real photos in matching.
ME, FINAL = 'a1.jpg', 'a3.jpg'
SIZE = 104

# ---- confetti (same physics as voice match: drag + gravity, no hang)
def confetti_kf(name, t0, T=2.2, amp=1.5):
    k, c, vt = .16, 1.0, 650.0
    norm = 1 - math.exp(-T / k)
    fr = []
    for i in range(25):
        tau = T * (i / 24) ** 1.15
        f = amp * (1 - math.exp(-tau / k)) / norm
        g = vt * (tau - c * (1 - math.exp(-tau / c)))
        sc = min(1.0, .3 + tau / .12 * .7)
        op = 0 if i == 0 else (1 if tau < 1.0 else max(0.0, 1 - (tau - 1.0) / (T - 1.0)))
        rot = f / amp * .7 + tau / T * .9
        fr.append(f"{p(t0 + tau)}{{transform:translate(calc(var(--dx) * {f:.3f}),calc(var(--dy) * {f:.3f} + {g:.1f}px)) rotate(calc(var(--r) * {rot:.3f})) scale({sc:.2f});opacity:{op:.2f}}}")
    return f'@keyframes {name}{{0%,{fr[0].split("{")[0]}{{transform:translate(0,0) rotate(0) scale(.3);opacity:0}}' + ''.join(fr[1:]) + f'{p(t0 + T + .01)},100%{{opacity:0}}}}'

random.seed(5)
cols = ['#7FB7FF', '#9C8CF5', '#5FC8E8', '#FFB38A', '#B9A8FF', '#8FD3F0', '#FF9AC1', '#6E9BFF']
conf = []
for i in range(16):
    a = -math.pi / 2 + (i / 16) * 2 * math.pi + random.uniform(-.2, .2)
    r = random.uniform(110, 165)
    dx, dy = math.cos(a) * r, math.sin(a) * r * .8
    c = cols[i % len(cols)]
    kind = i % 4
    sh = [f'width: 10px; height: 10px; border-radius: 3px; background: {c}',
          f'width: 12px; height: 12px; border-radius: 50%; border: 2.5px solid {c}; box-sizing: border-box',
          f'width: 14px; height: 4px; border-radius: 2px; background: {c}',
          f'width: 8px; height: 8px; border-radius: 50%; background: {c}'][kind]
    conf.append(f'<span class="t-c" aria-hidden="true" style="position: absolute; left: 196px; top: 0; {sh}; --dx: {dx:.0f}px; --dy: {dy:.0f}px; --r: {random.randint(-200, 200)}deg"></span>')

END = D - .45   # everything fades before the loop restarts
css = f'''body{{margin:0}}
@keyframes drift{{0%,100%{{transform:translate(-1%,-.5%)}}50%{{transform:translate(1%,.6%)}}}}
.ambient{{animation:drift 28s ease-in-out infinite}}
@property --m{{syntax:'<integer>';inherits:false;initial-value:0}}
@keyframes tScene{{0%,{p(END)}{{opacity:1}}100%{{opacity:0}}}}
.t-scene{{animation:tScene {D}s ease infinite}}
@keyframes tBumpL{{0%{{transform:translateX(-230px);opacity:0;animation-timing-function:cubic-bezier(.45,.05,.85,.5)}}{p(.07)}{{opacity:1}}{p(LAND)}{{transform:translateX(6px) scaleX(1);animation-timing-function:linear}}{p(LAND + .06)}{{transform:translateX(9px) scaleX(.93);animation-timing-function:cubic-bezier(.2,.7,.35,1)}}{p(LAND + .5)}{{transform:translateX(-3px) scaleX(1);animation-timing-function:ease-in-out}}{p(LAND + .85)},100%{{transform:translateX(0)}}}}
@keyframes tBumpR{{0%{{transform:translateX(230px);opacity:0;animation-timing-function:cubic-bezier(.45,.05,.85,.5)}}{p(.07)}{{opacity:1}}{p(LAND)}{{transform:translateX(-6px) scaleX(1);animation-timing-function:linear}}{p(LAND + .06)}{{transform:translateX(-9px) scaleX(.93);animation-timing-function:cubic-bezier(.2,.7,.35,1)}}{p(LAND + .5)}{{transform:translateX(3px) scaleX(1);animation-timing-function:ease-in-out}}{p(LAND + .85)},100%{{transform:translateX(0)}}}}
.t-bl{{transform-origin:100% 50%;animation:tBumpL {D}s linear infinite}}
.t-br{{transform-origin:0 50%;animation:tBumpR {D}s linear infinite}}
@keyframes tFlash{{0%,{p(LAND)}{{transform:scale(.3);opacity:0}}{p(LAND + .06)}{{opacity:.9}}{p(LAND + .6)},100%{{transform:scale(2.4);opacity:0}}}}
.t-flash{{animation:tFlash {D}s ease-out infinite}}
@keyframes tDeg{{0%,{p(LAND + .1)}{{transform:translateY(8px) scale(.9);opacity:0}}{p(LAND + .3)}{{transform:translateY(0) scale(1.04);opacity:1}}{p(LAND + .42)},100%{{transform:translateY(0) scale(1);opacity:1}}}}
.t-deg{{animation:tDeg {D}s ease-out infinite}}
@keyframes tFill{{0%,{p(LAND + .2)}{{transform:scaleX(0)}}{p(LAND + .95)},100%{{transform:scaleX(.86)}}}}
.t-fill{{transform-origin:0 50%;animation:tFill {D}s cubic-bezier(.2,.7,.3,1) infinite}}
@keyframes tDegN{{0%,{p(LAND + .2)}{{--m:0}}{p(LAND + .95)},100%{{--m:86}}}}
.t-degn{{counter-reset:m var(--m);animation:tDegN {D}s cubic-bezier(.2,.7,.3,1) infinite}}
.t-degn::after{{content:counter(m) "%"}}
@keyframes tTitle{{0%,{p(LAND + .25)}{{transform:translateY(10px) scale(.7);opacity:0}}{p(LAND + .42)}{{transform:translateY(0) scale(1.08);opacity:1}}{p(LAND + .56)},100%{{transform:scale(1);opacity:1}}}}
.t-title{{animation:tTitle {D}s cubic-bezier(.2,.8,.3,1) infinite}}
{confetti_kf('tConf', LAND + .05)}
.t-c{{animation:tConf {D}s linear infinite}}
@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}}}
'''

def av(img, extra=''):
    return (f'<div style="width: {SIZE}px; height: {SIZE}px; border-radius: 50%; overflow: hidden; box-shadow: 0 0 0 3px #FFFFFF, 0 12px 26px rgba(80,110,170,0.22); background: #DCE6F4{extra}">'
            f'<img src="./img/{img}" alt="" style="width: 100%; height: 100%; object-fit: cover; display: block"></div>')

L = 201 - 6 - SIZE  # left avatar x
R = 201 + 6         # right avatar x
AT = 240            # avatars top
body = f'''<div style="position: relative; width: 402px; height: 874px; overflow: hidden; font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif; color: #2E3550; background: linear-gradient(180deg, #FCF1E8 0%, #F4F1F3 42%, #EAEFF6 74%, #E3ECF6 100%)">
  <div aria-hidden="true" class="ambient" style="position: absolute; left: -16px; top: -16px; width: 434px; height: 906px; background: radial-gradient(ellipse at 50% 26%, rgba(156,203,235,0.36), rgba(156,203,235,0) 42%), radial-gradient(ellipse at 88% 70%, rgba(255,214,190,0.24), rgba(255,214,190,0) 45%), radial-gradient(ellipse at 6% 86%, rgba(181,190,240,0.28), rgba(181,190,240,0) 50%)"></div>

  <div style="position: absolute; left: 0; top: 54px; width: 402px; height: 44px; display: flex; align-items: center; justify-content: center">
    <button aria-label="Close" style="position: absolute; left: 16px; top: 0; width: 44px; height: 44px; border-radius: 50%; border: 1px solid rgba(255,255,255,0.7); background: rgba(255,255,255,0.44); display: flex; align-items: center; justify-content: center; color: #41506E; cursor: pointer">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"></path></svg>
    </button>
    <div style="font-size: 17px; font-weight: 700; letter-spacing: -0.2px; color: #41506E">Text Match</div>
  </div>
  <div style="position: absolute; left: 24px; top: 116px; width: 354px; box-sizing: border-box; padding: 10px 14px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.85); background: rgba(255,255,255,0.5); text-align: center; font-size: 13px; line-height: 1.4; color: #6F7A96">Match count refreshes at <b style="font-weight: 700; color: #41506E">8:00</b> every day</div>

  <div class="t-scene">
    <div style="position: absolute; left: 0; top: {AT + SIZE // 2}px; width: 402px; height: 0">
      <span class="t-flash" aria-hidden="true" style="position: absolute; left: 141px; top: -60px; width: 120px; height: 120px; border-radius: 50%; filter: blur(3px); background: radial-gradient(circle, rgba(255,255,255,0.95) 0%, rgba(170,205,255,0.6) 38%, rgba(170,205,255,0) 70%)"></span>
      {''.join(conf)}
    </div>
    <div class="t-bl" style="position: absolute; left: {L}px; top: {AT}px">{av(ME)}</div>
    <div class="t-br" style="position: absolute; left: {R}px; top: {AT}px">{av(FINAL)}</div>


    <div class="t-deg" style="position: absolute; left: 0; top: {AT + SIZE + 22}px; width: 402px; display: flex; flex-direction: column; align-items: center">
      <div style="position: relative; width: 112px; height: 26px; border-radius: 13px; overflow: hidden; background: rgba(255,255,255,0.6); border: 1px solid rgba(255,255,255,0.9); box-shadow: 0 6px 14px rgba(90,120,190,0.14)">
        <span class="t-fill" aria-hidden="true" style="position: absolute; inset: 0; background: linear-gradient(90deg, #FF57A8, #F55E67)"></span>
        <span class="t-degn" style="position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 800; color: #FFFFFF; text-shadow: 0 1px 2px rgba(180,40,80,0.35); font-variant-numeric: tabular-nums"></span>
      </div>
      <div style="margin-top: 6px; font-size: 12px; font-weight: 500; color: #6F7A96">Match degree</div>
    </div>
    <div class="t-title" style="position: absolute; left: 0; top: {AT + SIZE + 78}px; width: 402px; text-align: center; font-size: 34px; font-weight: 800; letter-spacing: -0.8px; background: linear-gradient(100deg, #5FA8FF 0%, #7C8CF5 50%, #B07CF0 100%); -webkit-background-clip: text; background-clip: text; color: transparent">Chat now!</div>

  </div>

</div>'''

html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Text Match · Matched</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300..800&amp;display=swap" rel="stylesheet">
<style>
{css}</style>
</helmet>
{body}
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":402,"height":874}}}}'>
class Component extends DCLogic {{
  renderVals() {{ return {{}}; }}
}}
</script>
</body>
</html>
'''
open('project/TextMatchSuccess.dc.html', 'w').write(html)
print('ok')
