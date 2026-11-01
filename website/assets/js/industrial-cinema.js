document.addEventListener('DOMContentLoaded', () => { if (window.matchMedia('(prefers-reduced-motion: reduce)').matches)
    return; const items = [...document.querySelectorAll('.section .reveal')]; if (!('IntersectionObserver' in window))
    return; const io = new IntersectionObserver(entries => { entries.forEach(entry => { if (entry.isIntersecting) {
    entry.target.classList.remove('cinema-hidden');
    entry.target.classList.add('cinema-visible');
    io.unobserve(entry.target);
} }); }, { threshold: .08, rootMargin: '0px 0px -35px 0px' }); items.forEach(el => { const r = el.getBoundingClientRect(); if (r.top < window.innerHeight * .9)
    return; el.classList.add('cinema-hidden'); io.observe(el); }); });
