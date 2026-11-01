/* Small, progressive enhancements. No external animation library required. */
(() => { const boot = () => { const chapters = document.querySelectorAll('.hc-journey>.hc-chapter'); if (!chapters.length)
    return; const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches; if (reduce || !('IntersectionObserver' in window))
    return; const io = new IntersectionObserver(entries => { for (const entry of entries) {
    if (entry.isIntersecting) {
        entry.target.classList.add('hc-editorial-in');
        io.unobserve(entry.target);
    }
} }, { rootMargin: '0px 0px -8% 0px', threshold: .12 }); chapters.forEach(ch => io.observe(ch)); }; document.readyState === 'loading' ? document.addEventListener('DOMContentLoaded', boot) : boot(); })();
