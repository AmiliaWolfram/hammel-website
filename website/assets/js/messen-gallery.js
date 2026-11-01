(() => {
 "use strict";
 const future = document.getElementById("messe-upcoming"), past = document.getElementById("messe-past");
 if (!future || !past) return;
 const el = (tag,cls,txt) => {const n=document.createElement(tag); if(cls)n.className=cls; if(txt!==undefined)n.textContent=txt; return n;};
 const safeLink = value => {try {const u=new URL(value,location.href);return /^(https?:)$/.test(u.protocol)?u.href:null;}catch{return null;}};
 const date = value => new Intl.DateTimeFormat("de-DE",{day:"2-digit",month:"short",year:"numeric",timeZone:"UTC"}).format(new Date(value+"T12:00:00Z"));
 const img = (src,alt) => {const n=el("img");n.src=src;n.alt=alt;n.loading="lazy";return n;};
 const photoURL = value => typeof value==="string" && value.startsWith("/media/messen/") ? value : null;
 const info = (e) => [e.city,e.country].filter(Boolean).join(", ");
 const empty = (root,msg) => root.append(el("p","messe-gallery-empty",msg));
 function upcoming(e) {
  const card=el("article","mg-future-card");const picture=el("div","mg-future-picture");
  if(photoURL(e.image))picture.append(img(e.image,e.title));else picture.append(el("span","mg-placeholder","HAMMEL"));
  const body=el("div","mg-future-body");body.append(el("span","mg-meta",date(e.start_date)+" — "+date(e.end_date)),el("h3","",e.title),el("p","mg-place",info(e)));
  if(e.booth)body.append(el("p","mg-booth","HALLE / STAND  "+e.booth));
  if(e.description)body.append(el("p","mg-description",e.description));
  const link=safeLink(e.url);if(link){const a=el("a","mg-home-link");a.href=link;a.target="_blank";a.rel="noopener noreferrer";a.append(el("span","mg-link-arrow","↗"),el("span","","MESSE ENTDECKEN"));body.append(a);}
  card.append(picture,body);future.append(card);
 }
 function pastEvent(e) {
  const card=el("article","mg-past-card"),heading=el("div","mg-past-heading");
  const text=el("div");text.append(el("span","mg-meta",date(e.start_date)+" — "+date(e.end_date)+"  /  "+info(e)),el("h3","",e.title));
  if(e.description)text.append(el("p","mg-description",e.description));heading.append(text);card.append(heading);
  const photos=(Array.isArray(e.photos)?e.photos:[]).filter(p=>photoURL(p.image));
  if(!photos.length && photoURL(e.image))photos.push({image:e.image,caption:""});
  if(photos.length){
   let index=0;const frame=el("div","mg-gallery-frame"),main=img(photos[0].image,e.title),caption=el("p","mg-photo-caption"),count=el("span","mg-photo-count"),buttons=el("div","mg-gallery-controls");
   main.className="mg-gallery-image";main.tabIndex=0;main.setAttribute("role","button");main.setAttribute("aria-label","Foto vergrößern");frame.append(main);
   const prev=el("button","mg-gallery-arrow","←"),next=el("button","mg-gallery-arrow","→");prev.type=next.type="button";prev.setAttribute("aria-label","Vorheriges Foto");next.setAttribute("aria-label","Nächstes Foto");
   const update=()=>{main.src=photos[index].image;main.alt=photos[index].caption||e.title;caption.textContent=photos[index].caption||"";count.textContent=(index+1)+" / "+photos.length;};
   prev.addEventListener("click",()=>{index=(index+photos.length-1)%photos.length;update();});next.addEventListener("click",()=>{index=(index+1)%photos.length;update();});
   const open=()=>{const modal=el("div","mg-lightbox"),close=el("button","mg-lightbox-close","×"),large=img(photos[index].image,main.alt);close.type="button";close.setAttribute("aria-label","Schließen");modal.setAttribute("role","dialog");modal.setAttribute("aria-modal","true");modal.append(close,large);const dismiss=()=>{modal.remove();document.removeEventListener("keydown",key);};const key=ev=>{if(ev.key==="Escape")dismiss();};close.addEventListener("click",dismiss);modal.addEventListener("click",ev=>{if(ev.target===modal)dismiss();});document.addEventListener("keydown",key);document.body.append(modal);close.focus();};
   main.addEventListener("click",open);main.addEventListener("keydown",ev=>{if(ev.key==="Enter")open();});
   let x=0;frame.addEventListener("touchstart",ev=>{x=ev.changedTouches[0].screenX;},{passive:true});frame.addEventListener("touchend",ev=>{const d=ev.changedTouches[0].screenX-x;if(Math.abs(d)>45){index=(index+(d<0?1:photos.length-1))%photos.length;update();}},{passive:true});
   buttons.append(prev,count,next);const foot=el("div","mg-gallery-foot");foot.append(caption,buttons);card.append(frame,foot);update();
  }else card.append(el("p","mg-no-photo","Fotos folgen in Kürze."));
  past.append(card);
 }
 async function load(){let data=[];try{const r=await fetch("/api/messen/",{credentials:"same-origin"});if(!r.ok)throw Error();data=await r.json();}catch(error){console.error('Messen API nicht erreichbar',error);}
  if(!Array.isArray(data))data=[];const today=new Date();const local=[today.getFullYear(),String(today.getMonth()+1).padStart(2,"0"),String(today.getDate()).padStart(2,"0")].join("-");
  const valid=data.filter(e=>e&&typeof e.title==="string"&&/^\d{4}-\d{2}-\d{2}$/.test(e.start_date)&&/^\d{4}-\d{2}-\d{2}$/.test(e.end_date));
  const a=valid.filter(e=>e.end_date>=local).sort((a,b)=>a.start_date.localeCompare(b.start_date)),b=valid.filter(e=>e.end_date<local).sort((a,b)=>b.start_date.localeCompare(a.start_date));
  a.forEach(upcoming);b.forEach(pastEvent);if(!a.length)empty(future,"Unsere nächsten Messetermine werden in Kürze veröffentlicht.");if(!b.length)empty(past,"Unser Messe-Rückblick wird in Kürze ergänzt.");
 }load();
})();