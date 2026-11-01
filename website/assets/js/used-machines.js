(async function () {
  const grid = document.getElementById('used-grid');
  if (!grid) return;
  const count = document.getElementById('used-count');
  const details = document.getElementById('used-machine-details');
  const fallback = '/assets/img/machines/vb750.webp';
  function node(tag, className, value) { const e=document.createElement(tag); if(className)e.className=className; if(value!==undefined)e.textContent=value; return e; }
  function show(machine, card) {
    grid.querySelectorAll('.used-card').forEach(e=>{e.classList.toggle('is-active',e===card);e.setAttribute('aria-expanded',String(e===card));});
    details.replaceChildren();
    const layout=node('div','used-expanded-layout');
    const visual=node('div','used-expanded-visual');
    const img=node('img');img.src=machine.image||fallback;img.alt=machine.title;img.loading='lazy';visual.append(img);
    if(machine.photos?.length){const gallery=node('div','used-expanded-gallery');machine.photos.forEach(p=>{const thumb=node('img');thumb.src=p.image;thumb.alt=p.caption||machine.title;thumb.loading='lazy';gallery.append(thumb)});visual.append(gallery)}
    const body=node('div','used-expanded-content');body.append(node('span','used-kicker','HAMMEL USED EQUIPMENT'),node('h3','',machine.title));
    const dl=node('dl','used-specs');
    const month=machine.build_month?String(machine.build_month).padStart(2,'0')+'/':'';
    const specs=[['Maschinennummer',machine.serial_number],['Baujahr',machine.build_year?month+machine.build_year:''],['Betriebsstunden',machine.operating_hours],['Motor',machine.engine],['Leistung',machine.power],['Wellen',machine.shafts],['Zustand',machine.condition],['Ausstattung',machine.equipment],['Gewicht',machine.weight]];
    specs.forEach(([label,value])=>{if(!value)return;dl.append(node('dt','',label),node('dd','',value))});body.append(dl);
    if(machine.description)body.append(node('p','used-disclaimer',machine.description));
    const actions=node('div','used-expanded-actions');const inquiry=node('a','used-primary','MASCHINE ANFRAGEN ↗');inquiry.href='/kontakt/index.html';actions.append(inquiry);
    const permalink=node('a','used-detail-link','DETAILSEITE ÖFFNEN ↗');permalink.href=machine.url;actions.append(permalink);
    if(machine.video_url){const video=node('a','used-detail-link','VIDEO ANSEHEN ↗');video.href=machine.video_url;video.target='_blank';video.rel='noopener noreferrer';actions.append(video)}
    body.append(actions);layout.append(visual,body);details.append(layout);details.hidden=false;
    details.scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth',block:'start'});
  }
  try {
    const response=await fetch('/api/gebrauchtmaschinen/',{credentials:'same-origin'});
    if(!response.ok)throw Error('HTTP '+response.status);
    const machines=await response.json();count.textContent=machines.length+' MASCHINEN';grid.replaceChildren();
    if(!machines.length){grid.append(node('p','used-empty','Aktuell sind keine Maschinen veröffentlicht. Fragen Sie unser Team nach verfügbaren Modellen.'));return;}
    machines.forEach(machine=>{
      const card=node('button','used-card');card.type='button';card.setAttribute('aria-expanded','false');card.setAttribute('aria-controls','used-machine-details');
      const image=node('img');image.loading='lazy';image.alt=machine.title;image.src=machine.image||fallback;
      const content=node('div','used-card-body');content.append(node('span','used-kicker','HAMMEL USED EQUIPMENT'),node('h3','',machine.title),node('p','',machine.build_year?'BAUJAHR '+machine.build_year:''),node('strong','','DETAILS ANSEHEN ↗'));
      card.append(image,content);card.addEventListener('click',()=>show(machine,card));grid.append(card);
    });
  } catch(err) {grid.replaceChildren(node('p','used-empty','Die Maschinen konnten gerade nicht geladen werden. Bitte versuchen Sie es später erneut.'));console.error(err)}
})();
