(function () {
  var INSIGHTS = [
    'You stay when a conversation gets unexpectedly honest.',
    'You open up when connections feel natural.',
    'You value space that still carries reassurance.'
  ];
  var kicker = document.querySelector('.kicker');
  var btn = document.createElement('button');
  btn.type = 'button'; btn.className = 'ins-toggle'; btn.setAttribute('aria-label', 'Pause insights');
  var PAUSE = '<svg width="10" height="10" viewBox="0 0 10 10" aria-hidden="true"><rect x="1.5" y="1" width="2.4" height="8" rx="1" fill="currentColor"/><rect x="6.1" y="1" width="2.4" height="8" rx="1" fill="currentColor"/></svg>';
  var PLAY = '<svg width="10" height="10" viewBox="0 0 10 10" aria-hidden="true"><path d="M2.6 1.4v7.2c0 .5.5.8.9.5l5.4-3.6c.4-.3.4-.8 0-1.1L3.5.9c-.4-.3-.9 0-.9.5z" fill="currentColor"/></svg>';
  btn.innerHTML = PAUSE;
  kicker.appendChild(btn);

  var idx = 0, paused = false, running = false, timer = null, typing = false;
  var origUpdate = updateCopy;
  function stop() { clearTimeout(timer); timer = null; running = false; typing = false; }
  function setBtn() {
    btn.innerHTML = paused ? PLAY : PAUSE;
    btn.setAttribute('aria-label', paused ? 'Play insights' : 'Pause insights');
    btn.setAttribute('aria-pressed', String(paused));
  }
  function showFull() { title.textContent = INSIGHTS[idx]; title.classList.remove('typing'); typing = false; }
  function hold() { if (INSIGHTS.length > 1) timer = setTimeout(next, 3800); }
  function next() {
    title.classList.add('ins-out');
    timer = setTimeout(function () { title.classList.remove('ins-out'); idx = (idx + 1) % INSIGHTS.length; typeCurrent(); }, 320);
  }
  function typeCurrent() {
    var chars = Array.from(INSIGHTS[idx]), i = 0;
    title.setAttribute('aria-label', INSIGHTS[idx]);
    if (motion.matches) { showFull(); hold(); return; }
    title.textContent = ''; title.classList.add('typing'); typing = true;
    (function step() {
      if (paused) return;
      if (document.hidden) { timer = setTimeout(step, 150); return; }
      title.textContent += chars[i++];
      if (i >= chars.length) { title.classList.remove('typing'); typing = false; hold(); return; }
      timer = setTimeout(step, chars[i - 1] === '.' ? 300 : 36 + (i % 4) * 5);
    })();
  }
  function startRotation() {
    stop(); running = true;
    title.classList.remove('thinking-copy');
    btn.hidden = false;
    if (paused) { showFull(); return; }
    typeCurrent();
  }
  updateCopy = function (state) {
    if (state === 'idle') { clearTimeout(typingTimer); startRotation(); return; }
    stop(); btn.hidden = true; title.classList.remove('ins-out');
    origUpdate(state);
  };
  btn.addEventListener('click', function (e) {
    e.stopPropagation();
    paused = !paused; setBtn();
    if (!running) return;
    if (paused) { clearTimeout(timer); title.classList.remove('ins-out'); showFull(); }
    else { clearTimeout(timer); hold(); }
  });
  btn.hidden = orb.state !== 'idle';
  if (orb.state === 'idle') startRotation();
  // Greet first, then settle into the understanding carousel.
  if (orb.state === 'thinking') { clearTimeout(returnTimer); returnTimer = setTimeout(function () { setState('idle'); }, 8500); }
})();
