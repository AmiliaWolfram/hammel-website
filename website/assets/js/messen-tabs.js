/* Independent HAMMEL Messe navigation: always works, even without API/gallery data. */
(() => {
  'use strict';
  // Shared eased scroll: gentle acceleration and deceleration, with cancellation.
  window.hammelMessenScroll = window.hammelMessenScroll || (() => {
    let frame = 0;
    return (target, duration = 1050) => {
      cancelAnimationFrame(frame);
      const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      const start = window.scrollY;
      const end = Math.max(0, Math.min(target, document.documentElement.scrollHeight - window.innerHeight));
      if (reduced || Math.abs(end-start)<2) { window.scrollTo(0,end); return 0; }
      const begin = performance.now();
      const ease = t => t<0.5 ? 4*t*t*t : 1-Math.pow(-2*t+2,3)/2;
      const tick = now => {
        const t = Math.min(1,(now-begin)/duration);
        window.scrollTo(0,start+(end-start)*ease(t));
        if(t<1) frame=requestAnimationFrame(tick);
      };
      frame=requestAnimationFrame(tick);
      return duration;
    };
  })();
  function init() {
    const tabs = Array.from(document.querySelectorAll('[data-messe-tab]'));
    const upcoming = document.getElementById('mf-upcoming-panel');
    const past = document.getElementById('mf-past-panel');
    const detailSection = document.getElementById('mf-detail-standalone');
    if (!tabs.length || !upcoming || !past) return;
    const activate = name => {
      if (name !== 'upcoming' && name !== 'past') return;
      document.querySelectorAll('[data-messe-heading]').forEach(h => { h.hidden = h.dataset.messeHeading !== name; });
      upcoming.hidden = name !== 'upcoming';
      past.hidden = name !== 'past';
      if (detailSection) detailSection.hidden = name !== 'past' || !detailSection.dataset.hasEvent;
      tabs.forEach(tab => {
        const selected = tab.dataset.messeTab === name;
        tab.classList.toggle('is-active', selected);
        tab.setAttribute('aria-pressed', String(selected));
        tab.setAttribute('aria-selected', String(selected));
      });
    };
    tabs.forEach(tab => tab.addEventListener('click', () => {
      const name = tab.dataset.messeTab;
      if (tab.classList.contains('is-active')) return;
      // Capture the target before hiding the taller panel (which otherwise clamps scroll instantly).
      const section = tab.closest('.messe-home-section') || tab.closest('section');
      const heading = section?.querySelector('.mf-section-heading');
      const target = heading || section || tab;
      const offset = window.innerWidth < 768 ? 86 : 110;
      const targetY = Math.max(0, window.scrollY + target.getBoundingClientRect().top - offset);
      const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      // Preserve page height while the old panel is replaced, avoiding a sudden browser scroll clamp.
      const oldHeight = section?.getBoundingClientRect().height || 0;
      if (section) section.style.minHeight = oldHeight + 'px';
      // Close every year when changing between upcoming and past exhibitions.
      document.querySelectorAll('#mf-upcoming-panel .my-year-toggle').forEach(heading => {
        if(heading.querySelector('.my-year-number')?.textContent.trim()===String(new Date().getFullYear())) return;
        heading.setAttribute('aria-expanded','false');
        const panel=document.getElementById(heading.getAttribute('aria-controls'));
        if(panel) panel.hidden=true;
      });
      activate(name);
      requestAnimationFrame(() => {
        const duration = window.hammelMessenScroll(targetY, 1150);
        // Release reserved height only after the smooth scroll has finished.
        window.setTimeout(() => {if(section) section.style.minHeight='';}, reduce?0:1350);
      });
    }));
    activate(location.hash === '#vergangene-messen' ? 'past' : 'upcoming');
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, {once:true});
  else init();
})();
