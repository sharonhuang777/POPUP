# Priority (boost card) match success, North America: no bolt. Two directions built from the standard
# match-success board so the pair reads as one family:
#   A  VoicePrioritySuccessA  halo-trail collision: avatars rush in faster with coral light trails, impact bursts rings
#   B  VoicePrioritySuccessB  halo spin-collapse: a coral halo spins up and collapses, the avatars pop out of it and collide
# Both play once and hold the last frame; tap the board to replay. Run from the canvas root (writes project/*.dc.html).
import math, re, sys, os

SRC = sys.argv[1] if len(sys.argv) > 1 else 'project/VoiceMatchSuccess.dc.html'
tpl = open(SRC).read()

head = tpl[:tpl.index('@keyframes mL')]
tail_css = tpl[tpl.index('@media (prefers-reduced-motion'):tpl.index('</helmet>')]
body_open = tpl[tpl.index('</helmet>'):tpl.index('  <div style="position: absolute; left: 0; top: 322px')]
script = tpl[tpl.index('</div>\n</x-dc>'):]
av_l = re.search(r'    <div class="m-l".*?\n    </div>\n', tpl, re.S).group(0)
av_r = re.search(r'    <div class="m-r".*?\n    </div>\n', tpl, re.S).group(0)
head = head.replace('<title>Voice Match · Matched</title>', '<title>Voice Match · Priority matched</title>')

def confetti_kf(name, D, t0, T=2.4, amp=1.5):
    # Burst outward with air drag; gravity pulls from the first frame, so nothing hangs at the top.
    k, c, vt = .16, 1.0, 650.0
    norm = 1 - math.exp(-T / k)
    fr = []
    for i in range(25):
        tau = T * (i / 24) ** 1.15
        f = amp * (1 - math.exp(-tau / k)) / norm
        g = vt * (tau - c * (1 - math.exp(-tau / c)))
        sc = min(1.0, .3 + tau / .12 * .7)
        op = 0 if i == 0 else (1 if tau < 1.1 else max(0.0, 1 - (tau - 1.1) / (T - 1.1)))
        rot = f / amp * .7 + tau / T * .9
        fr.append(f"{(t0 + tau) / D * 100:.2f}%{{transform:translate(calc(var(--dx) * {f:.3f}),calc(var(--dy) * {f:.3f} + {g:.1f}px)) rotate(calc(var(--r) * {rot:.3f})) scale({sc:.2f});opacity:{op:.2f}}}")
    first = fr[0].split('{')[0]
    return (f'@keyframes {name}{{0%,{first}{{transform:translate(0,0) rotate(0) scale(.3);opacity:0}}' + ''.join(fr[1:]) +
            f"{min(99.99, (t0 + T) / D * 100 + .01):.2f}%,100%{{opacity:0}}}}")

def sparks():
    import random
    random.seed(11)
    cols = ['#FF8A4E', '#F2545B', '#FFC857', '#FFB070', '#C25CF0', '#FF9AC1', '#FFFFFF', '#FF7A4E']
    out = []
    for i in range(16):
        a = -math.pi / 2 + (i / 16) * 2 * math.pi + random.uniform(-.2, .2)
        r = random.uniform(120, 175)
        dx, dy = math.cos(a) * r, math.sin(a) * r * .8
        c = cols[i % len(cols)]
        kind = i % 4
        if kind == 0: sh = f'width: 10px; height: 10px; border-radius: 3px; background: {c}'
        elif kind == 1: sh = f'width: 12px; height: 12px; border-radius: 50%; border: 2.5px solid {c}; box-sizing: border-box'
        elif kind == 2: sh = f'width: 14px; height: 4px; border-radius: 2px; background: {c}'
        else: sh = f'width: 8px; height: 8px; border-radius: 50%; background: {c}; box-shadow: 0 0 8px {c}'
        out.append(f'<span class="q-c" aria-hidden="true" style="position: absolute; left: 196px; top: 0; {sh}; --dx: {dx:.0f}px; --dy: {dy:.0f}px; --r: {random.randint(-200, 200)}deg"></span>')
    return ''.join(out)

