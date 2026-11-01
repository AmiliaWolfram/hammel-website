document.addEventListener('DOMContentLoaded', () => { const root = document.querySelector('.story'); if (!root)
    return; if (!('IntersectionObserver' in window) || matchMedia('(prefers-reduced-motion: reduce)').matches)
    return; const targets = [...root.querySelectorAll('.story__reveal')]; const observer = new IntersectionObserver((entries) => { for (const entry of entries) {
    if (entry.isIntersecting) {
        entry.target.classList.add('story__visible');
        observer.unobserve(entry.target);
    }
} }, { threshold: .08, rootMargin: '0px 0px 45px 0px' }); root.classList.add('story--js'); targets.forEach(el => observer.observe(el)); });
