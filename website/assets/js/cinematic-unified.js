/* Progressive enhancement: content remains readable if JS or observers are unavailable. */
document.addEventListener('DOMContentLoaded', () => {
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduce || !('IntersectionObserver' in window))
        return;
    const scenes = [...document.querySelectorAll('main section.cinematic-scene')];
    const innerCards = [...document.querySelectorAll('main.content .reveal')];
    const cardObserver = new IntersectionObserver(entries => entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.remove('cinema-entering');
            entry.target.classList.add('cinema-entered');
            cardObserver.unobserve(entry.target);
        }
    }), { threshold: .08, rootMargin: '0px 0px -25px 0px' });
    innerCards.forEach((el, i) => {
        el.classList.add('cinema-stage');
        if (el.getBoundingClientRect().top > window.innerHeight * .85) {
            el.classList.add('cinema-entering');
            cardObserver.observe(el);
        }
    });
    const subhero = document.querySelector('.subhero .wrap');
    if (subhero) {
        subhero.classList.add('cinema-stage', 'cinema-entered');
    }
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (!entry.isIntersecting)
                return;
            const scene = entry.target;
            scene.classList.add('cinema-scene-active');
            scene.querySelectorAll('.cinema-stage').forEach(el => {
                el.classList.remove('cinema-entering');
                el.classList.add('cinema-entered');
                el.addEventListener('transitionend', () => { el.style.willChange = 'auto'; }, { once: true });
            });
            observer.unobserve(scene);
        });
    }, { threshold: .075, rootMargin: '0px 0px -55px 0px' });
    scenes.forEach(scene => {
        const rect = scene.getBoundingClientRect();
        const content = scene.querySelector('.wrap') || scene.firstElementChild;
        if (!content)
            return;
        // Keep the existing reveal behavior; avoid competing transforms on .reveal
        const elements = [...content.children].filter(el => !el.matches('script,style'));
        const stages = elements.length > 1 ? elements.slice(0, 5) : [content];
        stages.forEach((el, i) => {
            if (el.classList.contains('reveal'))
                return;
            el.classList.add('cinema-stage', 'cinema-delay-' + Math.min(i, 3));
        });
        if (rect.top < window.innerHeight * .87) {
            scene.classList.add('cinema-scene-active');
            return;
        }
        stages.forEach(el => { if (!el.classList.contains('reveal'))
            el.classList.add('cinema-entering'); });
        observer.observe(scene);
    });
});
