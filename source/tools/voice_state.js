// Standard-match attempts left today. The shell posts {left: n}; pages that show the count update in place.
(function () {
  function apply(n) {
    [].forEach.call(document.querySelectorAll('[data-left]'), function (el) { el.textContent = n; });
    [].forEach.call(document.querySelectorAll('.vm-std'), function (b) { b.setAttribute('aria-disabled', n <= 0 ? 'true' : 'false'); });
    [].forEach.call(document.querySelectorAll('[data-dot]'), function (d, i) {
      var on = i < n;
      d.style.background = on ? '#8F6FF0' : '#B9B0C8';
      d.style.opacity = on ? '1' : '.45';
      d.style.boxShadow = on ? '0 0 4px rgba(143,111,240,0.55)' : 'none';
    });
  }
  window.addEventListener('message', function (e) { if (e.data && e.data.left != null) apply(e.data.left); });
})();
