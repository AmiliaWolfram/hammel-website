document.addEventListener('DOMContentLoaded', () => {
    const videos = [...document.querySelectorAll('[data-material-video]')];
    if (!videos.length)
        return;
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduced)
        return;
    const observer = new IntersectionObserver(entries => {
        for (const entry of entries) {
            const video = entry.target;
            if (entry.isIntersecting && !document.hidden) {
                video.play().catch(() => { });
            }
            else {
                video.pause();
            }
        }
    }, { threshold: 0.15, rootMargin: '100px 0px' });
    videos.forEach(v => observer.observe(v));
    document.addEventListener('visibilitychange', () => {
        if (document.hidden)
            videos.forEach(v => v.pause());
        else
            videos.forEach(v => { const r = v.getBoundingClientRect(); if (r.top < innerHeight && r.bottom > 0)
                v.play().catch(() => { }); });
    });
});
