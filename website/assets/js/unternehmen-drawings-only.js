/* A single low-contrast contour fades in and out as its section crosses the viewport. */
(()=>{
 function start(){
  const items=[];
  for(const section of document.querySelectorAll('.about-main .story__chapter')){
   const drawing=section.querySelector('.history-drawing:not(.history-drawing--echo)');
   if(!drawing)continue;
   if(drawing.parentElement!==section)section.insertBefore(drawing,section.firstChild);
   for(const echo of section.querySelectorAll('.history-drawing--echo'))echo.remove();
   items.push([section,drawing]);
  }
  if(!items.length)return;
  if(matchMedia('(prefers-reduced-motion: reduce)').matches)return;
  const clamp=n=>Math.max(0,Math.min(1,n));
  const smooth=n=>{n=clamp(n);return n*n*(3-2*n)};
  let queued=false;
  function render(){
   queued=false;const h=innerHeight||800;
   for(const [section,drawing] of items){
    const r=section.getBoundingClientRect();
    const entering=smooth((h*.88-r.top)/(h*.42));
    const exiting=smooth((r.bottom-h*.12)/(h*.42));
    const opacity=entering*exiting*.075;
    drawing.style.setProperty('--hammel-drawing-opacity',opacity.toFixed(4));
    drawing.style.setProperty('--hammel-drawing-shift',((1-entering)*9-(1-exiting)*9).toFixed(1)+'px');
   }
  }
  function schedule(){if(!queued){queued=true;requestAnimationFrame(render)}}
  addEventListener('scroll',schedule,{passive:true});addEventListener('resize',schedule,{passive:true});render();
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});else start();
})();
