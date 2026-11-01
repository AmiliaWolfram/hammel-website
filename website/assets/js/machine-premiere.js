document.addEventListener('DOMContentLoaded', () => {
    const tabs = [...document.querySelectorAll('.cinema-tab')];
    const panels = [...document.querySelectorAll('.cinema-panel')];
    if (!tabs.length)
        return;
    function activate(i, focus = false) { tabs.forEach((t, j) => { let active = i === j; t.classList.toggle('is-active', active); t.setAttribute('aria-selected', String(active)); t.tabIndex = active ? 0 : -1; }); panels.forEach((p, j) => { const active = i === j; if (active) {
        p.hidden = false;
        requestAnimationFrame(() => p.classList.add('is-active'));
    }
    else {
        p.classList.remove('is-active');
        p.hidden = true;
    } }); if (focus)
        tabs[i].focus(); }
    tabs.forEach((tab, i) => { tab.addEventListener('click', () => activate(i)); tab.addEventListener('keydown', e => { let next = e.key === 'ArrowRight' ? (i + 1) % tabs.length : e.key === 'ArrowLeft' ? (i + tabs.length - 1) % tabs.length : e.key === 'Home' ? 0 : e.key === 'End' ? tabs.length - 1 : -1; if (next >= 0) {
        e.preventDefault();
        activate(next, true);
    } }); });
});
