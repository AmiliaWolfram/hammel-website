document.addEventListener('DOMContentLoaded', () => { const video = document.querySelector('.engineering-film'); if (!video)
    return; if (matchMedia('(prefers-reduced-motion: reduce)').matches)
    return; const observer = new IntersectionObserver(entries => { for (const entry of entries) {
    if (entry.isIntersecting && !document.hidden) {
        video.play().catch(() => { });
    }
    else
        video.pause();
} }, { threshold: .2 }); observer.observe(video); document.addEventListener('visibilitychange', () => { if (document.hidden)
    video.pause();
else if (video.getBoundingClientRect().top < innerHeight && video.getBoundingClientRect().bottom > 0)
    video.play().catch(() => { }); }); });
