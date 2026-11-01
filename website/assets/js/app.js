const L = { de: { machines: 'MASCHINEN', solutions: 'LÖSUNGEN', service: 'SERVICE', company: 'UNTERNEHMEN', news: 'AKTUELLES', career: 'KARRIERE', contact: 'KONTAKT', hero: 'RECYCLINGTECHNIK AUS THÜRINGEN', lead: 'Leistungsstarke Zerkleinerungs- und Recyclingtechnik für Holz, Abfall, Metall und anspruchsvolle Sonderanwendungen', discover: 'MASCHINEN ENTDECKEN', find: 'LÖSUNG FINDEN', what: 'WAS MÖCHTEN SIE ZERKLEINERN', wood: 'HOLZ', metal: 'METALL', waste: 'ABFALL', special: 'SONDERMATERIALIEN' }, en: { machines: 'MACHINES', solutions: 'SOLUTIONS', service: 'SERVICE', company: 'COMPANY', news: 'NEWS', career: 'CAREERS', contact: 'CONTACT', hero: 'RECYCLING TECHNOLOGY FROM THURINGIA', lead: 'Powerful shredding and recycling technology for wood, waste, metal and demanding special applications', discover: 'EXPLORE MACHINES', find: 'FIND A SOLUTION', what: 'WHAT DO YOU WANT TO SHRED', wood: 'WOOD', metal: 'METAL', waste: 'WASTE', special: 'SPECIAL MATERIALS' }, fr: { machines: 'MACHINES', solutions: 'SOLUTIONS', service: 'SERVICE', company: 'ENTREPRISE', news: 'ACTUALITÉS', career: 'CARRIÈRES', contact: 'CONTACT', hero: 'TECHNOLOGIE DE RECYCLAGE DE THURINGE', lead: 'Technologie puissante de broyage et de recyclage pour le bois, les déchets, le métal et les applications spéciales', discover: 'DÉCOUVRIR LES MACHINES', find: 'TROUVER UNE SOLUTION', what: 'QUE VOULEZ-VOUS BROYER', wood: 'BOIS', metal: 'MÉTAL', waste: 'DÉCHETS', special: 'MATÉRIAUX SPÉCIAUX' }, es: { machines: 'MÁQUINAS', solutions: 'SOLUCIONES', service: 'SERVICIO', company: 'EMPRESA', news: 'ACTUALIDAD', career: 'EMPLEO', contact: 'CONTACTO', hero: 'TECNOLOGÍA DE RECICLAJE DE TURINGIA', lead: 'Potente tecnología de trituración y reciclaje para madera, residuos, metal y aplicaciones especiales', discover: 'DESCUBRIR MÁQUINAS', find: 'ENCONTRAR SOLUCIÓN', what: 'QUÉ QUIERE TRITURAR', wood: 'MADERA', metal: 'METAL', waste: 'RESIDUOS', special: 'MATERIALES ESPECIALES' }, it: { machines: 'MACCHINE', solutions: 'SOLUZIONI', service: 'SERVIZIO', company: 'AZIENDA', news: 'NOVITÀ', career: 'LAVORA CON NOI', contact: 'CONTATTI', hero: 'TECNOLOGIA DI RICICLAGGIO DALLA TURINGIA', lead: 'Potente tecnologia di triturazione e riciclaggio per legno, rifiuti, metallo e applicazioni speciali', discover: 'SCOPRI LE MACCHINE', find: 'TROVA UNA SOLUZIONE', what: 'COSA VUOI TRITURARE', wood: 'LEGNO', metal: 'METALLO', waste: 'RIFIUTI', special: 'MATERIALI SPECIALI' } };
let lang = localStorage.getItem('hammelLang') || 'de';
function apply() { document.documentElement.lang = lang; document.querySelectorAll('[data-i18n]').forEach(e => { let v = L[lang]?.[e.dataset.i18n]; if (v)
    e.textContent = v; }); document.querySelector('#langBtn').textContent = lang.toUpperCase() + ' ▾'; }
