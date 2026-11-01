/* Scroll-triggered content animation; sharp chapter backgrounds remain untouched. */
(() => { function init() { const root = document.querySelector('.story'); if (!root)
    return; if (window.matchMedia('(prefers-reduced-motion: reduce)').matches)
    return; root.classList.add('story--scroll'); const chapters = [...root.querySelectorAll('.story__chapter')]; let scheduled = false; function update() { scheduled = false; const vh = window.innerHeight || 900; for (const chapter of chapters) {
    const rect = chapter.getBoundingClientRect();
    if (rect.bottom < 0 || rect.top > vh)
        continue;
    const photo = chapter.querySelector('.story__photo');
    if (!photo)
        continue;
    const midpoint = rect.top + rect.height / 2;
    const amount = Math.max(-12, Math.min(12, (vh / 2 - midpoint) * .018));
    photo.style.setProperty('--story-parallax', amount.toFixed(1) + 'px');
} } function schedule() { if (!scheduled) {
    scheduled = true;
    requestAnimationFrame(update);
} } window.addEventListener('scroll', schedule, { passive: true }); window.addEventListener('resize', schedule, { passive: true }); update(); } if (document.readyState === 'loading')
    document.addEventListener('DOMContentLoaded', init, { once: true });
else
    init(); })();