HALO = ('<span class="q-spin" style="position: absolute; inset: 0; border-radius: 50%; background: conic-gradient(from 0deg, rgba(255,164,92,0), rgba(255,164,92,0.95), rgba(242,84,91,0.95), rgba(194,92,240,0.7), rgba(255,164,92,0)); '
        '-webkit-mask: radial-gradient(farthest-side, transparent calc(100% - {w}px), #000 calc(100% - {w2}px)); mask: radial-gradient(farthest-side, transparent calc(100% - {w}px), #000 calc(100% - {w2}px))"></span>')

def ring(cls, size, border):
    o = (402 - size) / 2
    return f'<span class="{cls}" aria-hidden="true" style="position: absolute; left: {o:.0f}px; top: {-size / 2:.0f}px; width: {size}px; height: {size}px; box-sizing: border-box; border-radius: 50%; border: {border}"></span>'

TITLE = ('  <div class="q-title" style="position: absolute; left: 0; top: 424px; width: 402px; text-align: center; font-size: 30px; font-weight: 800; letter-spacing: -0.6px; '
         'background: linear-gradient(100deg, #FF9A4C 0%, #F2545B 50%, #C25CF0 100%); -webkit-background-clip: text; background-clip: text; color: transparent">Priority Match Success</div>\n'
         '  <div class="q-sub" style="position: absolute; left: 24px; top: 472px; width: 354px; text-align: center; font-size: 15px; line-height: 1.45; color: #6E6080">'
         'You just skipped <b class="q-cnt" style="font-weight: 750; color: #F2545B; font-variant-numeric: tabular-nums"></b> people!</div>\n')

COMMON_CSS = '''@property --n{syntax:'<integer>';inherits:false;initial-value:0}
.q-cnt{counter-reset:n var(--n)}
.q-cnt::after{content:counter(n)}
.q-spin{animation:qSpin 2.4s linear infinite}
@keyframes qSpin{to{transform:rotate(360deg)}}
'''

def pct(t, D): return f'{t / D * 100:.2f}%'

def tail(D, t_hit, t_sub, t_cnt_end):
    p = lambda t: pct(t, D)
    return f'''@keyframes qTitle{{0%,{p(t_hit)}{{transform:translateY(10px) scale(.7);opacity:0}}{p(t_hit + .14)}{{transform:translateY(0) scale(1.08);opacity:1}}{p(t_hit + .28)},100%{{transform:translateY(0) scale(1);opacity:1}}}}
@keyframes qSub{{0%,{p(t_sub)}{{transform:translateY(8px);opacity:0}}{p(t_sub + .26)},100%{{transform:translateY(0);opacity:1}}}}
@keyframes qCnt{{0%,{p(t_sub)}{{--n:0;animation-timing-function:cubic-bezier(.2,.7,.3,1)}}{p(t_cnt_end)},100%{{--n:582}}}}
@keyframes qCntPop{{0%,{p(t_cnt_end)}{{transform:scale(1)}}{p(t_cnt_end + .1)}{{transform:scale(1.25)}}{p(t_cnt_end + .24)},100%{{transform:scale(1)}}}}
.q-title{{animation:qTitle {D}s cubic-bezier(.2,.8,.3,1) both}}
.q-sub{{animation:qSub {D}s ease-out both}}
.q-cnt{{display:inline-block;animation:qCnt {D}s linear both,qCntPop {D}s ease-out both}}
.q-c{{animation:qConf {D}s linear both}}
{confetti_kf('qConf', D, t_hit)}
'''

def avatars(lcls, rcls, extra=''):
    return ('  <div style="position: absolute; left: 145px; top: 266px; width: 112px; height: 112px">\n' + extra +
            av_l.replace('class="m-l"', f'class="{lcls}"') + av_r.replace('class="m-r"', f'class="{rcls}"') + '  </div>\n')

def write(name, css, body):
    s = head + COMMON_CSS + css + '\n' + tail_css + body_open + body + script
    assert '{{ replay }}' in s and s.count('<x-dc>') == 1
    open('project/' + name, 'w').write(s)

