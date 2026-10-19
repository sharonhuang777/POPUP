// Queue page: people-ahead count, progress ring and estimated wait tick down, then hand over to "It's your turn".
(function () {
  var ahead = document.querySelector('.q-ahead'), wait = document.querySelector('.q-wait'), arc = document.querySelector('.q-arc');
  var steps = [128, 96, 61, 32, 9, 1], C = 628.3, start = 128, w = 92, i = 0;
  function fmt(s) { return ('0' + Math.floor(s / 60)).slice(-2) + ':' + ('0' + s % 60).slice(-2); }
  function ring(n) { if (arc) arc.style.strokeDashoffset = (C * (0.7 * n / start)).toFixed(1); }
  ring(steps[0]);
  var t = setInterval(function () {
    i = Math.min(i + 1, steps.length - 1);
    w = Math.max(0, w - 17);
    if (ahead) ahead.textContent = steps[i];
    if (wait) wait.textContent = fmt(w);
    ring(steps[i]);
  }, 750);
  setTimeout(function () { clearInterval(t); parent.postMessage({ go: 'turn' }, '*'); }, 4800);
})();
