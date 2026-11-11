/* Phase 37: one-field-at-a-time autosave, never publishes a translation. */
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('translation-form');
  if (!form || !form.dataset.autosaveUrl) return;
  const indicator = document.getElementById('save-indicator');
  const footer = document.getElementById('footer-save-indicator');
  const csrf = form.querySelector('[name=csrfmiddlewaretoken]')?.value;
  const fields = [...form.querySelectorAll('textarea[name^="translation_"]')];
  const saved = new Map(fields.map(el => [el.name, el.value]));
  const pending = new Set();
  const timers = new Map();
  const active = new Map();
  let leaving = false;
  let manualSubmit = false;
  const update = (message) => {
    if (!indicator) return;
    indicator.textContent = message || (pending.size ? 'Ungespeicherte Änderungen' : 'Alle Texte gespeichert');
    if (footer) footer.textContent = pending.size ? 'Änderungen werden automatisch als Entwurf gespeichert.' : '';
    window.hrTranslationAutosaveSafe = pending.size === 0;
  };
  async function save(el) {
    const name = el.name;
    clearTimeout(timers.get(name));
    if (active.has(name)) return active.get(name);
    if (saved.get(name) === el.value) { pending.delete(name); update(); return; }
    const text = el.value;
    const body = new URLSearchParams({language: form.dataset.language, field: name.slice(12), text});
    update('Entwurf wird gespeichert …');
    const promise = (async () => {
      try {
        const response = await fetch(form.dataset.autosaveUrl, {
          method: 'POST', credentials: 'same-origin', body,
          headers: {'X-CSRFToken': csrf, 'X-Requested-With': 'XMLHttpRequest'}
        });
        const result = await response.json();
        if (!response.ok || !result.ok) throw new Error(result.message || 'Speichern fehlgeschlagen');
        saved.set(name, text);
        if (el.value === text) pending.delete(name);
        update('Gespeichert / ' + result.saved_at);
      } catch (err) {
        pending.add(name);
        update('Nicht gespeichert – bitte Verbindung prüfen oder SPRACHVERSION SPEICHERN verwenden');
      } finally {
        active.delete(name);
        if (el.value !== saved.get(name) && !leaving) {
          pending.add(name);
          timers.set(name, setTimeout(() => save(el), 1200));
        }
      }
    })();
    active.set(name, promise);
    return promise;
  }
  fields.forEach(el => el.addEventListener('input', () => {
    if (el.value === saved.get(el.name)) pending.delete(el.name);
    else pending.add(el.name);
    update(); clearTimeout(timers.get(el.name));
    timers.set(el.name, setTimeout(() => save(el), 1100));
  }));
  // Switching language or proceeding to review must not drop a pending keystroke.
  document.querySelectorAll('.language-tabs a, a[href*="step=review"], #translation-back').forEach(link => {
    link.addEventListener('click', async event => {
      if (manualSubmit || !pending.size) return;
      event.preventDefault();
      if (leaving) return;
      leaving = true;
      for (const el of fields) if (pending.has(el.name)) await save(el);
      if (pending.size) {
        leaving = false;
        update('Speichern fehlgeschlagen. Bitte erneut versuchen, bevor Sie die Seite verlassen.');
        return;
      }
      window.hrTranslationAutosaveSafe = true;
      location.assign(link.href);
    });
  });
  form.addEventListener('submit', () => { manualSubmit = true; });
  window.addEventListener('beforeunload', event => {
    if (!manualSubmit && pending.size) { event.preventDefault(); event.returnValue = ''; }
  });
  update();
});
