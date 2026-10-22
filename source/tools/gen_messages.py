# Messages list: longer list + what happens when it scrolls under the top bar, and unread badges on the tab bar.
# - The list scrolls inside the page; the header (title + buttons) stays pinned. As soon as the list scrolls,
#   the header gets a frosted white bar with a hairline, the "Messages" title keeps its size.
# - Tab bar: red count badges on Plaza (5, same as the bell) and Messages (total unread chats).
# - Canvas board: auto-demo scrolls down and back to the top in a loop; scrolling / tapping by hand takes over.
# Usage: python3 gen_messages.py <in Messages.dc.html> <out path>
import re, sys

src, out = sys.argv[1], sys.argv[2]
s = open(src).read()

MORE = [
    ('a1.jpg', 'Kristin Watson', 'lol that playlist is elite, adding everything', '2 h', 2, True),
    ('a6.jpg', 'Marvin McKinney', 'Voice note · 0:42', '3 h', 1, False),
    ('a3.jpg', 'Theresa Webb', 'are you going to the rooftop thing friday?', 'Yesterday', 0, False),
    ('a5.jpg', 'Darlene Robertson', 'thank you for listening last night 🤍', 'Yesterday', 0, True),
    ('a2.jpg', 'Albert Flores', '[Photo]', 'Mon', 0, False),
    ('a4.jpg', 'Savannah Nguyen', 'ok but which bakery was it??', 'Sun', 0, False),
    ('a1.jpg', 'Ronald Richards', 'haha we should do a call again sometime', '01/06', 0, False),
    ('a6.jpg', 'Courtney Henry', 'sent you the recipe!', '01/04', 0, False),
    ('a3.jpg', 'Guy Hawkins', 'good luck tomorrow, you got this', '01/02', 0, False),
    ('a5.jpg', 'Eleanor Pena', 'happy new year!! 🎉', '01/01', 0, False),
]

def row(img, name, pv, tm, badge, online):
    on = '<span class="on" title="Online"></span>' if online else ''
    b = f'<span class="badge">{badge}</span>' if badge else '<span></span>'
    cls = 'pv unread' if badge else 'pv'
    return (f'    <div class="row">\n      <div class="ava"><img src="./img/{img}" alt="">{on}</div>\n      <div class="mid">\n'
            f'        <div class="nm">{name}</div>\n        <div class="{cls}">{pv}</div>\n      </div>\n'
            f'      <div class="side"><span class="tm">{tm}</span>{b}</div>\n    </div>\n')

# pull the pieces out of the current board
bg = re.search(r'  <div aria-hidden="true" style="position: absolute; left: 0; top: 0; width: 402px; height: 240px;.*?</div>\n', s, re.S).group(0)
header = re.search(r'  <header .*?</header>\n', s, re.S).group(0)
card = re.search(r'  <div style="position: absolute; left: 8px; top: 112px;.*?\n  </div>\n', s, re.S).group(0)
lst = re.search(r'  <div style="position: absolute; left: 0; top: 282px; width: 402px">\n(.*?)\n  </div>\n', s, re.S).group(1)
fade = re.search(r'  <div aria-hidden="true" style="position: absolute; left: 0; bottom: 0; width: 402px; height: 140px;.*?</div>\n', s, re.S).group(0)
nav = re.search(r'  <nav aria-label="Tab bar".*?</nav>\n', s, re.S).group(0)

existing_badges = sum(int(x) for x in re.findall(r'<span class="badge">(\d+)</span>', card + lst))
total = existing_badges + sum(m[4] for m in MORE)

card = card.replace('<div style="position: absolute; left: 8px; top: 112px; width: 386px;', '<div style="position: relative; margin: 0 8px; width: 386px;')
lst_html = '  <div style="position: relative; margin-top: 10px; width: 402px">\n' + lst + '\n' + ''.join(row(*m) for m in MORE) + '  </div>\n'
bg_scroll = bg.replace('position: absolute; left: 0; top: 0;', 'position: absolute; left: 0; top: 0; z-index: 0;')

# header: frosted bar behind it that fades in once the list scrolls; title shrinks
header = header.replace('<header style="position: absolute; left: 12px; top: 54px; width: 378px; height: 44px;',
                        '<header class="mh" style="position: absolute; left: 12px; top: 54px; width: 378px; height: 44px; z-index: 3;')
header = header.replace('<h1 style="position: relative; margin: 0;', '<h1 class="mh-t" style="position: relative; margin: 0; transform-origin: 0 50%;')
hbar = ('  <div class="mh-bg" aria-hidden="true" style="position: absolute; left: 0; top: 0; width: 402px; height: 108px; z-index: 2; opacity: 0; '
        'background: rgba(255,255,255,0.78); -webkit-backdrop-filter: blur(20px) saturate(1.4); backdrop-filter: blur(20px) saturate(1.4); '
        'box-shadow: 0 0.5px 0 rgba(46,36,64,0.12), 0 6px 18px rgba(46,36,64,0.05); pointer-events: none"></div>\n')

