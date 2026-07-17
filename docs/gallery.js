/* ===== Dan's Logs — Gallery: renders the synced Lightroom album ===== */
(function () {
  var mount = document.getElementById('masonry');
  var empty = document.getElementById('galEmpty');
  if (!mount) return;

  fetch('assets/gallery.json')
    .then(function (r) { return r.ok ? r.json() : null; })
    .then(function (data) {
      var photos = (data && data.photos) || [];
      if (!photos.length) { if (empty) empty.style.display = 'block'; return; }

      mount.innerHTML = photos.map(function (p, i) {
        var ratio = (p.w && p.h) ? ' style="aspect-ratio:' + p.w + '/' + p.h + '"' : '';
        return '<a class="m-item" href="' + p.file + '" data-i="' + i + '"' + ratio + '>' +
          '<img src="' + p.file + '" alt="' + (p.name || 'Photograph') + '" loading="lazy"></a>';
      }).join('');

      initLightbox(photos);
    })
    .catch(function () { if (empty) empty.style.display = 'block'; });

  function initLightbox(photos) {
    var lb = document.getElementById('lb');
    var img = document.getElementById('lbImg');
    var count = document.getElementById('lbCount');
    var cur = 0;

    function show(i) {
      cur = (i + photos.length) % photos.length;
      img.src = photos[cur].file;
      img.alt = photos[cur].name || '';
      if (count) count.textContent = (cur + 1) + ' / ' + photos.length;
      lb.classList.add('on');
      lb.setAttribute('aria-hidden', 'false');
    }
    function hide() { lb.classList.remove('on'); lb.setAttribute('aria-hidden', 'true'); img.src = ''; }

    mount.addEventListener('click', function (e) {
      var a = e.target.closest('.m-item');
      if (!a) return;
      e.preventDefault();
      show(parseInt(a.getAttribute('data-i'), 10) || 0);
    });
    document.getElementById('lbClose').addEventListener('click', hide);
    document.getElementById('lbNext').addEventListener('click', function (e) { e.stopPropagation(); show(cur + 1); });
    document.getElementById('lbPrev').addEventListener('click', function (e) { e.stopPropagation(); show(cur - 1); });
    lb.addEventListener('click', function (e) { if (e.target === lb) hide(); });
    document.addEventListener('keydown', function (e) {
      if (!lb.classList.contains('on')) return;
      if (e.key === 'Escape') hide();
      else if (e.key === 'ArrowRight') show(cur + 1);
      else if (e.key === 'ArrowLeft') show(cur - 1);
    });
  }
})();