# ---------------- A: halo-trail collision ----------------
D = 3.0; H = .45   # impact
p = lambda t: pct(t, D)
cssA = f'''@keyframes aL{{0%{{transform:translateX(-235px) scale(.92);opacity:0;animation-timing-function:cubic-bezier(.4,0,.9,.55)}}{p(.06)}{{opacity:1}}{p(H)}{{transform:translateX(-56px) scale(1);animation-timing-function:linear}}{p(H + .05)}{{transform:translateX(-48px) scaleX(.88) scaleY(1.08);animation-timing-function:cubic-bezier(.2,.8,.4,1)}}{p(H + .26)}{{transform:translateX(-67px) scale(1.03);animation-timing-function:ease-in-out}}{p(H + .48)},100%{{transform:translateX(-60px) scale(1);opacity:1}}}}
@keyframes aR{{0%{{transform:translateX(235px) scale(.92);opacity:0;animation-timing-function:cubic-bezier(.4,0,.9,.55)}}{p(.06)}{{opacity:1}}{p(H)}{{transform:translateX(56px) scale(1);animation-timing-function:linear}}{p(H + .05)}{{transform:translateX(48px) scaleX(.88) scaleY(1.08);animation-timing-function:cubic-bezier(.2,.8,.4,1)}}{p(H + .26)}{{transform:translateX(67px) scale(1.03);animation-timing-function:ease-in-out}}{p(H + .48)},100%{{transform:translateX(60px) scale(1);opacity:1}}}}
@keyframes aTrL{{0%{{transform:translateX(-235px) scaleX(.5);opacity:0;animation-timing-function:cubic-bezier(.4,0,.9,.55)}}{p(.08)}{{opacity:.9}}{p(H)}{{transform:translateX(-56px) scaleX(1.25);opacity:1}}{p(H + .16)},100%{{transform:translateX(-60px) scaleX(.2);opacity:0}}}}
@keyframes aTrR{{0%{{transform:translateX(235px) scaleX(.5);opacity:0;animation-timing-function:cubic-bezier(.4,0,.9,.55)}}{p(.08)}{{opacity:.9}}{p(H)}{{transform:translateX(56px) scaleX(1.25);opacity:1}}{p(H + .16)},100%{{transform:translateX(60px) scaleX(.2);opacity:0}}}}
@keyframes aFlash{{0%,{p(H)}{{transform:scale(.2);opacity:0}}{p(H + .06)}{{opacity:1}}{p(H + .6)},100%{{transform:scale(2.8);opacity:0}}}}
@keyframes aShock{{0%,{p(H)}{{transform:scale(.35);opacity:0}}{p(H + .03)}{{opacity:1}}{p(H + .75)},100%{{transform:scale(1.9);opacity:0}}}}
@keyframes aHalo{{0%,{p(H + .25)}{{transform:scale(.6);opacity:0}}{p(H + .6)},100%{{transform:scale(1);opacity:1}}}}
@keyframes aGlow{{0%,{p(H + .3)}{{opacity:0}}{p(H + .8)},100%{{opacity:1}}}}
.a-l{{animation:aL {D}s linear both}}
.a-r{{animation:aR {D}s linear both}}
.a-trl{{transform-origin:100% 50%;animation:aTrL {D}s linear both}}
.a-trr{{transform-origin:0 50%;animation:aTrR {D}s linear both}}
.a-flash{{animation:aFlash {D}s ease-out both}}
.a-s1,.a-s2,.a-s3{{animation:aShock {D}s cubic-bezier(.15,.7,.3,1) both}}
.a-s2{{animation-delay:.1s}}
.a-s3{{animation-delay:.2s}}
.a-halo{{animation:aHalo {D}s cubic-bezier(.3,1.4,.5,1) both}}
.a-glow{{animation:aGlow {D}s ease-out both}}
''' + tail(D, H, H + .14, H + .9)

trail = lambda cls, side: (f'    <span class="{cls}" aria-hidden="true" style="position: absolute; top: 18px; {side}; width: 190px; height: 76px; border-radius: 38px; '
                           f'background: linear-gradient({"90deg" if cls == "a-trl" else "270deg"}, rgba(255,164,92,0) 0%, rgba(255,150,100,0.35) 45%, rgba(242,84,91,0.75) 100%); filter: blur(7px)"></span>\n')
