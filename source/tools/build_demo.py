import json
import os
import re, json, base64, io, os
from PIL import Image

import os as _os
S = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
R = S + '/remote/project/'
IMG = S + '/canvas/project/img/'

def data_uri(name, maxw=None, q=72):
    path = IMG + name
    im = Image.open(path)
    if name.endswith('.png'):
        if maxw and im.width > maxw:
            im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
        if name == 'avatar.png':
            b = io.BytesIO(); im.convert('RGB').save(b, 'JPEG', quality=80); mime = 'image/jpeg'
        else:
            b = io.BytesIO(); im.save(b, 'PNG', optimize=True); mime = 'image/png'
    else:
        im = im.convert('RGB')
        if maxw and im.width > maxw:
            im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
        b = io.BytesIO(); im.save(b, 'JPEG', quality=q, optimize=True); mime = 'image/jpeg'
    return 'data:%s;base64,%s' % (mime, base64.b64encode(b.getvalue()).decode())

IMGS = {}
def img(name):
    if name not in IMGS:
        IMGS[name] = data_uri(name, maxw=None if name.startswith(('u', 'tab', 'coin', 'avatar')) else 520)
    return IMGS[name]

def parts(fname):
    s = open(R + fname).read()
    helmet = re.search(r'<helmet>(.*?)</helmet>', s, re.S).group(1)
    body = re.search(r'</helmet>(.*?)</x-dc>', s, re.S).group(1)
    script = re.search(r'<script type="text/x-dc"[^>]*>(.*?)</script>', s, re.S).group(1)
    lib = script.split('class Component')[0]
    return helmet, body, lib

def clean(body):
    body = re.sub(r'<sc-if value="\{\{ odd \}\}"[^>]*>.*?</sc-if>', '', body, flags=re.S)
    body = re.sub(r'<sc-if value="\{\{ even \}\}"[^>]*>', '', body)
    body = body.replace('</sc-if>', '')
    body = body.replace('ref="{{ orbRef }}"', 'data-orb').replace('onClick="{{ replay }}"', '')
    body = body.replace('ref="{{ coverRef }}"', 'data-cover').replace('ref="{{ cloudRef }}"', 'data-cloud')
    body = body.replace('"</path>', '"></path>')
    body = re.sub(r'\./img/([a-z0-9-]+\.(?:png|jpg))', lambda m: img(m.group(1)), body)
    body = body.replace('aria-label="Plaza"', 'data-go="plaza" aria-label="Plaza"')
    body = body.replace('aria-label="Home · Popup"', 'data-go="home" aria-label="Home · Popup"')
    body = body.replace('aria-label="Messages"', 'data-go="messages" aria-label="Messages"')
    body = body.replace('aria-label="My profile"', 'data-go="profile" aria-label="My profile"')
    return body

NAV = """
(function () {
  var st = document.createElement('style');
  st.textContent = '@keyframes tabPop{0%{transform:scale(1)}35%{transform:scale(.8)}70%{transform:scale(1.14)}100%{transform:scale(1)}}.tab-pop{animation:tabPop .5s cubic-bezier(.34,1.56,.64,1)}';
  document.head.appendChild(st);
})();
function tabBar() { return document.querySelector('nav[aria-label="Tab bar"], .bottom-nav'); }
function tabItems(bar, pill) { return Array.prototype.filter.call(bar.children, function (c) { return c !== pill; }); }
var OWN_IDX = (function () {
  var bar = tabBar(), pill = bar && bar.querySelector('.tab-pill');
  if (!pill) return null;
  var m = new DOMMatrixReadOnly(getComputedStyle(pill).transform);
  return Math.round(m.m41 / (pill.offsetWidth || 1));
})();
window.addEventListener('message', function (e) {
  if (!e.data || e.data.pillFrom == null || OWN_IDX == null) return;
  var bar = tabBar(), pill = bar.querySelector('.tab-pill');
  var from = e.data.pillFrom, tr = pill.style.transition || getComputedStyle(pill).transition;
  pill.style.transition = 'none';
  pill.style.transform = 'translateX(' + (from * 100) + '%)';
  void pill.offsetWidth;
  pill.style.transition = '';
  requestAnimationFrame(function () { pill.style.transform = 'translateX(' + (OWN_IDX * 100) + '%)'; });
  var item = tabItems(bar, pill)[OWN_IDX];
  if (item) { item.classList.remove('tab-pop'); void item.offsetWidth; item.classList.add('tab-pop'); }
});
document.addEventListener('click', function (e) {
  var g = e.target.closest('[data-go]');
  if (g) {
    e.preventDefault();
    var msg = { go: g.getAttribute('data-go') };
    if (g.classList.contains('match-card') || g.classList.contains('talk-button')) {
      g.classList.add('pressed');
      setTimeout(function () { parent.postMessage(msg, '*'); setTimeout(function () { g.classList.remove('pressed'); }, 400); }, 170);
      return;
    }
    if (g.closest('nav[aria-label="Tab bar"], .bottom-nav') && OWN_IDX != null) msg.from = OWN_IDX;
    parent.postMessage(msg, '*'); return;
  }
  var b = e.target.closest('[aria-label="Back"]');
  if (b) { e.preventDefault(); parent.postMessage({ back: 1 }, '*'); }
});
"""

