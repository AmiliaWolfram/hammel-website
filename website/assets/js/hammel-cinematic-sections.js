/* HAMMEL section choreography — progressively enhances existing layout.
   Uses only custom properties and the independent translate property.
   Leaves THE ORIGINAL, technical drawings and their scroll animation alone. */
(() => {
  'use strict';
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  function init() {
    // Public-facing blocks, not portals, admin panels, forms or inner widgets.
    if (/\/(admin|vertrieb|hrportal|login|logout|accounts|api)(?:\/|$)/i.test(location.pathname)) return;
    const main = document.querySelector('main');
    if (!main) return;
    const candidates = [
      ...document.querySelectorAll('main > section, main > .section, main > .wrap.product-grid, main > .content-section, main > .cinematic-scene'),
      ...document.querySelectorAll('.hammel-page-hero, main > .solutions-intro, main > .solution-machines, main > .solutions-facts'),
      ...document.querySelectorAll('main > div > section.cinematic-scene')
    ];
    const scenes = [...new Set(candidates)].filter(el => {
      if (el.closest('.story, .story__chapter, form, .admin-panel')) return false;
      if (el.matches('.story, .story__chapter')) return false;
      const box = el.getBoundingClientRect();
      return box.height >= 110;
    });
    if (!scenes.length) return;
    scenes.forEach((el,i) => {
      el.classList.add('hc-scene');
      if (el.querySelector('img,video')) el.classList.add('hc-scene--media');
      const style = getComputedStyle(el);
      const bg = style.backgroundColor.match(/rgba?\(([^)]+)\)/);
      if (bg) {
        const c = bg[1].split(',').slice(0,3).map(Number);
        if (c[0] > c[1]*1.55 && c[0] > c[2]*1.55 && c[0] > 90) el.classList.add('hc-red');
        else if (c.reduce((a,b)=>a+b,0)<330) el.classList.add('hc-dark');
        else el.classList.add('hc-light');
      }
    });
    const clamp = n => Math.min(1,Math.max(0,n));
    const smooth = n => {n=clamp(n);return n*n*(3-2*n)};
    let frame = 0;
    function update(){
      frame=0;
      const h=innerHeight||800;
      for(const el of scenes){
        const r=el.getBoundingClientRect();
        // A section enters over ~45% of viewport; reverses on scrolling back.
        const reveal=smooth((h*0.98-r.top)/(h*0.46));
        // Section boundary gains subtle depth as it crosses the upper viewport.
        const edge=smooth((h*.9-r.top)/(h*.55))*(1-smooth((-r.top)/(h*.34)));
        const drift=(1-reveal)*26;
        el.style.setProperty('--hc-reveal',reveal.toFixed(4));
        el.style.setProperty('--hc-edge',edge.toFixed(4));
        el.style.setProperty('--hc-drift',drift.toFixed(2)+'px');
      }
    }
    function schedule(){if(!frame)frame=requestAnimationFrame(update)}
    addEventListener('scroll',schedule,{passive:true});
    addEventListener('resize',schedule,{passive:true});
    addEventListener('pageshow',schedule);
    update();
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});
  else init();
})();
