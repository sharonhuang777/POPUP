HEAD = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300..800&amp;display=swap" rel="stylesheet">
<style>
body{{margin:0}}
@keyframes drift{{0%,100%{{transform:translate(-1%,-.5%)}}50%{{transform:translate(1%,.6%)}}}}
.ambient{{animation:drift 28s ease-in-out infinite}}
{css}
@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}}}
</style>
</helmet>
<div style="position: relative; width: 402px; height: 874px; overflow: hidden; font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif; color: #342b43; background: linear-gradient(180deg, #FCF1E8 0%, #FAF0EE 40%, #F3ECF3 72%, #ECE6F5 100%)">

  <div aria-hidden="true" class="ambient" style="position: absolute; left: -16px; top: -16px; width: 434px; height: 906px; background: {glow}"></div>

  <div style="position: absolute; left: 0; top: 54px; width: 402px; height: 44px; display: flex; align-items: center; justify-content: center">
    <button aria-label="Close" style="position: absolute; left: 16px; top: 0; width: 44px; height: 44px; border-radius: 50%; border: 1px solid rgba(255,255,255,0.7); background: rgba(255,255,255,0.44); display: flex; align-items: center; justify-content: center; color: #53416e; cursor: pointer">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"></path></svg>
    </button>
    <div style="font-size: 17px; font-weight: 700; letter-spacing: -0.2px; color: #53416e">Voice Match</div>
    <button aria-label="Minimize" style="position: absolute; right: 16px; top: 0; width: 44px; height: 44px; border-radius: 50%; border: 1px solid rgba(255,255,255,0.7); background: rgba(255,255,255,0.44); display: flex; align-items: center; justify-content: center; color: #53416e; cursor: pointer">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 14h6v6M20 10h-6V4M14 10l7-7M3 21l7-7"></path></svg>
    </button>
  </div>
{body}
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":402,"height":874}}}}'>
class Component extends DCLogic {{
  renderVals() {{ return {{}}; }}
}}
</script>
</body>
</html>
'''
PHONE = '<path d="M7.6737 0.539717C8.26329 0.628959 8.57534 0.774166 8.87628 1.08871C9.13241 1.35649 9.38833 1.75413 9.73637 2.38744L10.1234 3.11422C11.8053 6.15337 11.704 7.42782 11.5562 8.04087C11.2891 9.11441 10.6463 9.49976 9.91836 9.91528C9.72461 10.0206 9.52945 10.1459 9.38051 10.2393L9.30329 10.2997C8.8091 10.7666 8.12467 11.4447 8.17984 12.7182C8.23196 13.9197 8.9407 15.5627 10.7994 18.0202L10.8103 18.0345C14.0191 21.9713 16.0558 22.7948 17.1133 22.863C17.5272 22.8931 17.8512 22.8137 18.1005 22.6918C18.3194 22.5847 18.4662 22.4484 18.5265 22.393L18.5945 22.3352C19.4131 21.487 19.9035 21.0161 20.3387 20.7434C20.7365 20.4941 21.1007 20.4044 21.7038 20.3949C22.2572 20.383 22.637 20.4737 23.176 20.7953C23.7555 21.1412 24.4872 21.7347 25.7344 22.7519C26.8476 23.6618 27.5946 24.3604 28.0152 24.995C28.4124 25.5943 28.5034 26.1113 28.3232 26.7153L28.3102 26.7677C28.1727 27.5104 27.7268 28.3953 27.096 29.2083C26.4669 30.019 25.6913 30.7084 24.9478 31.0892C23.9324 31.5807 22.5489 31.7424 20.9028 31.5184C19.453 31.3211 17.8467 30.8305 16.181 30.0697C12.1857 28.242 8.41987 25.0358 5.59355 21.0343C1.33886 14.9972 -0.246029 9.43057 0.82331 4.89806C1.10758 3.80581 1.63496 2.51055 3.45084 1.63858L3.48897 1.61913C4.98279 0.737721 6.56197 0.370778 7.6737 0.539717Z"'
BOLT = '<path d="M16.4951 1.14258C18.3709 -0.528969 21.2657 1.34132 20.499 3.76758L17.7432 12.4951L17.6221 12.877L17.9688 13.0781L25.2588 17.3125C26.7252 18.1624 26.9326 20.2127 25.6631 21.3438L10.5049 34.8574C8.62904 36.5286 5.73516 34.6586 6.50195 32.2324L9.25586 23.5049L9.37598 23.123L9.03027 22.9219L1.74023 18.6875C0.274689 17.8376 0.067064 15.7864 1.33496 14.6553L16.4951 1.14258Z"'
GLASS_ORB = "border-radius: 50%; box-sizing: border-box; border: 1.5px solid transparent; background: radial-gradient(circle at 50% 28%, rgba(255,255,255,0.95) 0%, rgba(246,238,255,0.7) 55%, rgba(226,214,252,0.55) 100%) padding-box, linear-gradient(150deg, #FFFFFF 0%, rgba(255,255,255,0.4) 45%, rgba(130,110,190,0.45) 100%) border-box; box-shadow: inset 0 3px 4px rgba(255,255,255,0.95), inset 0 -6px 12px rgba(110,90,170,0.18), 0 18px 40px rgba(130,100,210,0.28)"
def avatar(img, tint, size=112, pos=''):
    return f'''<div class="{{cls}}" style="position: absolute; {pos} width: {size}px; height: {size}px; border-radius: 50%; overflow: hidden; box-shadow: 0 0 0 3px #FFFFFF, 0 14px 30px rgba(110,80,170,0.28)">
      <img src="./img/{img}" alt="" style="width: 100%; height: 100%; object-fit: cover; object-position: center 20%; filter: blur(11px) saturate(1.15); transform: scale(1.3)">
      <div style="position: absolute; inset: 0; background: {tint}"></div>
      <div style="position: absolute; inset: 0; background: radial-gradient(70% 55% at 30% 22%, rgba(255,255,255,0.6), rgba(255,255,255,0) 60%), linear-gradient(125deg, rgba(255,255,255,0) 38%, rgba(255,255,255,0.25) 46%, rgba(255,255,255,0) 54%)"></div>
      <div style="position: absolute; inset: 0; border-radius: 50%; box-shadow: inset 0 0 22px rgba(255,255,255,0.5), inset 0 -10px 18px rgba(90,60,160,0.22)"></div>
    </div>'''
HIM_TINT = 'linear-gradient(160deg, rgba(196,170,255,0.38), rgba(120,90,200,0.32))'
ME_TINT = 'linear-gradient(160deg, rgba(255,190,200,0.36), rgba(242,110,120,0.30))'

# ---------------- 1. network check ----------------
css1 = '''
@keyframes nRipple{0%{transform:scale(.78);opacity:.7}100%{transform:scale(1.6);opacity:0}}
@keyframes nBreath{0%,100%{transform:scale(1)}50%{transform:scale(1.05)}}
@keyframes nSpin{to{transform:rotate(360deg)}}
@keyframes nArc{0%,100%{opacity:.25}40%,60%{opacity:1}}
@keyframes nSheen{0%{transform:translateX(-120%) rotate(20deg)}55%,100%{transform:translateX(220%) rotate(20deg)}}
.n-ring{animation:nRipple 2.4s cubic-bezier(.2,.6,.3,1) infinite}
.n-ring.r2{animation-delay:.8s}.n-ring.r3{animation-delay:1.6s}
.n-orb{animation:nBreath 2.4s ease-in-out infinite}
.n-spin{animation:nSpin .9s linear infinite}
.n-a1{animation:nArc 1.5s ease-in-out infinite}.n-a2{animation:nArc 1.5s ease-in-out .2s infinite}.n-a3{animation:nArc 1.5s ease-in-out .4s infinite}
.n-sheen{animation:nSheen 3s ease-in-out infinite}
'''
rings = ''.join(f'<span class="n-ring{c}" aria-hidden="true" style="position: absolute; inset: 0; border-radius: 50%; border: 1.5px solid {col}; background: radial-gradient(circle, rgba(255,255,255,0) 58%, {bg} 100%)"></span>' for c,col,bg in [('', 'rgba(170,140,240,0.55)','rgba(190,165,245,0.18)'),(' r2','rgba(255,150,120,0.5)','rgba(255,180,150,0.16)'),(' r3','rgba(170,140,240,0.45)','rgba(190,165,245,0.14)')])
body1 = f'''
  <div style="position: absolute; left: 24px; top: 116px; width: 354px; box-sizing: border-box; padding: 10px 14px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.85); background: rgba(255,255,255,0.5); text-align: center; font-size: 13px; line-height: 1.4; color: #7A6E92">Match count refreshes at <b style="font-weight: 700; color: #53416E">8:00</b> every day</div>

  <div style="position: absolute; left: 81px; top: 214px; width: 240px; height: 240px">
    {rings}
    <div class="n-orb" style="position: absolute; left: 50px; top: 50px; width: 140px; height: 140px; {GLASS_ORB}; display: flex; align-items: center; justify-content: center; overflow: hidden">
      <span class="n-sheen" aria-hidden="true" style="position: absolute; top: -20px; left: 0; width: 40px; height: 180px; background: linear-gradient(90deg, rgba(255,255,255,0), rgba(255,255,255,0.7), rgba(255,255,255,0))"></span>
      <svg width="50" height="57" viewBox="0 0 29 33" fill="none" aria-hidden="true" style="position: relative"><defs><linearGradient id="nPh" x1="12.8" y1="-0.9" x2="14.3" y2="38" gradientUnits="userSpaceOnUse"><stop stop-color="#A68DF5"></stop><stop offset="1" stop-color="#6247C9"></stop></linearGradient></defs>{PHONE} fill="url(#nPh)"></path></svg>
    </div>
  </div>

  <div style="position: absolute; left: 141px; top: 484px; width: 120px; height: 48px; box-sizing: border-box; border-radius: 999px; border: 1.5px solid rgba(255,255,255,0.9); background: linear-gradient(150deg, rgba(255,255,255,0.75), rgba(255,255,255,0.4)); box-shadow: 0 10px 24px rgba(120,90,170,0.14), inset 0 1px 1px #FFFFFF; display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: 750; letter-spacing: 0.5px; font-variant-numeric: tabular-nums; color: #2E2A40">00:02</div>

  <div style="position: absolute; left: 40px; top: 562px; width: 322px; height: 52px; box-sizing: border-box; padding: 0 16px; border-radius: 18px; border: 1px solid rgba(255,255,255,0.85); background: rgba(255,255,255,0.55); display: flex; align-items: center; gap: 12px">
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#7356D4" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path class="n-a3" d="M2.5 8.8a14 14 0 0 1 19 0"></path><path class="n-a2" d="M5.6 12.3a9.5 9.5 0 0 1 12.8 0"></path><path class="n-a1" d="M8.8 15.7a5 5 0 0 1 6.4 0"></path><circle cx="12" cy="19.2" r="1.3" fill="#7356D4" stroke="none"></circle></svg>
    <div style="flex: 1; font-size: 15px; font-weight: 600; color: #3B3150">Checking your network…</div>
    <svg class="n-spin" width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="12" cy="12" r="9" stroke="rgba(115,86,212,0.18)" stroke-width="2.6"></circle><path d="M12 3a9 9 0 0 1 9 9" stroke="#8F6FF0" stroke-width="2.6" stroke-linecap="round"></path></svg>
  </div>
  <div style="position: absolute; left: 24px; top: 628px; width: 354px; text-align: center; font-size: 13px; color: #8E86A0">Keep the app open, we'll connect you in a moment.</div>