def page(helmet, body, js, scroll=False):
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=402">'
            + helmet +
            '<style>html,body{margin:0;background:#FBF3EE}body{overflow-x:hidden;overflow-y:%s}::-webkit-scrollbar{display:none}button{-webkit-tap-highlight-color:transparent}</style>'
            '</head><body>' % ('auto' if scroll else 'hidden') + body + '<script>' + js + NAV + '</script></body></html>')

screens = {}

# Home (user's dynamic home file)
home = open(S + '/demo/home-preview.html').read()
fit_css = ('<style>html,body{margin:0;overflow:hidden;background:#fcf1e8}main{display:block!important;min-height:0!important;padding:0!important}'
           '.phone{width:402px!important;height:874px!important;aspect-ratio:auto!important;border-radius:0!important;box-shadow:none!important}'
           '.panel{position:absolute!important;left:-9999px!important;visibility:hidden!important}'
           '.phone .statusbar,.phone .home-indicator{display:none!important}'
           '.match-card,.bottom-nav svg,.avatar{cursor:pointer}</style>')
home = home.replace('</head>', fit_css + '</head>', 1)
mc = '<div class="match-card">'
assert home.count(mc) == 2
home = home.replace(mc, '<div class="match-card" data-go="text">', 1).replace(mc, '<div class="match-card" data-go="voice">', 1)
assert home.count('<button id="talk" class="talk-button">')==1
home = home.replace('<button id="talk" class="talk-button">','<button id="talk" class="talk-button" data-go="chat">',1)
assert home.count("document.getElementById('talk').onclick=")==1
home = home.replace("document.getElementById('talk').onclick=","window.__talkOrb=",1)
home = home.replace('aria-label="广场"', 'aria-label="广场" data-go="plaza"', 1)
home = home.replace('aria-label="聊天"', 'aria-label="聊天" data-go="messages"', 1)
home = home.replace('<div class="avatar"', '<div class="avatar" data-go="profile"', 1)
import re as _re
home, _n = _re.subn(r'<img src="data:[^"]*" alt="AI，当前页面">', '<img src="' + img('orb-static.png') + '" alt="AI，当前页面" class="nav-orb">', home, count=1)
assert _n == 1
home = home.replace('</head>', '<style>.phone .bottom-nav{top:auto!important;bottom:34px!important;left:16px!important;right:16px!important;height:58px!important;box-sizing:border-box;border-radius:29px!important;border:none!important;display:grid!important;overflow:hidden!important;grid-template-columns:1fr 1fr 1fr;align-items:center;justify-items:center;padding:6px!important;background:linear-gradient(180deg,rgba(247,246,250,0.88) 0%,rgba(236,234,241,0.84) 100%)!important;-webkit-backdrop-filter:blur(20px) saturate(1.6)!important;backdrop-filter:blur(20px) saturate(1.6)!important;box-shadow:inset 0 0 0 1.5px rgba(255,255,255,0.95),inset 0 2px 3px rgba(255,255,255,0.9),inset 0 -2px 6px rgba(90,80,120,0.06),0 14px 32px rgba(40,30,70,0.13),0 2px 6px rgba(40,30,70,0.06)!important}.phone .bottom-nav>*{position:relative;z-index:1}.phone .bottom-nav>.tab-pill{position:absolute;z-index:0;left:6px;top:6px;bottom:6px;width:calc((100% - 12px)/3);border-radius:23px;background:#fff;box-shadow:0 2px 8px rgba(40,30,70,0.08),0 0 0 0.5px rgba(40,30,70,0.04);transform:translateX(100%);transition:transform .55s cubic-bezier(.34,1.3,.64,1)}.phone .bottom-nav svg{stroke:#2B2533!important}.phone .bottom-nav img.nav-orb{width:40px!important;height:40px!important;border-radius:50%;border:none;box-sizing:border-box;object-fit:cover;background:#EEE8F8;filter:none!important;box-shadow:0 3px 10px rgba(143,114,242,0.3)}</style></head>', 1)
home = home.replace('</head>', '<style>.phone .brand{left:12px!important;width:auto!important;top:56px!important;height:40px;line-height:40px;text-align:left!important}.phone .avatar{top:56px!important;left:auto!important;right:12px!important;width:40px!important;height:40px!important;aspect-ratio:auto!important;box-sizing:border-box;border:2px solid #fff;background:#1A1024 url(' + img('avatar.png') + ') center 20%/cover no-repeat!important;box-shadow:0 0 0 1px rgba(164,135,242,0.35),0 4px 12px rgba(83,65,110,0.14)}.phone .bell{top:56px!important;right:64px!important;width:40px!important;height:40px!important;aspect-ratio:auto!important;box-sizing:border-box;background:rgba(255,255,255,0.65)!important;border:1px solid rgba(255,255,255,0.9)!important;box-shadow:0 4px 12px rgba(83,65,110,0.08)}.phone .bell img{width:30px!important;height:30px!important}</style></head>', 1)
home, _n = _re.subn(r'<div class="bell"><img src="data:[^"]*" alt="通知"></div>', '<div class="bell coins" role="img" aria-label="Coins: 120"><img src="' + img('coin-home.png') + '" alt=""><span>120</span></div>', home, count=1)
assert _n == 1
home = home.replace('</head>', '<style>.phone .bell.coins{width:auto!important;padding:0 14px 0 6px;border-radius:20px!important;display:flex!important;align-items:center;gap:6px;font-size:15px;font-weight:600;color:#3B2F52;font-variant-numeric:tabular-nums}.phone .bell.coins img{width:28px!important;height:28px!important;object-fit:contain;filter:drop-shadow(0 1px 2px rgba(200,140,20,0.35))}</style></head>', 1)
assert home.count('<div class="bottom-nav" aria-label="底部导航">') == 1
home = home.replace('<div class="bottom-nav" aria-label="底部导航">', '<div class="bottom-nav" aria-label="底部导航"><span class="tab-pill" aria-hidden="true"></span>', 1)
home = home.replace('</head>', '<style>.ins-toggle{margin-left:1px;width:22px;height:22px;padding:0;border-radius:50%;border:0;background:transparent;color:#B9AEC8;display:inline-flex;align-items:center;justify-content:center;cursor:pointer;-webkit-tap-highlight-color:transparent}.ins-toggle svg{width:9px;height:9px}.ins-toggle[hidden]{display:none}.ins-toggle:active{transform:scale(.9)}.phone .insight-title{transition:opacity .3s ease,filter .3s ease}.phone .match-card{transition:transform .2s cubic-bezier(.2,.8,.2,1),background-color .2s ease,box-shadow .2s ease;-webkit-tap-highlight-color:transparent}.phone .talk-button{transition:transform .18s cubic-bezier(.2,.8,.2,1),background-color .18s ease;-webkit-tap-highlight-color:transparent}.phone .talk-button:active,.phone .talk-button.pressed{transform:scale(.95);background-color:rgba(255,255,255,0.75)!important}.phone .match-card:active,.phone .match-card.pressed{transform:scale(.97);background-color:rgba(255,255,255,0.5)!important;box-shadow:0 2px 10px rgba(110,80,170,0.10)}.phone .insight-title.ins-out{opacity:0;filter:blur(3px)}</style></head>', 1)
home = home.replace('</body>', '<script>' + open(S + '/demo/home-insights.js').read() + NAV + "\ndocument.addEventListener('touchstart', function () {}, { passive: true });\n" + '</script></body>', 1)
assert home.count('data-go=') == 6
screens['home'] = home
open(S + '/demo/home-built.html', 'w').write(home)

