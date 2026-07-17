/* ===== Dan's Logs — Gallery: album wall + per-album photo view =====
   Reads docs/assets/gallery.json (written by scripts/sync_lightroom.py):
     { size, albums: [ { slug, title, cover, count, photos:[{file,name,w,h}] } ] }
   - On Gallery.html  (#albumWall)  -> renders the wall of project covers
   - On Album.html    (#masonry)    -> renders one album's photos + lightbox
*/
(function () {
  var wall = document.getElementById('albumWall');
  var masonry = document.getElementById('masonry');
  var empty = document.getElementById('galEmpty');
  if (!wall && !masonry) return;

  fetch('assets/gallery.json')
    .then(function (r) { return r.ok ? r.json() : null; })
    .then(function (data) {
      var albums = (data && data.albums) || [];
      if (!albums.length) { if (empty) empty.style.display = 'block'; return; }
      if (wall) renderWall(albums);
      if (masonry) renderAlbum(albums);
    })
    .catch(function () { if (empty) empty.style.display = 'block'; });

  /* ---- The wall of projects (Gallery.html) ---- */
  function renderWall(albums) {
    wall.innerHTML = albums.map(function (a) {
      return '' +
        '<a class="album-card" href="Album.html?a=' + encodeURIComponent(a.slug) + '">' +
        '  <div class="album-ph"><img src="' + a.cover + '" alt="' + esc(a.title) + '" loading="lazy"></div>' +
        '  <div class="album-meta">' +
        '    <span class="at">' + esc(a.title) + '</span>' +
        '    <span class="ac">' + a.count + ' photo' + (a.count === 1 ? '' : 's') + '</span>' +
        '    <span class="ar">↗</span>' +
        '  </div>' +
        '</a>';
    }).join('');
  }

  /* ---- One album's photos + lightbox (Album.html) ---- */
  function renderAlbum(albums) {
    var slug = new URLSearchParams(location.search).get('a');
    var i = albums.findIndex(function (a) { return a.slug === slug; });
    if (i < 0) i = 0;
    var album = albums[i];
    var photos = album.photos || [];

    document.title = album.title + " — Dan's Logs";
    setText('albumTitle', album.title);
    setText('albumCount', album.count + ' photo' + (album.count === 1 ? '' : 's'));

    masonry.innerHTML = photos.map(function (p, k) {
      var ratio = (p.w && p.h) ? ' style="aspect-ratio:' + p.w + '/' + p.h + '"' : '';
      return '<a class="m-item" href="' + p.file + '" data-i="' + k + '"' + ratio + '>' +
        '<img src="' + p.file + '" alt="' + esc(p.name || album.title) + '" loading="lazy"></a>';
    }).join('');

    // Prev / next album links
    var pnav = document.getElementById('albumNav');
    if (pnav) {
      var prev = albums[(i - 1 + albums.length) % albums.length];
      var next = albums[(i + 1) % albums.length];
      pnav.innerHTML =
        '<a class="prev" href="Album.html?a=' + encodeURIComponent(prev.slug) + '">' +
          '<span class="lbl">← Previous project</span><span class="nm">' + esc(prev.title) + '</span></a>' +
        '<a class="next" href="Album.html?a=' + encodeURIComponent(next.slug) + '">' +
          '<span class="lbl">Next project →</span><span class="nm">' + esc(next.title) + '</span></a>';
    }

    initLightbox(photos);
  }

  function initLightbox(photos) {
    var lb = document.getElementById('lb');
    var img = document.getElementById('lbImg');
    var count = document.getElementById('lbCount');
    if (!lb) return;
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

    masonry.addEventListener('click', function (e) {
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

  function setText(id, txt) { var el = document.getElementById(id); if (el) el.textContent = txt; }
  function esc(s) { return String(s || '').replace(/[&<>"]/g, function (c) {
    return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
})();
