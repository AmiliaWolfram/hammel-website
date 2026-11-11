/* HR editor enhancement: progressive sections and safe draft autosave. */
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('hr-de-form');
  if (!form || !document.getElementById('hr-builder')) return;
  const status = document.getElementById('hr-save-status');
  const groups = [
    ['STELLENDATEN', 'Titel, Art der Stelle, Abteilung und Arbeitsort', ['title','category','department','location','employment_type']],
    ['EINLEITUNG', 'Kurze Beschreibung der Stelle', ['introduction']],
    ['WEITERE ANFORDERUNGEN', 'Zusätzliche Hinweise', ['requirements']]
  ];
  const first = form.querySelector('.staff-field');
  if (first) {
    const nav = document.createElement('nav'); nav.className = 'hr-section-links'; nav.setAttribute('aria-label','Abschnitte der deutschen Stellenanzeige');
    groups.forEach(([title, , names], index) => {
      const section = document.createElement('section'); section.className = 'hr-form-section'; section.id = 'hr-section-' + index;
      const header = document.createElement('div'); header.className = 'hr-form-section-head';
      const h = document.createElement('h2'); h.textContent = title; header.append(h);
      const hint = document.createElement('p'); hint.textContent = groups[index][1]; header.append(hint); section.append(header);
      const items = names.map(name => form.querySelector('[name="'+name+'"]')?.closest('.staff-field')).filter(Boolean);
      if (!items.length) return;
      form.insertBefore(section, document.getElementById('hr-builder'));
      items.forEach(item => section.append(item));
      const link = document.createElement('a'); link.href = '#' + section.id; link.textContent = title; nav.append(link);
    });
    const builder = document.getElementById('hr-builder');
    const link = document.createElement('a'); link.href='#hr-builder'; link.textContent='STELLENBAUKASTEN'; nav.append(link);
    form.insertBefore(nav, form.firstChild.nextSibling);
  }
  const url = form.dataset.autosaveUrl;
  if (!url) return;
  let timer = null, inFlight = false, pending = false, lastSaved = '';
  const csrf = form.querySelector('[name="csrfmiddlewaretoken"]')?.value;
  const serialize = () => new URLSearchParams(new FormData(form)).toString();
  lastSaved = serialize();
  async function save() {
    if (inFlight) { pending = true; return; }
    const data = serialize(); if (data === lastSaved) return;
    inFlight = true; status.textContent='Entwurf wird gespeichert …';
    try {
      const response = await fetch(url, {method:'POST', body:new URLSearchParams(data), credentials:'same-origin', headers:{'X-CSRFToken':csrf,'X-Requested-With':'XMLHttpRequest'}});
      const result = await response.json();
      if (!response.ok || !result.ok) throw new Error(result.message || 'Bitte Eingaben prüfen und manuell speichern');
      lastSaved = data; status.textContent='Entwurf gespeichert / '+result.saved_at;
    } catch (error) { status.textContent='Nicht automatisch gespeichert / '+error.message; }
    finally { inFlight=false; if (pending || serialize()!==lastSaved) { pending=false; clearTimeout(timer); timer=setTimeout(save,2500); } }
  }
  const changed = () => { status.textContent='Ungespeicherte Änderungen'; clearTimeout(timer); timer=setTimeout(save,1800); };
  form.addEventListener('input',changed); form.addEventListener('change',changed);
  document.querySelectorAll('.hr-builder-option input').forEach(el=>el.addEventListener('change',()=>setTimeout(changed,50)));
  form.addEventListener('submit',()=>clearTimeout(timer));
});