# Voice launch
h, b, _ = parts('V2LaunchAccent.dc.html')
b = clean(b)
starts = [m.start() for m in re.finditer(r'<button style="margin-top: 10px; width: 100%; height: 46px;', b)]
assert len(starts) == 2, starts
b = b[:starts[1]] + '<button data-go="pri" ' + b[starts[1] + 8:]
b = b[:starts[0]] + '<button class="vm-std" data-go="stdx" ' + b[starts[0] + 8:]
VSTATE = open(S + '/tools/voice_state.js').read()
# Attempts-left dots and count follow the demo's state
_dot = '<span style="width: 5px; height: 5px; border-radius: 50%;'
assert b.count(_dot) == 2 and b.count('<span title="Used" style="width: 5px;') == 1
b = b.replace(_dot, '<span data-dot="1" style="width: 5px; height: 5px; border-radius: 50%;').replace('<span title="Used" style="width: 5px;', '<span data-dot="1" style="width: 5px;')
assert b.count('2 left today') == 1
b = b.replace('2 left today', '<span data-left="2">2</span> left today')
h += '<style>.vm-std[aria-disabled="true"]{opacity:.45}</style>'
screens['voice'] = page(h, b, VSTATE)

# Voice match: queue, your turn, match failed
def back_to_voice(b):
    assert b.count('<button aria-label="Back"') == 1
    return b.replace('<button aria-label="Back"', '<button data-go="voice" aria-label="Back"')
