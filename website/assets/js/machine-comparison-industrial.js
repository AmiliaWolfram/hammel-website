(function(){"use strict";const buttons=[...document.querySelectorAll(".comparison-filter")];const rows=[...document.querySelectorAll(".comparison-row")];const empty=document.querySelector(".comparison-empty");if(!buttons.length||!rows.length)return;const normalize=s=>(s||"").replace(/\s+/g," ").trim().toLocaleLowerCase("de");function apply(mode){let visible=0;for(const row of rows){const values=[...row.querySelectorAll("td")].map(cell=>normalize(cell.textContent));const different=new Set(values).size>1;row.hidden=mode==="differences"&&!different;if(!row.hidden)visible++}for(const button of buttons){const active=button.dataset.filter===mode;button.classList.toggle("is-active",active);button.setAttribute("aria-pressed",String(active))}if(empty)empty.hidden=visible!==0}buttons.forEach(button=>button.addEventListener("click",()=>apply(button.dataset.filter)));apply("all")})();
/* Match the intro column to the FULL card height, including model name and action. */
(function(){
 const root=document.querySelector('.comparison-page');
 if(!root)return;
 const intro=root.querySelector('.comparison-series-intro');
 const cards=[...root.querySelectorAll('thead .comparison-model-link')];
 if(!intro||!cards.length)return;
 let frame=0;
 function align(){
   cancelAnimationFrame(frame);
   frame=requestAnimationFrame(()=>{
     intro.style.removeProperty('--comparison-card-height');
     if(window.innerWidth<=800)return;
     const height=Math.ceil(Math.max(...cards.map(card=>card.getBoundingClientRect().height)));
     if(height>0)intro.style.setProperty('--comparison-card-height',height+'px');
   });
 }
 window.addEventListener('resize',align,{passive:true});
 window.addEventListener('load',align);
 if(document.fonts&&document.fonts.ready)document.fonts.ready.then(align);
 cards.forEach(card=>card.querySelectorAll('img').forEach(img=>img.addEventListener('load',align,{once:true})));
 align();
})();
