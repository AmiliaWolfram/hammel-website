document.addEventListener('DOMContentLoaded', () => { const title = document.querySelector('.shred-title'); if (!title)
    return; const start = () => requestAnimationFrame(() => title.classList.add('is-ready')); if (document.fonts && document.fonts.ready) {
    Promise.race([document.fonts.ready, new Promise(resolve => setTimeout(resolve, 1800))]).then(start);
}
else
    start(); });