# tab bar badges
DOT = ('<span class="tb-cnt" aria-label="5 new in Plaza" style="position: absolute; top: 4px; left: calc(50% + 6px); min-width: 18px; height: 18px; '
       'box-sizing: border-box; padding: 0 5px; border-radius: 9px; background: #FF4D5E; border: 1.5px solid #FFFFFF; display: flex; '
       'align-items: center; justify-content: center; font-size: 10.5px; font-weight: 700; line-height: 1; color: #FFFFFF">5</span>')
CNT = (f'<span class="tb-cnt" aria-label="{total} unread" style="position: absolute; top: 4px; left: calc(50% + 6px); min-width: 18px; height: 18px; '
       'box-sizing: border-box; padding: 0 5px; border-radius: 9px; background: #FF4D5E; border: 1.5px solid #FFFFFF; display: flex; '
       f'align-items: center; justify-content: center; font-size: 10.5px; font-weight: 700; line-height: 1; color: #FFFFFF">{total if total < 100 else "99+"}</span>')
nav = re.sub(r'(<button class="tab" aria-label="Plaza"[^>]*>.*?</svg>)(</button>)', lambda m: m.group(1) + DOT + m.group(2), nav, count=1, flags=re.S)
nav = re.sub(r'(<button class="tab" aria-label="Messages"[^>]*>.*?</svg>)(</button>)', lambda m: m.group(1) + CNT + m.group(2), nav, count=1, flags=re.S)
nav = nav.replace('<nav aria-label="Tab bar" style="position: absolute;', '<nav aria-label="Tab bar" style="z-index: 4; position: absolute;')
fade = fade.replace('height: 140px;', 'height: 140px; z-index: 3; pointer-events: none;')

body = (header + hbar +
        '  <div class="msc" data-msc ref="{{ scRef }}" style="position: absolute; inset: 0; z-index: 1; overflow-y: auto; overflow-x: hidden; scrollbar-width: none">\n'
        + bg_scroll + '  <div style="position: relative; z-index: 1; padding: 112px 0 130px">\n' + card + lst_html + '  </div>\n  </div>\n' + fade + nav)

root_open = re.search(r'<div style="position: relative; width: 402px; height: 874px;[^>]*>\n', s).group(0)
new_body = root_open + '\n' + body + '\n</div>\n'
a = s.index(root_open); b = s.index('</x-dc>')
s = s[:a] + new_body + s[b:]

css_add = '''.msc::-webkit-scrollbar{display:none}
'''
s = s.replace('.tab{width:44px;', css_add + '.tab{width:44px;', 1)

LIB = r'''
// Pinned header over a scrolling list: frosted bar fades in over the first 24px of scroll (the title keeps its size).
function mountMsgScroll(sc) {
  if (!sc) return;
  var root = sc.parentNode, bar = root.querySelector('.mh-bg'), t = root.querySelector('.mh-t');
  function paint() { var k = Math.max(0, Math.min(1, sc.scrollTop / 24)); bar.style.opacity = k.toFixed(3); }
  sc.addEventListener('scroll', function () { requestAnimationFrame(paint); }, { passive: true });
  paint();
  return paint;
}
'''
COMP = r'''class Component extends DCLogic {
  componentDidMount() { this.start(); }
  componentWillUnmount() { this.stop(); }
  stop() { clearTimeout(this.t1); cancelAnimationFrame(this.raf); this.auto = false; }
  start() {
    // canvas demo: glide down, pause, glide back to the top, pause, repeat; any touch / wheel hands control to the viewer
    var self = this, sc = this.sc; if (!sc || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    this.auto = true;
    var take = function () { self.stop(); }; sc.addEventListener('wheel', take, { passive: true }); sc.addEventListener('pointerdown', take);
    var glide = function (to, ms, next) { var from = sc.scrollTop, t0 = performance.now();
      var step = function (now) { if (!self.auto) return; var k = Math.min(1, (now - t0) / ms), e = k < .5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2;
        sc.scrollTop = from + (to - from) * e; if (k < 1) self.raf = requestAnimationFrame(step); else self.t1 = setTimeout(next, 1200); };
      self.raf = requestAnimationFrame(step); };
    var loop = function () { if (!self.auto) return; glide(Math.min(560, sc.scrollHeight - sc.clientHeight), 2400, function () { glide(0, 1600, loop); }); };
    this.t1 = setTimeout(loop, 1200);
  }
  renderVals() {
    var self = this;
    if (!this._sc) this._sc = function (el) { self.sc = el; if (el) { mountMsgScroll(el); self.stop(); self.start(); } };
    return { scRef: this._sc };
  }
}'''
s = re.sub(r'class Component extends DCLogic \{.*?\n\}', lambda m: LIB.strip() + '\n' + COMP, s, count=1, flags=re.S)
open(out, 'w').write(s)
print('ok', total)
