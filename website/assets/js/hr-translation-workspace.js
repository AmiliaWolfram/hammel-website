document.addEventListener('DOMContentLoaded',()=>{
 const root=document.querySelector('.translation-editor');const form=document.getElementById('translation-form');if(!root||!form)return;
 const cards=[...form.querySelectorAll('section.field')];if(!cards.length)return;
 const sections=[{id:'general',title:'Allgemeine Angaben'},{id:'description',title:'Stellenbeschreibung'},{id:'tasks',title:'Aufgaben'},{id:'requirements',title:'Anforderungen'}];
 const classify=(card,i)=>{const name=((card.querySelector('h2')?.textContent||'')+' '+(card.querySelector('textarea')?.name||'')).toLowerCase();if(/aufgab|tätigkeit|responsibilit|duties|task/.test(name))return 'tasks';if(/anforder|kenntnis|qualifik|skill|profil|voraussetz/.test(name))return 'requirements';if(/beschreibung|einleitung|intro|benefit|wir bieten|über uns|text|inhalt/.test(name))return 'description';return i===0?'general':'description'};
 cards.forEach((card,i)=>card.dataset.cleanSection=classify(card,i));
 const top=document.createElement('div');top.className='hr-clean-top';const tabs=root.querySelector('.language-tabs');tabs.parentNode.insertBefore(top,tabs);top.appendChild(tabs);const progress=document.createElement('span');progress.className='hr-clean-progress';progress.setAttribute('aria-live','polite');top.appendChild(progress);
 const layout=document.createElement('div');layout.className='hr-clean-layout';const sidebar=document.createElement('aside');sidebar.className='hr-clean-sidebar';sidebar.innerHTML='<h2 class="hr-clean-sidebar-title">INHALTE</h2><nav class="hr-clean-nav" aria-label="Übersetzungsbereiche"></nav>';
 const work=document.createElement('div');work.className='hr-clean-work';const heading=document.createElement('h2');heading.className='hr-clean-section-heading';work.appendChild(heading);
 const nextbar=document.createElement('div');nextbar.className='hr-clean-bottom';const hint=document.createElement('span');hint.className='hr-clean-progress';nextbar.appendChild(hint);const next=document.createElement('button');next.type='button';next.className='hr-clean-next';next.textContent='WEITER →';nextbar.appendChild(next);
 const nav=sidebar.querySelector('nav');let active='general';
 const originalParent=form.parentNode;originalParent.insertBefore(layout,form);layout.append(sidebar,work);work.appendChild(form);
 const actions=form.querySelector('.actions');form.insertBefore(nextbar,actions);
 sections.forEach(s=>{const btn=document.createElement('button');btn.type='button';btn.dataset.section=s.id;btn.innerHTML='<span class="nav-name"></span><span class="nav-progress"></span>';btn.querySelector('.nav-name').textContent=s.title;btn.addEventListener('click',()=>show(s.id));nav.appendChild(btn)});
 function done(card){return !!card.querySelector('textarea')?.value.trim()&&card.querySelector('select[name^="status_"]')?.value==='published'&&card.dataset.stale!=='yes'}
 function refresh(){let total=0;cards.forEach(c=>{if(done(c))total++});progress.textContent=total+' / '+cards.length+' geprüft';sections.forEach(s=>{const group=cards.filter(c=>c.dataset.cleanSection===s.id);const count=group.filter(done).length;nav.querySelector('[data-section="'+s.id+'"] .nav-progress').textContent=group.length?count+' / '+group.length+' geprüft':'Keine Textfelder'});const visible=cards.filter(c=>c.dataset.cleanSection===active);hint.textContent=visible.filter(done).length+' / '+visible.length+' geprüft'}
 function show(id){active=id;const section=sections.find(s=>s.id===id);heading.textContent=section.title;cards.forEach(c=>c.hidden=c.dataset.cleanSection!==id);nav.querySelectorAll('button').forEach(b=>{b.classList.toggle('active',b.dataset.section===id);if(b.dataset.section===id)b.setAttribute('aria-current','true');else b.removeAttribute('aria-current')});next.textContent=id==='requirements'?'ZUM ERSTEN BEREICH ↺':'WEITER →';refresh()}
 next.addEventListener('click',()=>show(sections[(sections.findIndex(s=>s.id===active)+1)%sections.length].id));
 cards.forEach(c=>{c.addEventListener('input',refresh);c.addEventListener('change',refresh)});
 // Draft recovery stays in the page but is moved outside the editable fields.
 const draft=document.getElementById('draft-prompt');if(draft)work.insertBefore(draft,heading);
 const urlSection=new URLSearchParams(location.search).get('section');show(sections.some(s=>s.id===urlSection)?urlSection:'general');
});