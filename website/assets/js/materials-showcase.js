// EINSATZBEREICHE: accessible tabs with one active video at a time.
document.addEventListener('DOMContentLoaded', () => {
  const section = document.querySelector('.materials-showcase');
  if (!section) return;

  const tabs = Array.from(section.querySelectorAll('[data-material-tab]'));
  const panels = Array.from(section.querySelectorAll('[data-material-panel]'));
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let visible = false;

  function updatePlayback() {
    panels.forEach(panel => {
      const video = panel.querySelector('video');
      if (!video) return;
      if (panel.classList.contains('is-active') && visible && !document.hidden && !prefersReducedMotion) {
        video.play().catch(() => {});
      } else {
        video.pause();
      }
    });
  }

  function selectMaterial(key, focus = false) {
    tabs.forEach(tab => {
      const active = tab.dataset.materialTab === key;
      tab.classList.toggle('is-active', active);
      tab.setAttribute('aria-selected', String(active));
      tab.tabIndex = active ? 0 : -1;
      if (active && focus) tab.focus();
    });
    panels.forEach(panel => {
      const active = panel.dataset.materialPanel === key;
      panel.classList.toggle('is-active', active);
      panel.hidden = !active;
      if (active) {
        const video = panel.querySelector('video');
        if (video && video.readyState === 0) video.load();
      }
    });
    updatePlayback();
  }

  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => selectMaterial(tab.dataset.materialTab));
    tab.addEventListener('keydown', event => {
      if (!['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Home', 'End'].includes(event.key)) return;
      event.preventDefault();
      const next = event.key === 'Home' ? 0 : event.key === 'End' ? tabs.length - 1 :
        (index + (['ArrowRight', 'ArrowDown'].includes(event.key) ? 1 : -1) + tabs.length) % tabs.length;
      selectMaterial(tabs[next].dataset.materialTab, true);
    });
  });

  const observer = new IntersectionObserver(entries => {
    visible = entries[0].isIntersecting;
    updatePlayback();
  }, { threshold: 0.12 });
  observer.observe(section);
  document.addEventListener('visibilitychange', updatePlayback);
  selectMaterial('metall');
});