bodyA = f'''  <div class="a-glow" aria-hidden="true" style="position: absolute; left: 41px; top: 162px; width: 320px; height: 320px; border-radius: 50%; background: radial-gradient(circle, rgba(255,160,110,0.34), rgba(255,160,110,0) 65%)"></div>
  <div class="a-halo" aria-hidden="true" style="position: absolute; left: 86px; top: 207px; width: 230px; height: 230px">
    {HALO.format(w=3, w2=2.5)}
    <span style="position: absolute; inset: 12px; border-radius: 50%; border: 1px solid rgba(255,170,130,0.45)"></span>
  </div>
  <div style="position: absolute; left: 0; top: 322px; width: 402px; height: 0">
    {ring('a-s1', 140, '4px solid rgba(255,140,90,0.85)')}{ring('a-s2', 140, '3px solid rgba(242,84,91,0.6)')}{ring('a-s3', 140, '2px solid rgba(194,92,240,0.5)')}
    <span class="a-flash" aria-hidden="true" style="position: absolute; left: 136px; top: -65px; width: 130px; height: 130px; border-radius: 50%; background: radial-gradient(circle, rgba(255,255,255,0.98) 0%, rgba(255,180,130,0.8) 35%, rgba(242,84,91,0) 70%)"></span>
    {sparks()}
  </div>
''' + avatars('a-l', 'a-r', trail('a-trl', 'right: 56px') + trail('a-trr', 'left: 56px')) + '\n' + TITLE
write('VoicePrioritySuccessA.dc.html', cssA, bodyA)

# ---------------- B: halo spin-collapse, avatars pop out and collide ----------------
D = 3.4; C = .85; H = 1.3   # collapse, impact
p = lambda t: pct(t, D)
cssB = f'''@keyframes bRing{{0%{{transform:scale(.6) rotate(0);opacity:0;animation-timing-function:cubic-bezier(.3,.6,.6,1)}}{p(.18)}{{transform:scale(1) rotate(60deg);opacity:1;animation-timing-function:cubic-bezier(.6,0,.9,.6)}}{p(C)}{{transform:scale(.22) rotate(900deg);opacity:1}}{p(C + .06)},100%{{transform:scale(.1) rotate(960deg);opacity:0}}}}
@keyframes bRing2{{0%{{transform:scale(.7) rotate(0);opacity:0;animation-timing-function:cubic-bezier(.3,.6,.6,1)}}{p(.25)}{{transform:scale(1) rotate(-40deg);opacity:.8;animation-timing-function:cubic-bezier(.6,0,.9,.6)}}{p(C)}{{transform:scale(.2) rotate(-600deg);opacity:.8}}{p(C + .06)},100%{{transform:scale(.1) rotate(-640deg);opacity:0}}}}
@keyframes bCore{{0%,{p(.2)}{{transform:scale(.2);opacity:0}}{p(C)}{{transform:scale(1);opacity:1}}{p(C + .2)},100%{{transform:scale(2.4);opacity:0}}}}
@keyframes bStreak{{0%,{p(.25)}{{opacity:0;transform:rotate(var(--a)) translateY(-150px) scaleY(.4)}}{p(.5)}{{opacity:.9}}{p(C)}{{opacity:0;transform:rotate(var(--a)) translateY(-30px) scaleY(1.2)}}100%{{opacity:0}}}}
@keyframes bShock{{0%,{p(C)}{{transform:scale(.3);opacity:0}}{p(C + .03)}{{opacity:1}}{p(C + .7)},100%{{transform:scale(2);opacity:0}}}}
@keyframes bL{{0%,{p(C)}{{transform:translateX(0) scale(.3);opacity:0;animation-timing-function:cubic-bezier(.2,.8,.4,1)}}{p(C + .04)}{{opacity:1}}{p(C + .26)}{{transform:translateX(-100px) scale(1);animation-timing-function:cubic-bezier(.55,0,.9,.5)}}{p(H)}{{transform:translateX(-56px) scale(1);animation-timing-function:linear}}{p(H + .05)}{{transform:translateX(-49px) scaleX(.9) scaleY(1.06);animation-timing-function:cubic-bezier(.2,.8,.4,1)}}{p(H + .24)}{{transform:translateX(-65px) scale(1.02);animation-timing-function:ease-in-out}}{p(H + .44)},100%{{transform:translateX(-60px) scale(1);opacity:1}}}}
@keyframes bR{{0%,{p(C)}{{transform:translateX(0) scale(.3);opacity:0;animation-timing-function:cubic-bezier(.2,.8,.4,1)}}{p(C + .04)}{{opacity:1}}{p(C + .26)}{{transform:translateX(100px) scale(1);animation-timing-function:cubic-bezier(.55,0,.9,.5)}}{p(H)}{{transform:translateX(56px) scale(1);animation-timing-function:linear}}{p(H + .05)}{{transform:translateX(49px) scaleX(.9) scaleY(1.06);animation-timing-function:cubic-bezier(.2,.8,.4,1)}}{p(H + .24)}{{transform:translateX(65px) scale(1.02);animation-timing-function:ease-in-out}}{p(H + .44)},100%{{transform:translateX(60px) scale(1);opacity:1}}}}
@keyframes bFlash{{0%,{p(H)}{{transform:scale(.2);opacity:0}}{p(H + .06)}{{opacity:1}}{p(H + .55)},100%{{transform:scale(2.6);opacity:0}}}}
@keyframes bHalo{{0%,{p(H + .2)}{{transform:scale(.6);opacity:0}}{p(H + .55)},100%{{transform:scale(1);opacity:1}}}}
.b-ring{{animation:bRing {D}s linear both}}
.b-ring2{{animation:bRing2 {D}s linear both}}
.b-core{{animation:bCore {D}s cubic-bezier(.5,0,.8,.6) both}}
.b-st{{animation:bStreak {D}s cubic-bezier(.6,0,.9,.5) both}}
.b-shock{{animation:bShock {D}s cubic-bezier(.15,.7,.3,1) both}}
.b-l{{animation:bL {D}s linear both}}
.b-r{{animation:bR {D}s linear both}}
.b-flash{{animation:bFlash {D}s ease-out both}}
.b-halo{{animation:bHalo {D}s cubic-bezier(.3,1.4,.5,1) both}}
.b-halo .q-spin{{animation-duration:2.4s}}
''' + tail(D, H, H + .14, H + .9)

