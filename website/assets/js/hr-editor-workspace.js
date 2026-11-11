(()=>{'use strict';
function init(){const form=document.querySelector('#hr-de-form');if(!form||!document.querySelector('#hr-builder'))return;
const names=[['general','Allgemeine Angaben','Grunddaten zur Stelle'],['description','Stellenbeschreibung','Einleitung und Beschreibung'],['builder','Aufgaben & Anforderungen','Textbausteine und eigene Inhalte']];
const elements=[...form.children];const fields=elements.filter(e=>e.classList?.contains('staff-field'));const builder=form.querySelector('#hr-builder');
const groups={general:[],description:[],builder:[]};
for(const e of fields){const key=e.querySelector('[name]')?.name||'';const section=({title:'general',category:'general',department:'general',location:'general',employment_type:'general',introduction:'description',requirements:'builder',published:'general'})[key]||'description';groups[section].push(e)}
if(builder)groups.builder.push(builder);
const store=[...form.querySelectorAll('.hr-builder-storage')]; // keep original hidden fields within form
const shell=document.createElement('div');shell.className='hr-workspace';shell.innerHTML=`<nav class="hr-workspace-nav" aria-label="Bereiche der Stellenanzeige"><p class="hr-workspace-eyebrow">INHALTE</p>${names.map(([id,title,sub],i)=>`<button type="button" class="hr-workspace-tab" data-panel="${id}" aria-pressed="${i===0}"><span>${title}</span><small>${sub}</small></button>`).join('')}</nav><div class="hr-workspace-content"><div class="hr-workspace-top"><div><p class="hr-workspace-eyebrow">STELLENEDITOR</p><h2 id="hr-workspace-heading">Allgemeine Angaben</h2></div><span class="hr-workspace-progress" aria-live="polite">1 / 3</span></div><div id="hr-workspace-panels"></div><div class="hr-workspace-actions"><button type="button" class="hr-workspace-prev">ZURÜCK</button><button type="button" class="hr-workspace-next">WEITER</button></div></div>`;
const panels=shell.querySelector('#hr-workspace-panels');for(const [id] of names){const panel=document.createElement('section');panel.className='hr-workspace-panel';panel.dataset.panel=id;panel.hidden=true;groups[id].forEach(el=>panel.appendChild(el));panels.appendChild(panel)}
const firstField=form.querySelector('.staff-field');if(firstField)form.insertBefore(shell,firstField);else form.insertBefore(shell,form.firstChild);
let active=0;function show(index){active=Math.max(0,Math.min(names.length-1,index));const [id,title]=names[active];for(const panel of panels.children)panel.hidden=panel.dataset.panel!==id;for(const b of shell.querySelectorAll('.hr-workspace-tab')){const selected=b.dataset.panel===id;b.classList.toggle('is-active',selected);b.setAttribute('aria-pressed',String(selected));
   // Force the exact translation-editor selected appearance despite legacy !important rules.
   b.style.setProperty('background-color',selected?'#171717':'transparent','important');
   b.style.setProperty('background',selected?'#171717':'transparent','important');
   b.style.setProperty('color',selected?'#f2b705':'#191919','important');
   const heading=b.querySelector('span');const subtitle=b.querySelector('small');
   if(heading)heading.style.setProperty('color',selected?'#f2b705':'#191919','important');
   if(subtitle)subtitle.style.setProperty('color',selected?'#ffffff':'#666666','important')}shell.querySelector('#hr-workspace-heading').textContent=title;shell.querySelector('.hr-workspace-progress').textContent=`${active+1} / ${names.length}`;shell.querySelector('.hr-workspace-prev').hidden=active===0;shell.querySelector('.hr-workspace-next').hidden=active===names.length-1;}
shell.querySelectorAll('.hr-workspace-tab').forEach((b,i)=>b.addEventListener('click',()=>show(i)));shell.querySelector('.hr-workspace-prev').addEventListener('click',()=>show(active-1));shell.querySelector('.hr-workspace-next').addEventListener('click',()=>show(active+1));
form.addEventListener('invalid',e=>{const panel=e.target.closest('.hr-workspace-panel');if(panel){const idx=names.findIndex(([id])=>id===panel.dataset.panel);if(idx>=0)show(idx)}},true);
// Existing form scripts and form submit continue using the same inputs and names.
show(0);
const nav=shell.querySelector('.hr-workspace-nav');
const footer=document.createElement('div');footer.className='hr-workspace-nav-footer';
const save=form.querySelector(':scope > .staff-button[type="submit"]');
const back=document.querySelector('.hr-editor-bottom-back');
if(save){save.remove();save.setAttribute('form','hr-de-form');save.textContent="DEUTSCH SPEICHERN & WEITER";footer.appendChild(save);}
if(back){back.remove();footer.appendChild(back);}
nav.appendChild(footer);
document.querySelector('.hr-quick-guide')?.remove();}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();})();
(function(){
 const css=document.createElement('style');
 css.textContent=`
 .hr-workspace-nav{display:flex;flex-direction:column;align-self:start;position:sticky;top:125px;max-height:calc(100vh - 145px);overflow:auto}
 .hr-workspace-nav-footer{display:flex;flex-direction:column;gap:10px;margin-top:24px;padding-top:18px;border-top:1px solid #ddd}
 .hr-workspace-nav-footer .staff-button,.hr-workspace-nav-footer .hr-nav-button{width:100%;max-width:none;box-sizing:border-box;text-align:center;white-space:normal}
 .hr-workspace-nav-footer .hr-editor-bottom-back{margin:0;width:100%}
 .hr-workspace-panel[hidden]{display:none!important}
 @media(max-width:850px){.hr-workspace-nav{position:static;max-height:none}}
 `;
 document.head.appendChild(css);
})();
