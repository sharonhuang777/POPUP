// My profile: what happens as the posts scroll up (like the reference "他人主页 · 内容贴边").
// - The cover drifts up slower than the page (parallax); pulling down past the top stretches it.
// - When the white sheet reaches the top bar, the bar (status bar + tools) fills with a solid colour
//   taken from the cover, so the tools keep sitting on the cover's colour instead of on white.
// - The glass buttons turn into dark translucent circles with white icons, and the name slides in
//   next to the back button once the name row has passed under the bar.
// scroller: window (demo) or a scrolling element (canvas board).
function mountProfileScroll(scroller, nav, cover, opts) {
  opts = opts || {};
  var BAR = opts.barColor || '#9466E0';
  var clamp = function (v, a, b) { return Math.max(a, Math.min(b, v)); };
  var mix = function (a, b, t) { return a + (b - a) * t; };
  nav.style.zIndex = 5;
  var bg = document.createElement('div');
  bg.setAttribute('aria-hidden', 'true');
  bg.style.cssText = 'position:absolute;left:-16px;right:-16px;top:-54px;height:106px;z-index:-1;pointer-events:none;opacity:0;background:' + BAR;
  nav.insertBefore(bg, nav.firstChild);
  var back = nav.querySelector('button[aria-label="Back"]');
  var title = document.createElement('div');
  title.setAttribute('aria-hidden', 'true');
  title.style.cssText = 'position:absolute;left:56px;top:0;height:44px;max-width:150px;display:flex;align-items:center;opacity:0;pointer-events:none;' +
    'transform:translateY(8px);font-size:18px;font-weight:700;letter-spacing:-0.2px;color:#FFFFFF;white-space:nowrap;overflow:hidden;text-overflow:ellipsis';
  title.textContent = opts.name || '';
  nav.appendChild(title);
  var btns = Array.prototype.slice.call(nav.querySelectorAll('button'));
  var y0 = null;
  function paint() {
    var y = scroller === window ? (window.scrollY || document.documentElement.scrollTop) : scroller.scrollTop;
    if (y === y0) return; y0 = y;
    var t = clamp((y - 150) / 54, 0, 1);   // white sheet meets the bar → bar takes the cover colour
    var s = clamp((y - 245) / 40, 0, 1);   // name row has passed under the bar → name in the bar
    bg.style.opacity = t.toFixed(3);
    btns.forEach(function (b) {
      var c = Math.round(mix(255, 0, t));
      b.style.background = 'rgba(' + c + ',' + c + ',' + c + ',' + mix(0.5, 0.18, t).toFixed(3) + ')';
      b.style.borderColor = 'rgba(255,255,255,' + mix(0.8, 0, t).toFixed(3) + ')';
      b.style.color = t > 0.5 ? '#FFFFFF' : '';
    });
    title.style.opacity = s.toFixed(3);
    title.style.transform = 'translateY(' + mix(8, 0, s).toFixed(1) + 'px)';
    cover.style.transformOrigin = '50% 0';
    cover.style.transform = y >= 0 ? 'translateY(' + (y * 0.45).toFixed(1) + 'px)' : 'scale(' + (1 - y / 330).toFixed(4) + ')';
  }
  var on = function () { requestAnimationFrame(paint); };
  scroller.addEventListener('scroll', on, { passive: true });
  paint();
  return function () { scroller.removeEventListener('scroll', on); };
}
