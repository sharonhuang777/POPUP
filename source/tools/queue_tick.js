// Queue page: people-ahead count, progress ring, progress bar (your avatar moves toward the call) and
// estimated wait tick down, then hand over to "It's your turn".
(function () {
  var ahead = document.querySelector('.q-ahead'), wait = document.querySelector('.q-wait'), arc = document.querySelector('.q-arc');
  var fill = document.querySelector('.q-fill'), you = document.querySelector('.q-you');
  var steps = [12, 9, 6, 4, 2, 1], C = 628.3, start = 12, w = 92, i = 0;
  var TRACK = 320, MIN = 0.3; // bar spans 4px…324px; 30% done at the start of the demo
  function fmt(s) { return ('0' + Math.floor(s / 60)).slice(-2) + ':' + ('0' + s % 60).slice(-2); }
  function show(n) {
    var done = 1 - 0.7 * n / start;            // 0.3 → ~1.0 as the line shortens
    if (arc) arc.style.strokeDashoffset = (C * (1 - done)).toFixed(1);
    var px = Math.round(TRACK * Math.max(MIN, done) * 0.86);
    if (fill) fill.style.width = px + 'px';
    if (you) you.style.left = (4 + px - 28) + 'px';
  }
  show(steps[0]);
  var t = setInterval(function () {
    i = Math.min(i + 1, steps.length - 1);
    w = Math.max(0, w - 17);
    if (ahead) ahead.textContent = steps[i];
    if (wait) wait.textContent = fmt(w);
    show(steps[i]);
  }, 750);
  setTimeout(function () { clearInterval(t); parent.postMessage({ go: 'turn' }, '*'); }, 4800);
})();