streaks = ''.join(f'<span class="b-st" aria-hidden="true" style="--a: {a}deg; position: absolute; left: 199px; top: -18px; width: 4px; height: 36px; border-radius: 2px; transform-origin: 2px 18px; background: linear-gradient(180deg, rgba(255,180,120,0), rgba(255,140,90,0.9)); animation-delay: {(i % 3) * .05:.2f}s"></span>' for i, a in enumerate(range(0, 360, 30)))
bodyB = f'''  <div style="position: absolute; left: 0; top: 322px; width: 402px; height: 0">
    <div class="b-ring" aria-hidden="true" style="position: absolute; left: 61px; top: -140px; width: 280px; height: 280px; filter: drop-shadow(0 0 10px rgba(255,140,90,0.55))">{HALO.format(w=5, w2=4.5).replace('q-spin', 'b-x')}</div>
    <div class="b-ring2" aria-hidden="true" style="position: absolute; left: 91px; top: -110px; width: 220px; height: 220px; border-radius: 50%; border: 2px dashed rgba(242,84,91,0.55); box-sizing: border-box"></div>
    {streaks}
    <span class="b-core" aria-hidden="true" style="position: absolute; left: 156px; top: -45px; width: 90px; height: 90px; border-radius: 50%; background: radial-gradient(circle, #FFFFFF 0%, rgba(255,200,160,0.95) 30%, rgba(255,140,90,0.6) 55%, rgba(242,84,91,0) 72%)"></span>
    {ring('b-shock', 140, '4px solid rgba(255,140,90,0.8)')}
    <span class="b-flash" aria-hidden="true" style="position: absolute; left: 136px; top: -65px; width: 130px; height: 130px; border-radius: 50%; background: radial-gradient(circle, rgba(255,255,255,0.98) 0%, rgba(255,180,130,0.8) 35%, rgba(242,84,91,0) 70%)"></span>
    {sparks()}
  </div>
  <div class="b-halo" aria-hidden="true" style="position: absolute; left: 86px; top: 207px; width: 230px; height: 230px">
    {HALO.format(w=3, w2=2.5)}
    <span style="position: absolute; inset: 12px; border-radius: 50%; border: 1px solid rgba(255,170,130,0.45)"></span>
  </div>
''' + avatars('b-l', 'b-r') + '\n' + TITLE
write('VoicePrioritySuccessB.dc.html', cssB, bodyB)
print('ok')
