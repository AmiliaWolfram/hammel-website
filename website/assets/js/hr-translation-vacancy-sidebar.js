/* Vacancy translation editor: same section navigation in every language. */
(()=>{'use strict';
function init(){
 const main=document.querySelector('.translation-editor[data-vacancy-editor="true"]');
 const form=main?.querySelector('#translation-form');
 if(!form||form.querySelector('.hr-vacancy-translation-workspace'))return;
 const fields=[...form.querySelectorAll(':scope > section.field')];
 if(!fields.length)return;
 const sections=[
  {id:'general',title:'Allgemeine Angaben',sub:'Stellenbezeichnung'},
  {id:'description',title:'Stellenbeschreibung',sub:'Einleitung und Beschreibung'},
  {id:'tasks',title:'Aufgaben & Anforderungen',sub:'Aufgaben, Kenntnisse und Stärken'},
  {id:'benefits',title:'Das bieten wir',sub:'Leistungen und Vorteile'}
 ];
 const sectionFor=field=>{
  const name=field.querySelector('textarea[name^="translation_"]')?.name.replace(/^translation_/,'')||'';
  if(name==='title')return 'general';
  if(name==='introduction')return 'description';
  if(name==='benefits')return 'benefits';
  return 'tasks';
 };
 const shell=document.createElement('div');shell.className='hr-vacancy-translation-workspace';
 const nav=document.createElement('nav');nav.className='hr-vacancy-translation-nav';nav.setAttribute('aria-label','Inhalte der Stellenanzeige');
 const eyebrow=document.createElement('p');eyebrow.className='hr-vacancy-translation-eyebrow';eyebrow.textContent='INHALTE';nav.appendChild(eyebrow);
 const content=document.createElement('div');content.className='hr-vacancy-translation-content';
 const heading=document.createElement('h2');heading.className='hr-vacancy-translation-heading';content.appendChild(heading);
 const panels=document.createElement('div');content.appendChild(panels);
 const groups=new Map(sections.map(s=>[s.id,[]]));fields.forEach(field=>groups.get(sectionFor(field)).push(field));
 const available=sections.filter(s=>groups.get(s.id).length);
 available.forEach(s=>{
  const button=document.createElement('button');button.type='button';button.className='hr-vacancy-translation-tab';button.dataset.panel=s.id;
  const strong=document.createElement('span');strong.textContent=s.title;const small=document.createElement('small');small.textContent=s.sub;
  button.append(strong,small);nav.appendChild(button);
  const panel=document.createElement('section');panel.className='hr-vacancy-translation-panel';panel.dataset.panel=s.id;
  groups.get(s.id).forEach(field=>panel.appendChild(field));panels.appendChild(panel);
 });
 shell.append(nav,content);form.insertBefore(shell,fields[0]);
 const buttons=[...nav.querySelectorAll('button')];
 function show(id){buttons.forEach(button=>{const selected=button.dataset.panel===id;button.classList.toggle('is-active',selected);button.setAttribute('aria-pressed',String(selected));});
  panels.querySelectorAll('.hr-vacancy-translation-panel').forEach(panel=>panel.hidden=panel.dataset.panel!==id);
  heading.textContent=available.find(s=>s.id===id)?.title||'';
 }
 buttons.forEach(button=>button.addEventListener('click',()=>show(button.dataset.panel)));
 form.addEventListener('invalid',event=>{const panel=event.target.closest('.hr-vacancy-translation-panel');if(panel)show(panel.dataset.panel);},true);
 show(available[0].id);
 // Existing translation inputs, form submission and status fields remain unchanged.
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