h, b, _ = parts('VoiceQueue.dc.html')
# Queue comes after the thinking page; skipping the line or taking the priority line connects straight away,
# the regular line makes a standard attempt (the demo's first one fails).
b = back_to_voice(clean(b)); assert b.count('data-go="pri"') == 1
screens['queue'] = page(h, b.replace('data-go="pri"', 'data-go="call"'), open(S + '/tools/queue_tick.js').read())
h, b, _ = parts('VoiceTurn.dc.html')
b = back_to_voice(clean(b)); assert b.count('data-go="pri"') == 1 and b.count('data-go="std"') == 1
screens['turn'] = page(h, b.replace('data-go="pri"', 'data-go="call"').replace('data-go="std"', 'data-go="regular"'), '')
h, b, _ = parts('VoiceFail.dc.html')
screens['fail'] = page(h, back_to_voice(clean(b)), VSTATE)

THINK_ROT = open(S + '/tools/think_rotate.js').read()
def think(fname, mount, after=None, phrases=None):
    h, b, lib = parts(fname)
    end = ("parent.postMessage({ go: '%s' }, '*');" % after) if after else "location.reload();"
    js = lib + "\nvar c = document.querySelector('canvas[data-orb]');\n" + mount + \
         "\nc.addEventListener('click', function () { location.reload(); });\nsetTimeout(function () { " + end + " }, CYCLE_MS);\n" + ('window.__THINK_PHRASES=' + json.dumps(phrases) + ';\n' + THINK_ROT if phrases else '')
    return page(h, clean(b), js)

VP = ["Searching with the signals you've shared…", 'Listening for a voice that matches your pace…', 'Reading between your answers…', 'Weighing honesty over small talk…', 'Finding someone who stays up late too…', 'Almost there, narrowing it down…']
TP = ["Searching with the signals you've shared…", 'Reading between your answers…', 'Looking for someone who remembers the little things…', 'Weighing honesty over small talk…', 'Finding someone who stays up late too…', 'Almost there, narrowing it down…']
screens['std'] = think('V2Think1.dc.html', "new PearlOrb(c, { palette: POPUP_PURPLE, state: 'thinking' });", 'call')
screens['pri'] = think('V2VoiceThink1.dc.html', "new PearlOrb(c, { palette: POPUP_VOICE, state: 'thinking' });", 'call')
screens['text'] = think('TextThink.dc.html', "new PearlOrb(c, { palette: POPUP_MIST, state: 'thinking' });", 'tmatched')

h, b, lib = parts('ProfileMe.dc.html')
PSCROLL = open(S + '/tools/profile_scroll.js').read()
screens['profile'] = page(h, clean(b), lib + "\nmountGravityTags(document.querySelector('[data-cover]'), document.querySelector('[data-cloud]'));\n" + PSCROLL +
    "\nvar _pn = document.querySelector('button[aria-label=\"Back\"]').parentNode; _pn.style.position = 'fixed';\n"
    "mountProfileScroll(window, _pn, document.querySelector('[data-cover]'), { name: 'Jules' });\n", scroll=True)

