document.addEventListener('DOMContentLoaded',()=>{
 const cards=[...document.querySelectorAll('.translation-editor section.field')];if(!cards.length)return;
 const progress=document.getElementById('hr-translation-progress');
 const refresh=()=>{const complete=cards.filter(card=>{const text=card.querySelector('textarea')?.value.trim();const status=card.querySelector('select[name^="status_"]')?.value;return !!text&&status==='published'&&card.dataset.stale!=='yes'}).length;
 progress.textContent=`${complete} von ${cards.length} Textfeldern freigegeben / ${cards.length-complete} offen`;
 progress.style.setProperty('--complete',`${Math.round(complete/cards.length*100)}%`);
 };
 cards.forEach(card=>card.addEventListener('input',refresh));cards.forEach(card=>card.addEventListener('change',refresh));refresh();
 let index=-1;document.getElementById('jump-missing')?.addEventListener('click',()=>{
 const missing=cards.filter(card=>{const text=card.querySelector('textarea')?.value.trim();const status=card.querySelector('select[name^="status_"]')?.value;return !text||status!=='published'||card.dataset.stale==='yes'});
 if(!missing.length){progress.textContent='Alle Felder sind freigegeben';return;}
 index=(index+1)%missing.length;document.querySelector('[data-filter="all"]')?.click();
 missing[index].scrollIntoView({behavior:'smooth',block:'center'});missing[index].querySelector('textarea')?.focus({preventScroll:true});
 });
});
