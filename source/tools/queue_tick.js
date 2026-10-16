// Queue page: people-ahead count and estimated wait tick down, then hand over to "It's your turn".
(function () {
  var ahead = document.querySelector('.q-ahead'), wait = document.querySelector('.q-wait');
  var steps = ['999+', '846', '512', '238', '61', '3'], w = 92, i = 0;
  function fmt(s) { return ('0' + Math.floor(s / 60)).slice(-2) + ':' + ('0' + s % 60).slice(-2); }
  var t = setInterval(function () {
    i = Math.min(i + 1, steps.length - 1);
    w = Math.max(0, w - 17);
    if (ahead) ahead.textContent = steps[i];
    if (wait) wait.textContent = fmt(w);
  }, 750);
  setTimeout(function () { clearInterval(t); parent.postMessage({ go: 'turn' }, '*'); }, 4800);
})();