'''
glow1 = 'radial-gradient(ellipse at 50% 34%, rgba(190,165,245,0.34), rgba(190,165,245,0) 44%), radial-gradient(ellipse at 88% 80%, rgba(255,205,185,0.28), rgba(255,205,185,0) 45%), radial-gradient(ellipse at 6% 86%, rgba(190,170,235,0.26), rgba(190,170,235,0) 50%)'
open('project/VoiceNetCheck.dc.html','w').write(HEAD.format(title='Voice Match · Network check', css=css1, glow=glow1, body=body1))

# ---------------- 2. match success (avatars collide) ----------------
def confetti_kf(D, t0=.5, T=2.0):
    # Burst outward with air drag, gravity pulls down from the first frame (no hang at the top).
    import math
    k, c, vt = .16, 1.0, 650.0
    norm = 1 - math.exp(-T / k)
    fr = []
    for i in range(25):
        tau = T * (i / 24) ** 1.15
        f = 1.5 * (1 - math.exp(-tau / k)) / norm
        g = vt * (tau - c * (1 - math.exp(-tau / c)))
        sc = min(1.0, .3 + tau / .12 * .7)
        op = 0 if i == 0 else (1 if tau < 1.1 else max(0.0, 1 - (tau - 1.1) / (T - 1.1)))
        rot = f / 1.5 * .7 + tau / T * .9
        fr.append(f"{(t0 + tau) / D * 100:.2f}%{{transform:translate(calc(var(--dx) * {f:.3f}),calc(var(--dy) * {f:.3f} + {g:.1f}px)) rotate(calc(var(--r) * {rot:.3f})) scale({sc:.2f});opacity:{op:.2f}}}")
    return '@keyframes mConf{' + f"0%,{fr[0].split('{')[0]}" + '{transform:translate(0,0) rotate(0) scale(.3);opacity:0}' + ''.join(fr[1:]) + f"{(t0+T)/D*100+0.01:.2f}%,100%{{opacity:0}}" + '}'

D = 3.0  # plays once; title lands on impact, everything is in by ~0.9s, the app moves to the call 1s later (demo)
def pct(t): return f'{t/D*100:.2f}%'
CONF = confetti_kf(D, T=2.4)
css2 = f'''
@keyframes mL{{0%{{transform:translateX(-260px) scale(.9);opacity:0;animation-timing-function:cubic-bezier(.45,.05,.85,.5)}}{pct(.08)}{{opacity:1}}{pct(.48)}{{transform:translateX(-56px) scale(1);animation-timing-function:linear}}{pct(.53)}{{transform:translateX(-50px) scaleX(.9) scaleY(1.06);animation-timing-function:cubic-bezier(.2,.8,.4,1)}}{pct(.72)}{{transform:translateX(-65px) scale(1.02);animation-timing-function:ease-in-out}}{pct(.92)},100%{{transform:translateX(-60px) scale(1);opacity:1}}}}
@keyframes mR{{0%{{transform:translateX(260px) scale(.9);opacity:0;animation-timing-function:cubic-bezier(.45,.05,.85,.5)}}{pct(.08)}{{opacity:1}}{pct(.48)}{{transform:translateX(56px) scale(1);animation-timing-function:linear}}{pct(.53)}{{transform:translateX(50px) scaleX(.9) scaleY(1.06);animation-timing-function:cubic-bezier(.2,.8,.4,1)}}{pct(.72)}{{transform:translateX(65px) scale(1.02);animation-timing-function:ease-in-out}}{pct(.92)},100%{{transform:translateX(60px) scale(1);opacity:1}}}}
@keyframes mFlash{{0%,{pct(.48)}{{transform:scale(.2);opacity:0}}{pct(.56)}{{opacity:1}}{pct(1.1)},100%{{transform:scale(2.6);opacity:0}}}}
@keyframes mWave{{0%,{pct(.5)}{{transform:scale(.4);opacity:0}}{pct(.56)}{{opacity:.9}}{pct(1.5)},100%{{transform:scale(3.2);opacity:0}}}}
@keyframes mTitle{{0%,{pct(.48)}{{transform:translateY(10px) scale(.7);opacity:0}}{pct(.62)}{{transform:translateY(0) scale(1.08);opacity:1}}{pct(.76)},100%{{transform:translateY(0) scale(1);opacity:1}}}}
@keyframes mSub{{0%,{pct(.6)}{{transform:translateY(8px);opacity:0}}{pct(.88)},100%{{transform:translateY(0);opacity:1}}}}
{CONF}
.m-l{{animation:mL {D}s linear both}}
.m-r{{animation:mR {D}s linear both}}
.m-flash{{animation:mFlash {D}s ease-out both}}
.m-wave{{animation:mWave {D}s cubic-bezier(.2,.6,.3,1) both}}
.m-title{{animation:mTitle {D}s cubic-bezier(.2,.8,.3,1) both}}
.m-sub{{animation:mSub {D}s ease-out both}}
.m-c{{animation:mConf {D}s linear both}}
'''
import math, random
random.seed(7)
shapes = []
cols = ['#FF8A4E','#F2545B','#8F6FF0','#FFC857','#5FD3B6','#FF9AC1','#A68DF5','#7FB7FF']
for i in range(14):
    a = -math.pi/2 + (i/14)*2*math.pi + random.uniform(-.2,.2)
    r = random.uniform(120,175)
    dx, dy = math.cos(a)*r, math.sin(a)*r*0.8
    c = cols[i % len(cols)]
    kind = i % 4
    if kind == 0: sh = f'width: 10px; height: 10px; border-radius: 3px; background: {c}'
    elif kind == 1: sh = f'width: 12px; height: 12px; border-radius: 50%; border: 2.5px solid {c}; box-sizing: border-box'
    elif kind == 2: sh = f'width: 14px; height: 4px; border-radius: 2px; background: {c}'
    else: sh = f'width: 8px; height: 8px; border-radius: 50%; background: {c}'
    shapes.append(f'<span class="m-c" aria-hidden="true" style="position: absolute; left: 196px; top: 0; {sh}; --dx: {dx:.0f}px; --dy: {dy:.0f}px; --r: {random.randint(-200,200)}deg"></span>')
body2 = f'''
  <div style="position: absolute; left: 24px; top: 116px; width: 354px; box-sizing: border-box; padding: 10px 14px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.85); background: rgba(255,255,255,0.5); text-align: center; font-size: 13px; line-height: 1.4; color: #7A6E92">Match count refreshes at <b style="font-weight: 700; color: #53416E">8:00</b> every day</div>

  <div style="position: absolute; left: 0; top: 322px; width: 402px; height: 0">
    <span class="m-wave" aria-hidden="true" style="position: absolute; left: 141px; top: -60px; width: 120px; height: 120px; border-radius: 50%; border: 2px solid rgba(242,110,120,0.45)"></span>
    <span class="m-flash" aria-hidden="true" style="position: absolute; left: 141px; top: -60px; width: 120px; height: 120px; border-radius: 50%; background: radial-gradient(circle, rgba(255,255,255,0.95) 0%, rgba(255,190,170,0.7) 35%, rgba(196,170,255,0) 70%)"></span>
    {''.join(shapes)}
  </div>

  <div style="position: absolute; left: 145px; top: 266px; width: 112px; height: 112px">
    {avatar('u2.jpg', HIM_TINT, pos='left: 0; top: 0;').replace('{cls}','m-l')}
    {avatar('avatar.png', ME_TINT, pos='left: 0; top: 0;').replace('{cls}','m-r')}
  </div>

  <div class="m-title" style="position: absolute; left: 0; top: 424px; width: 402px; text-align: center; font-size: 34px; font-weight: 800; letter-spacing: -0.8px; background: linear-gradient(100deg, #FF8A4E 0%, #F2545B 45%, #8F6FF0 100%); -webkit-background-clip: text; background-clip: text; color: transparent">Match successfully!</div>
  <div class="m-sub" style="position: absolute; left: 24px; top: 474px; width: 354px; text-align: center; font-size: 15px; line-height: 1.45; color: #6E6080">Connecting your voice call…</div>