document.addEventListener('click', e => { if (e.target.closest('#langBtn'))
    document.querySelector('.lang').classList.toggle('open'); if (e.target.dataset.lang) {
    e.preventDefault();
    lang = e.target.dataset.lang;
    localStorage.setItem('hammelLang', lang);
    apply();
    document.querySelector('.lang').classList.remove('open');
} });
const io = new IntersectionObserver(es => es.forEach(e => e.isIntersecting && e.target.classList.add('show')), { threshold: .12 });
document.querySelectorAll('.reveal').forEach(e => io.observe(e));
apply();
// Choose the logo that contrasts with the section beneath the fixed header.
(function () {
    const header = document.querySelector('.top');
    if (!header)
        return;
    function syncHeader() {
        const y = window.scrollY + Math.min(window.innerHeight * .15, 120);
        let current = null;
        document.querySelectorAll('main section, .subhero, .content').forEach(el => {
            const top = el.getBoundingClientRect().top + window.scrollY;
            if (top <= y)
                current = el;
        });
        header.classList.toggle('on-light', !!current && (current.classList.contains('white') || getComputedStyle(current).backgroundColor === 'rgb(242, 242, 239)'));
    }
    window.addEventListener('scroll', syncHeader, { passive: true });
    window.addEventListener('resize', syncHeader);
    syncHeader();
})();
// Full-width photo crossfade and accessible click-to-expand gallery.
(function () {
    const gallery = document.querySelector('.intro-gallery');
    const modal = document.getElementById('galleryLightbox');
    if (!gallery || !modal)
        return;
    const slides = Array.from(gallery.querySelectorAll('.intro-slide'));
    const large = modal.querySelector('.gallery-large');
    const counter = modal.querySelector('.gallery-count');
    if (!slides.length || !large || !counter)
        return;
    let active = 0, timer = null, lastFocus = null;
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    function show(index) {
        active = (index + slides.length) % slides.length;
        slides.forEach((slide, i) => {
            const selected = i === active;
            slide.classList.toggle('active', selected);
            slide.setAttribute('aria-hidden', String(!selected));
            slide.tabIndex = selected ? 0 : -1;
        });
        if (!modal.hidden)
            updateModal();
    }
    function updateModal() {
        const img = slides[active].querySelector('img');
        large.src = img.currentSrc || img.src;
        large.alt = img.alt;
        counter.textContent = (active + 1) + ' / ' + slides.length;
    }
    function stop() { if (timer !== null) {
        window.clearInterval(timer);
        timer = null;
    } }
    function start() { stop(); if (!reduced && modal.hidden && !document.hidden)
        timer = window.setInterval(() => show(active + 1), 5000); }
    function open(index) { lastFocus = document.activeElement; show(index); modal.hidden = false; document.body.style.overflow = 'hidden'; updateModal(); stop(); modal.querySelector('.gallery-close').focus(); }
    function close() { modal.hidden = true; document.body.style.overflow = ''; start(); if (lastFocus && lastFocus.isConnected)
        lastFocus.focus(); }
    slides.forEach((slide, i) => slide.addEventListener('click', () => open(i)));
    modal.querySelector('.gallery-close').addEventListener('click', close);
    modal.querySelector('.gallery-prev').addEventListener('click', () => show(active - 1));
    modal.querySelector('.gallery-next').addEventListener('click', () => show(active + 1));
    modal.addEventListener('click', e => { if (e.target === modal)
        close(); });
    document.addEventListener('keydown', e => {
        if (modal.hidden)
            return;
        if (e.key === 'Escape')
            close();
        if (e.key === 'ArrowLeft')
            show(active - 1);
        if (e.key === 'ArrowRight')
            show(active + 1);
    });
    document.addEventListener('visibilitychange', start);
    show(0);
    start();
})();
