// My profile: what happens as the posts scroll up.
// - The cover drifts up slower than the page (parallax); pulling down past the top stretches it.
// - Once the cover is mostly gone, the top bar turns into a frosted white bar and the glass buttons
//   turn into plain light chips.
// - When the name row slides under the bar, a small avatar + "Jules" fades into the bar's centre.
// scroller: window (demo) or a scrolling element (canvas board).
function mountProfileScroll(scroller, nav, cover, opts) {
  opts = opts || {};
  var clamp = function (v, a, b) { return Math.max(a, Math.min(b, v)); };
  var mix = function (a, b, t) { return a + (b - a) * t; };
  nav.style.zIndex = 5;
  var bg = document.createElement('div');
  bg.setAttribute('aria-hidden', 'true');
  bg.style.cssText = 'position:absolute;left:-16px;right:-16px;top:-54px;height:106px;z-index:-1;pointer-events:none;opacity:0;' +
    'background:rgba(255,255,255,0.86);-webkit-backdrop-filter:blur(20px) saturate(1.6);backdrop-filter:blur(20px) saturate(1.6);' +
    'box-shadow:0 1px 0 rgba(83,65,110,0.08),0 8px 24px rgba(83,65,110,0.06)';
  nav.insertBefore(bg, nav.firstChild);
  var title = document.createElement('div');
  title.setAttribute('aria-hidden', 'true');
  title.style.cssText = 'position:absolute;left:50%;top:0;height:44px;display:flex;align-items:center;gap:8px;opacity:0;pointer-events:none;' +
    'transform:translate(-50%,10px);font-size:16px;font-weight:700;letter-spacing:-0.2px;color:#342B43;white-space:nowrap';
  title.innerHTML = '<img src="' + (opts.avatar || '') + '" alt="" style="display:block;width:28px;height:28px;box-sizing:border-box;border-radius:9px;border:1.5px solid #FFFFFF;object-fit:cover;object-position:center 20%;background:#1A1024;box-shadow:0 2px 6px rgba(83,65,110,0.18)">' + (opts.name || '');
  nav.appendChild(title);
  var btns = Array.prototype.slice.call(nav.querySelectorAll('button'));
  var y0 = -1;
  function paint() {
    var y = scroller === window ? (window.scrollY || document.documentElement.scrollTop) : scroller.scrollTop;
    if (y === y0) return; y0 = y;
    var t = clamp((y - 120) / 110, 0, 1);          // bar turns solid
    var s = clamp((y - 230) / 50, 0, 1);           // name arrives in the bar
    bg.style.opacity = t.toFixed(3);
    btns.forEach(function (b) {
      var r = Math.round(mix(255, 244, t)), g = Math.round(mix(255, 241, t)), bl = Math.round(mix(255, 248, t));
      b.style.background = 'rgba(' + r + ',' + g + ',' + bl + ',' + mix(0.5, 1, t).toFixed(3) + ')';
      b.style.borderColor = 'rgba(255,255,255,' + mix(0.8, 0, t).toFixed(3) + ')';
    });
    title.style.opacity = s.toFixed(3);
    title.style.transform = 'translate(-50%,' + mix(10, 0, s).toFixed(1) + 'px)';
    if (y >= 0) { cover.style.transformOrigin = '50% 0'; cover.style.transform = 'translateY(' + (y * 0.45).toFixed(1) + 'px)'; }
    else { cover.style.transformOrigin = '50% 0'; cover.style.transform = 'scale(' + (1 - y / 330).toFixed(4) + ')'; }
  }
  var on = function () { requestAnimationFrame(paint); };
  scroller.addEventListener('scroll', on, { passive: true });
  paint();
  return function () { scroller.removeEventListener('scroll', on); };
}