'''
glow2 = 'radial-gradient(ellipse at 50% 34%, rgba(255,186,170,0.32), rgba(255,186,170,0) 44%), radial-gradient(ellipse at 88% 80%, rgba(255,214,190,0.30), rgba(255,214,190,0) 45%), radial-gradient(ellipse at 6% 86%, rgba(190,170,235,0.28), rgba(190,170,235,0) 50%)'
# Standard match success uses the same background as the standard voice thinking page (V2Think1): lilac, not peach.
OLD_BG2 = 'background: linear-gradient(180deg, #FCF1E8 0%, #FAF0EE 40%, #F3ECF3 72%, #ECE6F5 100%)'
STD_BG2 = 'background: linear-gradient(180deg, #FCF1E8 0%, #F7EFF2 45%, #EEE8F6 75%, #E8E2F6 100%)'
glow2 = 'radial-gradient(ellipse at 50% 26%, rgba(196,170,245,0.34), rgba(196,170,245,0) 42%), radial-gradient(ellipse at 88% 72%, rgba(255,214,190,0.26), rgba(255,214,190,0) 45%), radial-gradient(ellipse at 6% 86%, rgba(181,158,235,0.30), rgba(181,158,235,0) 50%)'
out2 = HEAD.format(title='Voice Match · Matched', css=css2, glow=glow2, body=body2)
assert out2.count(OLD_BG2) == 1
out2 = out2.replace(OLD_BG2, STD_BG2)
# Plays once and holds the final frame; tap anywhere on the board to replay.
_root = '<div style="position: relative; width: 402px; height: 874px;'
assert out2.count(_root) == 1 and out2.count('renderVals() { return {}; }') == 1
out2 = out2.replace(_root, '<div data-ms-root data-loop="4200" ref="{{ rootRef }}" onClick="{{ replay }}" style="cursor: pointer; position: relative; width: 402px; height: 874px;', 1)
# On the canvas the board loops (plays, holds the last frame a moment, plays again); tap to replay at once.
# The demo strips this script and plays the page once.
out2 = out2.replace('renderVals() { return {}; }', """componentDidMount() { this.loop(); }
  componentWillUnmount() { clearInterval(this.iv); }
  restart() {
    var r = this.root;
    if (!r || !r.getAnimations) return;
    r.getAnimations({ subtree: true }).forEach(function (a) { if (a.animationName !== 'drift') { a.currentTime = 0; a.play(); } });
  }
  loop() {
    var self = this;
    clearInterval(this.iv);
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    var ms = +((this.root && this.root.getAttribute('data-loop')) || 4200);
    this.iv = setInterval(function () { self.restart(); }, ms);
  }
  renderVals() {
    var self = this;
    if (!this._rootRef) this._rootRef = function (el) { self.root = el; if (el) self.loop(); };
    if (!this._replay) this._replay = function () { self.restart(); self.loop(); };
    return { rootRef: this._rootRef, replay: this._replay };
  }""")
open('project/VoiceMatchSuccess.dc.html','w').write(out2)

# ---------------- 3. priority match success (bolt) ----------------
D = 5.4
def pc(t): return f'{t/D*100:.2f}%'
css3 = f'''
@keyframes pOrb{{0%{{transform:scale(.3);opacity:0}}{pc(.32)}{{transform:scale(1.14);opacity:1}}{pc(.5)}{{transform:scale(.96)}}{pc(.66)},{pc(5.0)}{{transform:scale(1);opacity:1}}100%{{transform:scale(1);opacity:0}}}}
@keyframes pBolt{{0%,{pc(.3)}{{transform:scale(.4) rotate(-12deg);opacity:0}}{pc(.55)}{{transform:scale(1.18) rotate(4deg);opacity:1}}{pc(.75)},{pc(5.0)}{{transform:scale(1) rotate(0);opacity:1}}100%{{opacity:0}}}}
@keyframes pShock{{0%,{pc(.4)}{{transform:scale(.5);opacity:0}}{pc(.46)}{{opacity:1}}{pc(1.3)},100%{{transform:scale(2.8);opacity:0}}}}
@keyframes pShock2{{0%,{pc(.62)}{{transform:scale(.5);opacity:0}}{pc(.68)}{{opacity:.8}}{pc(1.6)},100%{{transform:scale(3.3);opacity:0}}}}
@keyframes pRays{{0%,{pc(.45)}{{transform:scale(.4) rotate(0);opacity:0}}{pc(.75)}{{transform:scale(1.15) rotate(20deg);opacity:1}}{pc(1.5)}{{transform:scale(1.3) rotate(40deg);opacity:0}}100%{{opacity:0}}}}
@keyframes pHalo{{0%,{pc(1.3)}{{opacity:0}}{pc(1.7)},{pc(5.0)}{{opacity:1}}100%{{opacity:0}}}}
@keyframes pSpin{{to{{transform:rotate(360deg)}}}}
@keyframes pGlow{{0%,100%{{box-shadow:0 0 0 0 rgba(255,140,90,0.0),0 18px 40px rgba(240,100,80,0.30)}}50%{{box-shadow:0 0 34px 6px rgba(255,140,90,0.45),0 18px 40px rgba(240,100,80,0.30)}}}}
@keyframes pAL{{0%,{pc(1.1)}{{transform:translateX(-90px);opacity:0}}{pc(1.55)}{{transform:translateX(6px);opacity:1}}{pc(1.75)},{pc(5.0)}{{transform:translateX(0);opacity:1}}100%{{opacity:0}}}}
@keyframes pAR{{0%,{pc(1.1)}{{transform:translateX(90px);opacity:0}}{pc(1.55)}{{transform:translateX(-6px);opacity:1}}{pc(1.75)},{pc(5.0)}{{transform:translateX(0);opacity:1}}100%{{opacity:0}}}}
@keyframes pWaveIn{{0%,{pc(1.5)}{{transform:scaleX(0);opacity:0}}{pc(1.9)},{pc(5.0)}{{transform:scaleX(1);opacity:1}}100%{{opacity:0}}}}
@keyframes pBar{{0%,100%{{transform:scaleY(.35)}}50%{{transform:scaleY(1)}}}}
@keyframes pTitle{{0%,{pc(1.7)}{{transform:translateY(14px) scale(.9);opacity:0}}{pc(2.0)}{{transform:translateY(0) scale(1.04);opacity:1}}{pc(2.15)},{pc(5.0)}{{transform:scale(1);opacity:1}}100%{{opacity:0}}}}
@keyframes pSub{{0%,{pc(1.95)}{{transform:translateY(8px);opacity:0}}{pc(2.3)},{pc(5.0)}{{transform:translateY(0);opacity:1}}100%{{opacity:0}}}}
@keyframes pSpark{{0%,{pc(.5)}{{transform:translate(0,0) scale(.2);opacity:0}}{pc(.6)}{{opacity:1}}{pc(1.4)},100%{{transform:translate(var(--dx),var(--dy)) scale(1);opacity:0}}}}
.p-orb{{animation:pOrb {D}s cubic-bezier(.34,1.4,.64,1) infinite}}
.p-orb-glow{{animation:pGlow 1.8s ease-in-out infinite}}
.p-bolt{{animation:pBolt {D}s cubic-bezier(.34,1.5,.64,1) infinite}}
.p-shock{{animation:pShock {D}s cubic-bezier(.15,.7,.3,1) infinite}}
.p-shock2{{animation:pShock2 {D}s cubic-bezier(.15,.7,.3,1) infinite}}
.p-rays{{animation:pRays {D}s ease-out infinite}}
.p-halo{{animation:pHalo {D}s ease infinite}}
.p-halo .p-spin{{animation:pSpin 6s linear infinite}}
.p-al{{animation:pAL {D}s cubic-bezier(.3,.8,.3,1) infinite}}
.p-ar{{animation:pAR {D}s cubic-bezier(.3,.8,.3,1) infinite}}
.p-wave{{transform-origin:var(--o) 50%;animation:pWaveIn {D}s cubic-bezier(.3,.8,.3,1) infinite}}
.p-bar{{transform-origin:center;animation:pBar .9s ease-in-out infinite}}
.p-title{{animation:pTitle {D}s cubic-bezier(.34,1.3,.64,1) infinite}}
.p-sub{{animation:pSub {D}s ease-out infinite}}
.p-sp{{animation:pSpark {D}s cubic-bezier(.15,.7,.3,1) infinite}}
'''
def wave(side):
    hs = [6,12,20,10,26,14,8,18,10,6] if side=='l' else [6,10,18,8,14,26,10,20,12,6]
    bars = ''.join(f'<span class="p-bar" style="width: 3px; height: {h}px; border-radius: 2px; background: linear-gradient(180deg, #FFB070, #F2545B); animation-delay: -{(i*0.11):.2f}s"></span>' for i,h in enumerate(hs))
    left = 128 if side=='l' else 236
    origin = '100%' if side=='l' else '0%'
    return f'<div class="p-wave" aria-hidden="true" style="--o: {origin}; position: absolute; left: {left}px; top: 307px; width: 38px; height: 30px; display: flex; align-items: center; justify-content: space-between">{bars}</div>'
random.seed(3)
sparks = ''.join(f'<span class="p-sp" aria-hidden="true" style="position: absolute; left: 198px; top: 318px; width: {s}px; height: {s}px; border-radius: 50%; background: {c}; box-shadow: 0 0 8px {c}; --dx: {math.cos(a)*r:.0f}px; --dy: {math.sin(a)*r:.0f}px"></span>' for a,r,s,c in [((i/12)*2*math.pi+random.uniform(-.15,.15), random.uniform(90,140), random.choice([5,6,7]), random.choice(['#FFC857','#FF8A4E','#FF9AC1','#FFFFFF'])) for i in range(12)])
body3 = f'''
  <div style="position: absolute; left: 24px; top: 116px; width: 354px; box-sizing: border-box; padding: 10px 14px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.85); background: rgba(255,255,255,0.5); text-align: center; font-size: 13px; line-height: 1.4; color: #7A6E92">Match count refreshes at <b style="font-weight: 700; color: #53416E">8:00</b> every day</div>

  <span class="p-rays" aria-hidden="true" style="position: absolute; left: 81px; top: 202px; width: 240px; height: 240px; border-radius: 50%; background: repeating-conic-gradient(from 0deg, rgba(255,170,110,0.55) 0deg 4deg, rgba(255,170,110,0) 4deg 18deg); -webkit-mask-image: radial-gradient(circle, rgba(0,0,0,0) 26%, #000 34%, rgba(0,0,0,0) 70%); mask-image: radial-gradient(circle, rgba(0,0,0,0) 26%, #000 34%, rgba(0,0,0,0) 70%)"></span>
  <span class="p-shock" aria-hidden="true" style="position: absolute; left: 141px; top: 262px; width: 120px; height: 120px; box-sizing: border-box; border-radius: 50%; border: 3px solid rgba(255,140,90,0.75)"></span>
  <span class="p-shock2" aria-hidden="true" style="position: absolute; left: 141px; top: 262px; width: 120px; height: 120px; box-sizing: border-box; border-radius: 50%; border: 2px solid rgba(190,150,245,0.6)"></span>
  {sparks}
  <div class="p-halo" aria-hidden="true" style="position: absolute; left: 121px; top: 242px; width: 160px; height: 160px">
    <span class="p-spin" style="position: absolute; inset: 0; border-radius: 50%; background: conic-gradient(from 0deg, rgba(255,164,92,0), rgba(255,164,92,0.9), rgba(242,84,91,0.9), rgba(194,92,240,0.6), rgba(255,164,92,0)); -webkit-mask: radial-gradient(farthest-side, transparent calc(100% - 3px), #000 calc(100% - 2.5px)); mask: radial-gradient(farthest-side, transparent calc(100% - 3px), #000 calc(100% - 2.5px))"></span>
    <span style="position: absolute; inset: 10px; border-radius: 50%; border: 1px solid rgba(255,170,130,0.5)"></span>
  </div>
  <div class="p-orb" style="position: absolute; left: 141px; top: 262px; width: 120px; height: 120px">
    <div class="p-orb-glow" style="width: 120px; height: 120px; box-sizing: border-box; border-radius: 50%; border: 1.5px solid transparent; background: radial-gradient(circle at 50% 28%, #FFFFFF 0%, rgba(255,246,240,0.96) 60%, rgba(255,226,212,0.92) 100%) padding-box, linear-gradient(150deg, #FFFFFF 0%, rgba(255,200,170,0.8) 50%, rgba(242,84,91,0.5) 100%) border-box; display: flex; align-items: center; justify-content: center">
      <svg class="p-bolt" width="44" height="58" viewBox="0 0 27 36" fill="none" aria-hidden="true"><defs><linearGradient id="pBl" x1="13.5" y1="0" x2="13.5" y2="36" gradientUnits="userSpaceOnUse"><stop stop-color="#FFB070"></stop><stop offset="1" stop-color="#EE5A46"></stop></linearGradient></defs>{BOLT} fill="url(#pBl)"></path></svg>
    </div>
  </div>
  {wave('l')}{wave('r')}
  <div style="position: absolute; left: 26px; top: 276px; width: 92px; height: 92px">
    {avatar('u2.jpg', HIM_TINT, size=92, pos='left: 0; top: 0;').replace('{cls}','p-al')}
  </div>
  <div style="position: absolute; left: 284px; top: 276px; width: 92px; height: 92px">
    {avatar('avatar.png', ME_TINT, size=92, pos='left: 0; top: 0;').replace('{cls}','p-ar')}
  </div>

  <div class="p-title" style="position: absolute; left: 0; top: 434px; width: 402px; text-align: center; font-size: 30px; font-weight: 800; letter-spacing: -0.6px; background: linear-gradient(100deg, #FF9A4C 0%, #F2545B 50%, #C25CF0 100%); -webkit-background-clip: text; background-clip: text; color: transparent">Priority Match Success</div>
  <div class="p-sub" style="position: absolute; left: 24px; top: 480px; width: 354px; text-align: center; font-size: 15px; line-height: 1.45; color: #6E6080">You just skipped <b style="font-weight: 750; color: #F2545B">582</b> people!</div>
'''
glow3 = 'radial-gradient(ellipse at 50% 36%, rgba(255,170,130,0.38), rgba(255,170,130,0) 44%), radial-gradient(ellipse at 88% 80%, rgba(255,214,190,0.30), rgba(255,214,190,0) 45%), radial-gradient(ellipse at 6% 86%, rgba(190,170,235,0.26), rgba(190,170,235,0) 50%)'
# Old bolt version, superseded by gen_priority_variants.py (direction B) on 2026-10-22; kept for reference only.
# open('project/VoicePrioritySuccess.dc.html','w').write(HEAD.format(title='Voice Match · Priority matched', css=css3, glow=glow3, body=body3))
print('ok')
