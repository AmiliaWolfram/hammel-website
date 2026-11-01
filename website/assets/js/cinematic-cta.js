/* Match the red line to the real visible right edge of SHRED, including horizontal scaling. */
(function () {
    const title = document.querySelector('.shred-title');
    const word = title?.querySelector('.shred-line--shred .shred-ink');
    if (!title || !word)
        return;
    let raf = 0;
    function measure() {
        cancelAnimationFrame(raf);
        raf = requestAnimationFrame(() => {
            const start = title.getBoundingClientRect().left;
            const end = word.getBoundingClientRect().right;
            title.style.setProperty('--shred-rule-width', Math.max(0, Math.round(end - start)) + 'px');
        });
    }
    window.addEventListener('resize', measure, { passive: true });
    window.addEventListener('load', measure, { once: true });
    if (document.fonts?.ready)
        document.fonts.ready.then(measure);
    new ResizeObserver(measure).observe(title);
    measure();
})();
