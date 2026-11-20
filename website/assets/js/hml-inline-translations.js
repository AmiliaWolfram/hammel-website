(()=>{const root=document.querySelector('[data-hml-i18n]');const dataEl=document.getElementById('hml-inline-data');if(!root||!dataEl)return;const data=JSON.parse(dataEl.textContent);const form=root.closest('form');if(!form)return;const tabs=[...root.querySelectorAll('[data-hml-lang]')],panel=root.querySelector('[data-hml-fields]'),help=root.querySelector('[data-hml-help]'),output=root.querySelector('[data-hml-output]');const state={};['en','fr','es','it'].forEach(l=>{state[l]={};data.rows.forEach(r=>{state[l][r.name]={...r.versions[l]};});});let active='de';
const isSeries=!!root.closest('.baureihe-language-workspace');
if(isSeries){const tab=document.createElement('button');tab.type='button';tab.dataset.hmlLang='review';tab.textContent='PRÜFUNG';root.querySelector('.hml-i18n-tabs')?.append(tab);tabs.push(tab);}
const nativeFields=data.rows.map(r=>{const el=[...form.elements].find(e=>e.name===r.name);return {name:r.name,el,wrapper:el?.closest('.staff-field,.machine-field,.field')||el?.parentElement};});const originalDisplay=new Map();function counts(){for(const l of Object.keys(state)){const filled=Object.values(state[l]).filter(v=>v.text.trim()).length;const stale=Object.values(state[l]).some(v=>v.stale);const el=root.querySelector('[data-count="'+l+'"]');if(el)el.textContent=filled+'/'+data.rows.length+(stale?' !':'');}}function persist(){output.value=JSON.stringify(state);}function show(lang){active=lang;tabs.forEach(t=>{const yes=t.dataset.hmlLang===lang;t.classList.toggle('active',yes);t.setAttribute('aria-selected',yes?'true':'false');});nativeFields.forEach(({wrapper})=>{if(!wrapper)return;if(lang==='de'){if(originalDisplay.has(wrapper)){wrapper.style.display=originalDisplay.get(wrapper);originalDisplay.delete(wrapper);}}else{if(!originalDisplay.has(wrapper))originalDisplay.set(wrapper,wrapper.style.display);wrapper.style.display='none';}});panel.replaceChildren();panel.hidden=lang==='de';
if(root.closest('.baureihe-language-workspace')){
  form.classList.toggle('baureihe-translating',lang!=='de');
}
if(isSeries&&lang==='review'){
 panel.hidden=false;
 const container=document.createElement('div');container.className='baureihe-review';
 const title=document.createElement('h2');title.textContent='PRÜFUNG';container.append(title);
 const intro=document.createElement('p');intro.textContent='Übersicht der Übersetzungen und Bearbeitungsstände. Änderungen an Texten und Status erfolgen in den jeweiligen Sprachversionen.';container.append(intro);
 const table=document.createElement('table');const head=document.createElement('tr');
 ['Sprache','Übersetzte Felder','Status'].forEach(v=>{const th=document.createElement('th');th.textContent=v;head.append(th)});table.append(head);
 const visibleLanguages=tabs.filter(t=>t.dataset.hmlLang!=='de'&&t.dataset.hmlLang!=='review'&&!t.hidden&&t.style.display!=='none');
 visibleLanguages.forEach(t=>{const langCode=t.dataset.hmlLang;const versions=Object.values(state[langCode]||{});const filled=versions.filter(v=>(v.text||'').trim()).length;const statuses=[...new Set(versions.map(v=>v.status))];const row=document.createElement('tr');
 [langCode.toUpperCase(),filled+' / '+versions.length,statuses.length===1?({draft:'Entwurf',review:'Zur Prüfung',published:'Veröffentlicht'}[statuses[0]]||statuses[0]):'Unterschiedliche Status'].forEach((value,i)=>{const td=document.createElement('td');td.textContent=value;if(i===1&&filled<versions.length)td.className='baureihe-review-empty';row.append(td)});table.append(row)});
 container.append(table);panel.append(container);help.textContent='';return;
 }
 help.textContent=lang==='de'?'Deutsch ist der Originaltext. Die Felder unten bearbeiten den deutschen Inhalt.':'Übersetzungen für '+lang.toUpperCase()+' bearbeiten. Alle Änderungen werden mit dem Formular gespeichert.';if(lang==='de')return;for(const r of data.rows){const value=state[lang][r.name];const box=document.createElement('div');box.className='hml-i18n-field';const label=document.createElement('label');label.textContent=r.label;const input=document.createElement('textarea');input.value=value.text;input.maxLength=30000;input.rows=3;input.setAttribute('aria-label',r.label+' '+lang.toUpperCase());input.addEventListener('input',()=>{value.text=input.value;value.dirty=true;persist();counts();});const status=document.createElement('select');for(const [code,text] of [['draft','Entwurf'],['review','Zur Prüfung'],['published','Veröffentlicht']]){const opt=new Option(text,code);status.add(opt);}status.value=value.status;status.addEventListener('change',()=>{value.status=status.value;value.dirty=true;persist();});box.append(label);
if(root.closest('.baureihe-language-workspace')){
  const source=nativeFields.find(f=>f.name===r.name)?.el;
  const original=document.createElement('div');
  original.className='baureihe-german-reference';
  const heading=document.createElement('strong');
  heading.textContent='DEUTSCH – ORIGINAL';
  const content=document.createElement('div');
  content.textContent=(source?.value||'').trim()||'–';
  original.append(heading,content);
  box.append(original);
}
box.append(input);if(value.stale){const warning=document.createElement('p');warning.className='hml-i18n-stale';warning.textContent='ÜBERSETZUNG ÜBERPRÜFEN / Deutscher Originaltext wurde geändert';box.append(warning);}box.append(status);panel.append(box);}}tabs.forEach(t=>t.addEventListener('click',()=>show(t.dataset.hmlLang)));form.addEventListener('submit',persist);counts();persist();show('de');const inactiveToggle=root.querySelector('[data-machine-inactive-toggle]');if(inactiveToggle){inactiveToggle.addEventListener('click',()=>{const expanded=inactiveToggle.getAttribute('aria-expanded')!=='true';inactiveToggle.setAttribute('aria-expanded',String(expanded));inactiveToggle.textContent=expanded?'Ausblenden':'Zur Bearbeitung anzeigen';root.querySelectorAll('[data-inactive-language]').forEach(tab=>{tab.hidden=!expanded;tab.style.display=expanded?'':'none';});if(!expanded&&root.querySelector('[data-hml-lang="'+active+'"]')?.hasAttribute('data-inactive-language'))show('de');});root.querySelectorAll('[data-inactive-language]').forEach(tab=>{tab.hidden=true;tab.style.display='none';});} })();