h, b, lib = parts('ProfileOther.dc.html')
screens['other'] = page(h, clean(b), lib + "\nmountGravityTags(document.querySelector('[data-cover]'), document.querySelector('[data-cloud]'));\n", scroll=True)

h, b, _ = parts('Plaza.dc.html')
b = clean(b)
b = b.replace('<img class="av"', '<img data-go="other" style="cursor:pointer" class="av"').replace('<div class="nm">', '<div class="nm" data-go="other" style="cursor:pointer">')
b = b.replace('<nav aria-label="Tab bar" style="position: absolute;', '<nav aria-label="Tab bar" style="position: fixed;')
b = b.replace('<div aria-hidden="true" style="position: absolute; left: 0; bottom: 0; width: 402px; height: 140px;', '<div aria-hidden="true" style="position: fixed; left: 0; bottom: 0; width: 402px; height: 140px;')
screens['plaza'] = page(h, b, '', scroll=True)

def small(path,w):
    im=Image.open(path).convert('RGBA');im=im.resize((w,round(im.height*w/im.width)),Image.LANCZOS);b=io.BytesIO();im.save(b,'PNG',optimize=True)
    return 'data:image/png;base64,'+base64.b64encode(b.getvalue()).decode()
chat=open(S+'/demo/chat.html').read().replace('%%ORB%%',small(IMG+'orb-static.png',96)).replace('%%ICT%%',small(S+'/demo/mic0.png',120)).replace('%%ICV%%',small(S+'/demo/mic1.png',120)).replace('%%ME%%',small(IMG+'avatar.png',96))
chat=chat.replace('</script></body>', NAV.replace("var g = e.target.closest('[data-go]');","var g = null;") + '</script></body>')
screens['chat']=chat
# Match success: avatars collide, title lands on impact; once everything is in (~0.9s) wait 1s, then the call.
h, b, _ = parts('VoiceMatchSuccess.dc.html')
b = re.sub(r' data-loop="\d+" ref="\{\{ rootRef \}\}"', '', clean(b)).replace('data-ms-root  style="cursor: pointer; ', 'style="')
assert b.count('<button aria-label="Close"') == 1 and b.count('<button aria-label="Minimize"') == 1
b = b.replace('<button aria-label="Close"', '<button data-go="voice" aria-label="Close"').replace('<button aria-label="Minimize"', '<button data-go="home" aria-label="Minimize"')
screens['matched'] = page(h, b, "setTimeout(function () { parent.postMessage({ go: 'call' }, '*'); }, 1900);\n")
# Priority match success (halo spin-collapse, avatars pop out and collide): everything is in by ~2.2s, then 1s, then the call.
h, b, _ = parts('VoicePrioritySuccess.dc.html')
b = re.sub(r' data-loop="\d+" ref="\{\{ rootRef \}\}"', '', clean(b)).replace('data-ms-root  style="cursor: pointer; ', 'style="')
assert b.count('<button aria-label="Close"') == 1 and b.count('<button aria-label="Minimize"') == 1
b = b.replace('<button aria-label="Close"', '<button data-go="voice" aria-label="Close"').replace('<button aria-label="Minimize"', '<button data-go="home" aria-label="Minimize"')
screens['pmatched'] = page(h, b, "setTimeout(function () { parent.postMessage({ go: 'call' }, '*'); }, 3200);\n")
# Priority match success, receiving side (someone else used Priority and reached you): in by ~1.6s, then 1s, then the call.
h, b, _ = parts('VoicePriorityReceived.dc.html')
b = re.sub(r' data-loop="\d+" ref="\{\{ rootRef \}\}"', '', clean(b)).replace('data-ms-root  style="cursor: pointer; ', 'style="')
b = b.replace('<button aria-label="Close"', '<button data-go="voice" aria-label="Close"').replace('<button aria-label="Minimize"', '<button data-go="home" aria-label="Minimize"')
screens['preceived'] = page(h, b, "setTimeout(function () { parent.postMessage({ go: 'call' }, '*'); }, 2600);\n")
# Device check failed (network): Close → Voice Match, Try again → the check/thinking page again, Back home → home.
h, b, _ = parts('VoiceDeviceFail.dc.html')
b = clean(b)
assert b.count('<button aria-label="Close"') == 1 and b.count('>Try again</button>') == 1 and b.count('>Back home</button>') == 1
b = b.replace('<button aria-label="Close"', '<button data-go="voice" aria-label="Close"')
b = b.replace('<button style="position: absolute; left: 16px; top: 728px;', '<button data-go="std" style="position: absolute; left: 16px; top: 728px;')
b = b.replace('<button style="position: absolute; left: 16px; top: 794px;', '<button data-go="home" style="position: absolute; left: 16px; top: 794px;')
assert b.count('data-go="std"') == 1 and b.count('data-go="home"') == 1
screens['devfail'] = page(h, b, '')
# Text match: candidates roll with shared tags lighting, then "86% Match degree · Chat now!". Plays once and holds.
h, b, _ = parts('TextMatchSuccess.dc.html')
h = h.replace('.ambient{animation:drift 28s ease-in-out infinite}', '.ambient{animation:drift 28s ease-in-out INF}')
h = h.replace(' infinite}', ' both}').replace(' INF}', ' infinite}')
h = h.replace('.t-scene{animation:tScene', '.t-scene{animation-name:none;--was:tScene')   # no fade-out at the end
b = clean(b)
assert b.count('<button aria-label="Close"') == 1
b = b.replace('<button aria-label="Close"', '<button data-go="home" aria-label="Close"')
screens['tmatched'] = page(h, b, '')
h, b, _ = parts('VoiceCall.dc.html')
b = clean(b).replace('<button aria-label="End call"', '<button data-go="ended" aria-label="End call"').replace('<button aria-label="Minimize"', '<button data-go="home" aria-label="Minimize"')
# The call page's His Tag row and bottom controls keep the old app's Montserrat; embed it (Google Fonts links are stripped).
MONT = ''.join("@font-face{font-family:Montserrat;font-style:normal;font-weight:%d;font-display:swap;src:url(data:font/woff2;base64,%s) format('woff2')}" % (w, base64.b64encode(open(S + '/demo/montserrat-%d.woff2' % w, 'rb').read()).decode()) for w in (500, 600))
screens['call'] = page(h.replace('body{margin:0}', MONT + 'body{margin:0;background:#1F1540}'), b, open(S+'/tools/call_reveal.js').read())
h, b, _ = parts('VoiceEnded.dc.html')
screens['ended'] = page(h.replace('body{margin:0}', 'body{margin:0;background:#1F1540}'), clean(b), VSTATE + open(S + '/tools/ended_rate.js').read())
h, b, _ = parts('Messages.dc.html')
screens['messages'] = page(h, clean(b), '')

