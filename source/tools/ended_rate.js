// Call-ended page: tap a star to rate; stars up to it light up and the label changes.
(function () {
  var LB = { 1: 'Not my vibe', 2: 'Pretty good', 3: 'Loved it' };
  var stars = [].slice.call(document.querySelectorAll('.ve-star')), label = document.querySelector('.ve-label');
  stars.forEach(function (s) {
    s.addEventListener('click', function () {
      var r = +s.getAttribute('data-rate');
      stars.forEach(function (t) { t.classList.toggle('on', +t.getAttribute('data-rate') <= r); });
      if (label) { label.textContent = LB[r]; label.style.color = '#FFD27A'; }
    });
  });
})();
