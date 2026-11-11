/* One-to-one scroll-linked reversible motion for history chapters. */
(()=>{const reduced=matchMedia('(prefers-reduced-motion: reduce)');
function init(){const blocks=[...document.querySelectorAll('.story__chapter')].map(section=>({section,text:section.querySelector('.story__text'),art:section.querySelector('.story__art')})).filter(x=>x.text&&x.art);if(!blocks.length)return;
const clamp=x=>Math.max(0,Math.min(1,x));const smooth=x=>{x=clamp(x);return x*x*(3-2*x)};
let raf=0;
function update(){raf=0;const vh=innerHeight||800;for(const b of blocks){const r=b.section.getBoundingClientRect();const p=reduced.matches?1:smooth((vh*.94-r.top)/(vh*.50));const offset=(1-p);const reverse=b.section.classList.contains('story__chapter--reverse');
b.text.style.setProperty('--reveal-text-x',((reverse?-1:1)*offset*26).toFixed(2)+'px');b.text.style.setProperty('--reveal-text-y',(offset*20).toFixed(2)+'px');b.text.style.setProperty('--reveal-text-alpha',(0.18+0.82*p).toFixed(3));
b.art.style.setProperty('--reveal-art-y',(offset*38).toFixed(2)+'px');b.art.style.setProperty('--reveal-art-scale',(0.965+0.035*p).toFixed(4));b.art.style.setProperty('--reveal-art-alpha',(0.12+0.88*p).toFixed(3));
}}
function schedule(){if(!raf)raf=requestAnimationFrame(update)};addEventListener('scroll',schedule,{passive:true});addEventListener('resize',schedule,{passive:true});reduced.addEventListener?.('change',schedule);update();}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();})();