def premul(v):
    v = v.replace("premultipliedAlpha: false", "premultipliedAlpha: true")
    return v.replace("gl_FragColor=vec4(col,edge*glassAlpha);", "float pa=edge*glassAlpha;gl_FragColor=vec4(col*pa,pa);")
HIDE = '<style>nav[aria-label="Tab bar"],.phone .bottom-nav{display:none!important}</style>'
screens = {k: premul(v) for k, v in screens.items()}
for _k in ('home', 'plaza', 'messages'):
    screens[_k] = screens[_k].replace('</head>', HIDE + '</head>', 1)
for k, v in screens.items():
    assert '{{' not in v, k

os.makedirs(S + '/demo/screens', exist_ok=True)
for _k, _v in screens.items(): open(S + '/demo/screens/' + _k + '.html', 'w').write(_v)
shell = open(S + '/demo/shell.html').read().replace('/*SCREENS*/{}', json.dumps(screens).replace('</', '<\\/')).replace('/*ORB*/', img('orb-static.png'))

import re as _re, base64 as _b64
_F=_b64.b64encode(open(S+'/demo/outfit.woff2','rb').read()).decode()
_FF='@font-face{font-family:Outfit;font-style:normal;font-weight:100 900;font-display:swap;src:url(data:font/woff2;base64,'+_F+')}'
shell=_re.sub(r'<link href=\\"https://fonts\.googleapis\.com/css2\?[^>]*?>', '<style>'+_FF+'</style>', shell)
shell=_re.sub(r'<link[^>]*fonts\.(googleapis|gstatic)\.com[^>]*>', '', shell)
if 'fonts.googleapis.com' in shell: print('WARN google fonts remain')
shell=shell.replace('<style>', '<style>'+_FF, 1) if _FF not in shell[:shell.find('</style>')] else shell
open(S + '/demo/Popup Demo.html', 'w').write(shell)
print({k: len(v) for k, v in screens.items()}, len(shell))
