document.addEventListener('DOMContentLoaded',()=>{const links=[...document.querySelectorAll('.story-timeline__links a[href^="#"]')];const targets=links.map(a=>document.querySelector(a.getAttribute('href')));links.forEach(a=>a.addEventListener('click',e=>{const target=document.querySelector(a.getAttribute('href'));if(!target)return;e.preventDefault();target.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'});history.replaceState(null,'',location.pathname+location.search);}));if(!('IntersectionObserver'in window))return;const observer=new IntersectionObserver(entries=>{entries.forEach(entry=>{if(!entry.isIntersecting)return;links.forEach((a,i)=>{const active=targets[i]===entry.target;a.classList.toggle('is-current',active);if(active)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current');});});},{rootMargin:'-15% 0px -65% 0px'});targets.filter(Boolean).forEach(el=>observer.observe(el));});

/* Scroll-synced drawing progress, only for archive chapters; building finale untouched. */
(()=>{const chapters=[...document.querySelectorAll('.story__chapter')].filter(el=>el.querySelector('.story__art img[src*="/archiv/"]')&&!el.classList.contains('story__chapter--final'));if(!chapters.length)return;const reduced=matchMedia('(prefers-reduced-motion: reduce)');let scheduled=false;function update(){scheduled=false;const vh=innerHeight||800;chapters.forEach(el=>{const r=el.getBoundingClientRect();const progress=reduced.matches?1:Math.max(0,Math.min(1,(vh*.85-r.top)/(vh*.85+Math.min(r.height,vh*.8))));el.style.setProperty('--trace',progress.toFixed(3));});}function schedule(){if(!scheduled){scheduled=true;requestAnimationFrame(update)}}addEventListener('scroll',schedule,{passive:true});addEventListener('resize',schedule,{passive:true});update();})();

/* Reload must start at the top; timeline navigation must not persist as a hash. */
(function(){
  if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
  const nav = performance.getEntriesByType('navigation')[0];
  const isReload = nav && nav.type === 'reload';
  if (isReload) {
    if (location.hash) history.replaceState(null, '', location.pathname + location.search);
    const reset = () => window.scrollTo({top:0,left:0,behavior:'instant'});
    reset();
    window.addEventListener('pageshow', reset, {once:true});
    window.addEventListener('load', reset, {once:true});
  }
})();
