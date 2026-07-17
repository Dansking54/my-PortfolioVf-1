/* ===== Dan's Logs — shared project data + renderers ===== */
window.PROJECTS = [
  {
    slug: 'golden-hour', n: '01', title: 'Golden Hour', cat: 'Street', year: '2025',
    cover: '../assets/hero-goldenhour.jpg', pos: 'center 60%',
    blurb: 'Chasing the last warm light across Montréal — overpasses, parking lots, and the Biosphère glowing on the skyline.',
    media: [
      { t: 'img', src: '../assets/hero-goldenhour.jpg', span: 2 },
      { t: 'img', src: '../assets/golden-hour.jpg' },
      { t: 'img', src: '../assets/goldenhour-biosphere.jpg' },
      { t: 'img', src: '../assets/sunset-biosphere.jpg' },
      { t: 'slot', id: 'gh1' },
      { t: 'slot', id: 'gh2' },
    ],
  },
  {
    slug: 'fog-city', n: '02', title: 'Fog City', cat: 'Street', year: '2024',
    cover: '../assets/fog-city.jpg', pos: 'center',
    blurb: 'Montréal swallowed by low cloud — towers fading into grey, highway signage glowing through the haze.',
    media: [
      { t: 'img', src: '../assets/fog-city.jpg', span: 2 },
      { t: 'img', src: '../assets/fog-montreal.jpg' },
      { t: 'slot', id: 'fc1' },
      { t: 'slot', id: 'fc2' },
      { t: 'slot', id: 'fc3' },
    ],
  },
  {
    slug: 'be-cinematic', n: '03', title: 'Be Cinematic', cat: 'Film', year: '2025',
    cover: '../assets/be-cinematic.jpg', pos: '60% center',
    blurb: 'A short film study — anamorphic frames, slow light, and a city that never quite sleeps.',
    media: [
      { t: 'video', src: '../assets/be-cinematic.jpg', href: 'https://www.youtube.com/@Dans_Logs' },
      { t: 'img', src: '../assets/day3.jpg' },
      { t: 'slot', id: 'bc1' },
      { t: 'slot', id: 'bc2' },
    ],
  },
  {
    slug: 'concrete-color', n: '04', title: 'Concrete & Color', cat: 'Street', year: '2024',
    cover: '../assets/graffiti.jpg', pos: 'center',
    blurb: 'Walls as canvas — spray, rust, and the accidental palettes hiding under the city overpasses.',
    media: [
      { t: 'img', src: '../assets/graffiti.jpg', span: 2 },
      { t: 'img', src: '../assets/graffiti-bw.jpg' },
      { t: 'slot', id: 'cc1' },
      { t: 'slot', id: 'cc2' },
    ],
  },
  {
    slug: 'blue-hour', n: '05', title: 'Blue Hour', cat: 'Street', year: '2024',
    cover: '../assets/fog-montreal.jpg', pos: 'center',
    blurb: 'The cold few minutes after sunset — concrete turning to steel, headlights warming up the frame.',
    media: [
      { t: 'img', src: '../assets/fog-montreal.jpg', span: 2 },
      { t: 'slot', id: 'bh1' },
      { t: 'slot', id: 'bh2' },
      { t: 'slot', id: 'bh3' },
    ],
  },
  {
    slug: 'day-three', n: '06', title: 'Day Three', cat: 'Documentary', year: '2023',
    cover: '../assets/day3.jpg', pos: 'center',
    blurb: 'A three-day visual diary — faces, streets, and the in-between moments that make a place feel like home.',
    media: [
      { t: 'img', src: '../assets/day3.jpg', span: 2 },
      { t: 'img', src: '../assets/golden-hour.jpg' },
      { t: 'slot', id: 'd31' },
      { t: 'slot', id: 'd32' },
    ],
  },
];

/* Render the cover grid (Home) */
window.renderWorkGrid = function (mount) {
  if (!mount) return;
  mount.innerHTML = window.PROJECTS.map(function (p) {
    return '' +
      '<a class="proj" href="Project.html?p=' + p.slug + '">' +
      '  <div class="proj-ph"><img src="' + p.cover + '" alt="' + p.title + '" loading="lazy" style="object-position:' + (p.pos || 'center') + '"></div>' +
      '  <div class="proj-meta">' +
      '    <span class="pn">' + p.n + '</span>' +
      '    <span class="pt">' + p.title + '</span>' +
      '    <span class="pc">' + p.cat + ' · ' + p.year + '</span>' +
      '    <span class="par">↗</span>' +
      '  </div>' +
      '</a>';
  }).join('');
};

/* Render the detail page (Project.html) */
window.renderProjectPage = function () {
  var qs = new URLSearchParams(location.search);
  var slug = qs.get('p');
  var i = window.PROJECTS.findIndex(function (x) { return x.slug === slug; });
  if (i < 0) i = 0;
  var p = window.PROJECTS[i];

  document.title = p.title + " — Dan's Logs";
  var set = function (id, txt) { var el = document.getElementById(id); if (el) el.textContent = txt; };
  var img = document.getElementById('pheroImg');
  if (img) { img.src = p.cover; img.style.objectPosition = p.pos || 'center'; }
  set('pNum', p.n);
  set('pTitle', p.title);
  set('pCat', p.cat + ' · ' + p.year + ' · Montréal');
  set('pBlurb', p.blurb);

  var gallery = document.getElementById('gallery');
  if (gallery) {
    gallery.innerHTML = p.media.map(function (m) {
      if (m.t === 'img') {
        return '<figure class="g-item' + (m.span === 2 ? ' wide' : '') + '"><img src="' + m.src + '" alt="' + p.title + '" loading="lazy"></figure>';
      }
      if (m.t === 'video') {
        return '<figure class="g-item wide vid"><a href="' + m.href + '" target="_blank" rel="noopener">' +
          '<img src="' + m.src + '" alt="' + p.title + ' reel" loading="lazy">' +
          '<span class="play">▶</span><span class="vlbl">Watch the reel</span></a></figure>';
      }
      return '<figure class="g-item slot"><image-slot id="' + p.slug + '-' + m.id + '" placeholder="Drop a ' + p.title + ' frame"></image-slot></figure>';
    }).join('');
  }

  var prev = window.PROJECTS[(i - 1 + window.PROJECTS.length) % window.PROJECTS.length];
  var next = window.PROJECTS[(i + 1) % window.PROJECTS.length];
  var pnav = document.getElementById('pnav');
  if (pnav) {
    pnav.innerHTML =
      '<a class="prev" href="Project.html?p=' + prev.slug + '"><span class="lbl">← Previous</span><span class="nm">' + prev.title + '</span></a>' +
      '<a class="next" href="Project.html?p=' + next.slug + '"><span class="lbl">Next →</span><span class="nm">' + next.title + '</span></a>';
  }
};
