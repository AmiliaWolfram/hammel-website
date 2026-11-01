(() => { const nodes = document.querySelectorAll('.hc-reveal'); if (!nodes.length)
    return; if (!('IntersectionObserver' in window) || matchMedia('(prefers-reduced-motion: reduce)').matches) {
    nodes.forEach(el => el.classList.add('hc-visible'));
    return;
} const observer = new IntersectionObserver(entries => { for (const e of entries)
    if (e.isIntersecting) {
        e.target.classList.add('hc-visible');
        observer.unobserve(e.target);
    } }, { rootMargin: '0px 0px -8% 0px', threshold: .07 }); nodes.forEach(el => observer.observe(el)); })();
