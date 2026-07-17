/* Dan — shared site behavior */
(function () {
  // Header blur on scroll
  var header = document.querySelector('header.site');
  function onScroll() {
    if (!header) return;
    if (window.scrollY > 24) { header.classList.add('scrolled'); }
    else { header.classList.remove('scrolled'); }
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // Active nav link
  var path = location.pathname.split('/').pop() || 'Home.html';
  document.querySelectorAll('header.site nav a').forEach(function (a) {
    var href = a.getAttribute('href') || '';
    if (href.split('?')[0] === decodeURIComponent(path)) { a.classList.add('active'); }
  });

  // Reveal on scroll
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
    });
  }, { threshold: 0.12 });
  document.querySelectorAll('.rv').forEach(function (el) { io.observe(el); });
})();
