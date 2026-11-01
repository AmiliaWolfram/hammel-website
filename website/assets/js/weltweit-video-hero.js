document.addEventListener('DOMContentLoaded', () => { const hero = document.querySelector('.cosmic-hero--video'); const btn = document.getElementById('cosmic-enter'); const vid = hero?.querySelector('video'); if (!hero || !btn)
    return; btn.addEventListener('click', () => { const active = hero.classList.toggle('is-interactive'); btn.setAttribute('aria-expanded', String(active)); btn.innerHTML = '<span class="weltweit-link__circle" aria-hidden="true">' + (active ? '↙' : '↗') + '</span> ' + (active ? 'VIDEO ANSEHEN' : 'NETZWERK ENTDECKEN'); if (active) {
    vid?.pause();
}
else {
    vid?.play().catch(() => { });
} }); });
