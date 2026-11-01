(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const upcoming = $('messe-upcoming'), stage = $('mf-folder-stage'), detail = $('mf-event-detail');
  if (!upcoming || !stage || !detail) return;
  const create = (tag, className, text) => { const n=document.createElement(tag); if(className)n.className=className; if(text!==undefined)n.textContent=text; return n; };
  const validPhoto = url => typeof url==='string' && url.startsWith('/media/messen/') ? url : null;
  const safeURL = url => { try { const u=new URL(url,location.href); return ['http:','https:'].includes(u.protocol)?u.href:null; } catch {return null;} };
  const date = value => new Intl.DateTimeFormat('de-DE',{day:'2-digit',month:'short',year:'numeric',timeZone:'UTC'}).format(new Date(value+'T12:00:00Z'));
  const dates = e => e.start_date===e.end_date ? date(e.start_date) : `${date(e.start_date)} — ${date(e.end_date)}`;
  const place = e => [e.city,e.country].filter(Boolean).join(' · ');
  const image = (url,alt) => { const i=create('img');i.src=url;i.alt=alt;i.loading='lazy';return i; };
  const photoList = e => {
    const photos=(Array.isArray(e.photos)?e.photos:[]).filter(p=>validPhoto(p.image));
    if (!photos.length && validPhoto(e.image)) photos.push({image:e.image,caption:''});
    return photos;
  };
  const homeLink = (url,label) => {const href=safeURL(url);if(!href)return null;const a=create('a','mf-link cinematic-link');a.href=href;a.target='_blank';a.rel='noopener noreferrer';const circle=create('span','mf-link__circle cinematic-link__icon');circle.innerHTML='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 19 19 5M7 5h12v12"/></svg>';a.append(circle,create('span','cinematic-link__label',label));return a;};
  let past=[], current=0;
  function renderUpcoming(events){
    upcoming.replaceChildren();
    if(!events.length){upcoming.append(create('p','mf-empty','Unsere nächsten Messetermine werden in Kürze veröffentlicht.'));return;}
    const byYear=new Map();
    events.forEach(e=>{const year=e.start_date.slice(0,4);if(!byYear.has(year))byYear.set(year,[]);byYear.get(year).push(e);});
    byYear.forEach((items,year)=>{
      const section=create('section','my-year-section');
      const head=create('button','my-year-heading my-year-toggle');
      head.type='button';
      const isOpen=year===String(new Date().getFullYear());
      head.setAttribute('aria-expanded',String(isOpen));
      const grid=create('div','my-year-content');
      grid.id='my-year-content-'+year;
      grid.hidden=!isOpen;
      head.setAttribute('aria-controls',grid.id);
      if(isOpen){head.setAttribute('aria-disabled','true');head.title='Das aktuelle Jahr bleibt geöffnet';}
      head.append(create('span','my-year-number',year),create('span','my-year-rule'),create('span','my-year-count',items.length+' '+(items.length===1?'MESSE':'MESSEN')),create('span','my-year-chevron'));
      head.addEventListener('click',()=>{
        if(year===String(new Date().getFullYear())) return; // Current year stays expanded.
        const open=head.getAttribute('aria-expanded')!=='true';
        const offset=window.innerWidth<768?90:130;
        const reduce=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        // Keep enough document height during collapse to prevent instant scroll clamping.
        const container=upcoming.closest('.messe-home-section') || upcoming.closest('section');
        const previous=section.previousElementSibling?.querySelector('.my-year-heading');
        const destination=open ? head : (previous || head);
        const targetY=Math.max(0,window.scrollY+destination.getBoundingClientRect().top-offset);
        const oldHeight=container?.getBoundingClientRect().height || 0;
        if(!open && container) container.style.minHeight=oldHeight+'px';
        head.setAttribute('aria-expanded',String(open));
        grid.hidden=!open;
        window.requestAnimationFrame(()=>{
          if(window.hammelMessenScroll) window.hammelMessenScroll(targetY,1100);
          else window.scrollTo({top:targetY,behavior:reduce?'instant':'smooth'});
          if(!open && container) window.setTimeout(()=>{container.style.minHeight='';},reduce?0:1250);
        });
      });
      section.append(head);
      const cards=create('div','my-events-grid');
      items.forEach(e=>{
        const card=create('article','my-event-card');
        const top=create('div','my-event-top');
        top.append(create('p','my-event-date',dates(e)),create('h4','my-event-title',e.title));
        card.append(top);
        const visual=create('div','my-event-visual');
        const cover=validPhoto(e.image)||photoList(e)[0]?.image;
        if(cover){visual.append(image(cover,e.title));}
        else {const placeholder=create('div','my-event-placeholder');placeholder.append(create('span','my-placeholder-brand','HAMMEL'),create('span','my-placeholder-sub','RECYCLINGTECHNIK'),create('span','my-placeholder-mark','H'));visual.append(placeholder);}
        card.append(visual);
        const body=create('div','my-event-body');
        const loc=create('p','my-event-meta');loc.append(create('span','my-event-meta-icon','⌖'),create('span','',place(e)));body.append(loc);
        if(e.booth){const booth=create('p','my-event-meta');booth.append(create('span','my-event-meta-icon','▦'),create('span','',e.booth));body.append(booth);}
        if(e.description)body.append(create('p','my-event-description',e.description));
        const link=homeLink(e.url,'MESSE ENTDECKEN');if(link)body.append(link);
        card.append(body);cards.append(card);
      });
      grid.append(cards);section.append(grid);upcoming.append(section);
    });
  }
  function folderCard(e,offset){
    const card=create('button','mf-folder-card '+(offset===0?'is-current':'is-side'));
    card.type='button';card.setAttribute('aria-label',e.title+' auswählen');
    card.append(create('span','mf-folder-card__spine','HAMMEL / MESSE'));
    const cover=create('div','mf-folder-card__cover');const src=validPhoto(e.image)||photoList(e)[0]?.image;
    if(src)cover.append(image(src,e.title));else cover.append(create('span','mf-folder-card__placeholder','HAMMEL'));
    card.append(cover);
    const label=create('div','mf-folder-card__label');label.append(create('span','mf-folder-card__date',String(e.start_date).slice(0,4)),create('strong','',e.title),create('span','',place(e)));
    card.append(label);return card;
  }
  function showLightbox(photos,start){
    let i=start;const modal=create('div','mf-lightbox');modal.setAttribute('role','dialog');modal.setAttribute('aria-modal','true');modal.setAttribute('aria-label','Messefotos');
    const picture=image(photos[i].image,photos[i].caption||'Messefoto');picture.className='mf-lightbox__image';
    const close=create('button','mf-lightbox__close','×'),prev=create('button','mf-lightbox__prev','←'),next=create('button','mf-lightbox__next','→'),caption=create('p','mf-lightbox__caption');
    [close,prev,next].forEach(b=>b.type='button');close.setAttribute('aria-label','Schließen');prev.setAttribute('aria-label','Vorheriges Foto');next.setAttribute('aria-label','Nächstes Foto');
    const refresh=()=>{picture.src=photos[i].image;picture.alt=photos[i].caption||'Messefoto';caption.textContent=(photos[i].caption||'')+'  '+(i+1)+' / '+photos.length;};
    const dismiss=()=>{modal.remove();document.removeEventListener('keydown',key);};
    const step=d=>{i=(i+d+photos.length)%photos.length;refresh();};
    const key=ev=>{if(ev.key==='Escape')dismiss();if(ev.key==='ArrowLeft')step(-1);if(ev.key==='ArrowRight')step(1);};
    close.addEventListener('click',dismiss);prev.addEventListener('click',()=>step(-1));next.addEventListener('click',()=>step(1));modal.addEventListener('click',ev=>{if(ev.target===modal)dismiss();});document.addEventListener('keydown',key);
    modal.append(close,prev,picture,next,caption);document.body.append(modal);refresh();close.focus();
  }
  function renderDetail(e){
    detail.replaceChildren();
    const heading=create('div','mf-detail-heading');
    const text=create('div','mf-story-copy');
    text.append(create('p','mf-eyebrow','EINBLICKE & HIGHLIGHTS'),create('h3','',e.title));
    const meta=create('div','mf-story-meta');
    meta.append(create('span','mf-story-meta-label','DATUM / STANDORT'),create('p','mf-date',dates(e)+'  /  '+place(e)));
    text.append(meta);
    if(e.description)text.append(create('p','mf-detail-description',e.description));
    const link=homeLink(e.url,'ZUR MESSE-WEBSITE');if(link)text.append(link);
    heading.append(text);
    const photos=photoList(e);
    const gallery=create('div','mf-detail-gallery');
    const galleryHead=create('div','mf-story-gallery-head');
    galleryHead.append(create('span','','FOTOGALERIE'),create('span','',String(photos.length)+' FOTOS'));
    if(!photos.length){gallery.append(create('p','mf-story-no-photos','Fotos zu dieser Messe folgen in Kürze.'));}
    else photos.forEach((p,i)=>{
      const b=create('button','mf-detail-photo');b.type='button';
      b.setAttribute('aria-label','Foto '+(i+1)+' öffnen');
      b.append(image(p.image,p.caption||e.title));
      b.append(create('span','mf-photo-index',String(i+1)+' / '+String(photos.length)));
      b.append(create('span','mf-photo-expand','↗'));
      if(p.caption)b.append(create('span','mf-detail-photo__caption',p.caption));
      b.addEventListener('click',()=>showLightbox(photos,i));gallery.append(b);
    });
    const visual=create('div','mf-story-visual');
    visual.append(galleryHead,gallery);
    if(photos.length>1)visual.append(create('p','mf-story-photo-count',photos.length+' FOTOS  ·  ZUM VERGRÖSSERN ANKLICKEN'));
    detail.append(heading,visual);
  }
  // Continuous circular archive: seven visible positions with perspective depth.
  // Neighbour cards are actual selectable events; selecting one centers it.
  function renderFolders(){
    stage.replaceChildren();detail.replaceChildren();
    const detailSection=$('mf-detail-standalone');
    if(detailSection){detailSection.dataset.hasEvent=past.length?'1':'';detailSection.hidden=!past.length || $('mf-past-panel').hidden;}
    if(!past.length){stage.append(create('p','mf-empty mf-empty--archive','Noch keine vergangenen Messen veröffentlicht. Sobald eine veröffentlichte Messe beendet ist, erscheint sie hier.'));$('mf-folder-position').textContent='';document.querySelectorAll('.mf-folder-nav').forEach(b=>{b.disabled=true;b.setAttribute('aria-disabled','true');});return;}
    const active=past[current];
    const range=past.length===1?[0]:past.length===2?[-1,0,1]:[-3,-2,-1,0,1,2,3];
    range.forEach(offset=>{
      const index=(current+offset%past.length+past.length)%past.length;
      const e=past[index];
      const card=folderCard(e,offset);
      card.classList.add('mf-snake-card');
      card.dataset.offset=String(offset);
      card.style.setProperty('--distance',String(Math.abs(offset)));
      card.style.setProperty('--offset',String(offset));
      card.style.zIndex=String(10-Math.abs(offset));
      card.setAttribute('aria-current',offset===0?'true':'false');
      card.setAttribute('aria-label',e.title+(offset===0?' ausgewählt':' auswählen'));
      card.addEventListener('click',()=>{
        if(offset===0){detail.scrollIntoView({behavior:'smooth',block:'start'});return;}
        move(offset);
      });
      stage.append(card);
    });
    $('mf-folder-position').textContent=(current+1)+' / '+past.length+'  ·  '+active.title;
    renderDetail(active);
    document.querySelectorAll('.mf-folder-nav').forEach(b=>b.disabled=past.length<2);
  }
  function move(n){if(!past.length)return;current=(current+n+past.length)%past.length;renderFolders();}
  document.querySelector('.mf-folder-nav--prev')?.addEventListener('click',()=>move(-1));
  document.querySelector('.mf-folder-nav--next')?.addEventListener('click',()=>move(1));
  stage.addEventListener('keydown',event=>{if(event.key==='ArrowRight'||event.key==='ArrowLeft'){event.preventDefault();move(event.key==='ArrowRight'?1:-1);stage.querySelector('[aria-current="true"]')?.focus();}});
  let touchStart=null;stage.addEventListener('touchstart',e=>{touchStart=e.changedTouches[0].clientX;},{passive:true});stage.addEventListener('touchend',e=>{if(touchStart===null)return;const diff=e.changedTouches[0].clientX-touchStart;if(Math.abs(diff)>45)move(diff<0?1:-1);touchStart=null;},{passive:true});
  async function load(){let data=[];try{const r=await fetch('/api/messen/',{credentials:'same-origin'});if(!r.ok)throw Error();data=await r.json();}catch(error){console.error('Messen API nicht erreichbar',error);}
    if(!Array.isArray(data))data=[];
    const now=new Date(),today=[now.getFullYear(),String(now.getMonth()+1).padStart(2,'0'),String(now.getDate()).padStart(2,'0')].join('-');
    const valid=data.filter(e=>e&&typeof e.title==='string'&&/^\d{4}-\d{2}-\d{2}$/.test(e.start_date)&&/^\d{4}-\d{2}-\d{2}$/.test(e.end_date));
    renderUpcoming(valid.filter(e=>e.end_date>=today).sort((a,b)=>a.start_date.localeCompare(b.start_date)));
    past=valid.filter(e=>e.end_date<today).sort((a,b)=>b.start_date.localeCompare(a.start_date));renderFolders();
  }
  load();
})();
