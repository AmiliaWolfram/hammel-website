document.addEventListener('DOMContentLoaded', () => { const story = document.querySelector('.story'); if (!story)
    return; const cues = [...story.querySelectorAll('.story__next')]; if (!('IntersectionObserver' in window) || matchMedia('(prefers-reduced-motion: reduce)').matches) {
    cues.forEach(x => x.classList.add('story__visible'));
    return;
} const io = new IntersectionObserver(entries => { entries.forEach(e => { if (e.isIntersecting) {
    e.target.classList.add('story__visible');
    io.unobserve(e.target);
} }); }, { threshold: .15 }); cues.forEach(x => io.observe(x)); });
