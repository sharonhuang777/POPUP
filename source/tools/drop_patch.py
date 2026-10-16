import sys
for p in sys.argv[1:]:
    s=open(p).read()
    R=[
    ("  var bound = function (b) {\n    var m = metrics(),",
     "  var bound = function (b) {\n    if (b.delay > 0) return;\n    var m = metrics(),"),
    ("    if (b.y < m.pad) { b.y = m.pad; b.vy = Math.abs(b.vy) * .28; }\n    if (b.y > maxY) { b.y = maxY; b.vy = -Math.abs(b.vy) * .18; }",
     "    if (b.falling && b.y >= m.pad) b.falling = false;\n    if (b.y < m.pad && !b.falling) { b.y = m.pad; b.vy = Math.abs(b.vy) * .28; }\n    if (b.y > maxY) { b.y = maxY; if (b.fresh) { b.fresh = false; b.vy = -Math.abs(b.vy) * .42; b.spin += (Math.random() - .5) * 2.4; } else b.vy = -Math.abs(b.vy) * .18; }"),
    ("  var collide = function (a, b, positionOnly) {\n",
     "  var collide = function (a, b, positionOnly) {\n    if (a.delay > 0 || b.delay > 0) return;\n"),
    ("    bodies.forEach(function (b) {\n      var m = metrics(), floor = m.height - b.height - m.pad;",
     "    bodies.forEach(function (b) {\n      if (b.delay > 0) { b.delay--; return; }\n      var m = metrics(), floor = m.height - b.height - m.pad;"),
    ("  var step = function () {",
     """  var drop = function () {
    measure(); var m = metrics(), order = bodies.slice().sort(function () { return Math.random() - .5; });
    order.forEach(function (b, i) {
      var maxX = Math.max(m.pad, m.width - b.width - m.pad);
      b.x = m.pad + Math.random() * (maxX - m.pad); b.y = -(cloud.offsetTop || 100) - b.height - 10;
      b.vx = (Math.random() - .5) * 1.6; b.vy = 1 + Math.random() * 2; b.rotation = (Math.random() - .5) * 16; b.spin = (Math.random() - .5) * .8;
      b.delay = 4 + i * 5 + Math.round(Math.random() * 3); b.falling = true; b.fresh = true;
    });
    drawAll();
  };
  var step = function () {"""),
    ("raf = requestAnimationFrame(function () { raf = 0; if (disposed) return; place(); wake(170); });",
     "raf = requestAnimationFrame(function () { raf = 0; if (disposed) return; if (reduced) { place(); return; } drop(); wake(150 + bodies.length * 6); });"),
    ]
    for a,b in R:
        assert s.count(a)==1,(p,a[:50]); s=s.replace(a,b)
    open(p,'w').write(s); print('ok',p)
