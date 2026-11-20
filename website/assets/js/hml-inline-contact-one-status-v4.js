(()=>{
const root=document.querySelector('[data-contact-all-languages]'),dataEl=document.getElementById('hml-inline-data');
if(!root||!dataEl)return;
const data=JSON.parse(dataEl.textContent),form=root.closest('form'),output=root.querySelector('[data-hml-output]');
if(!form||!data||!data.rows)return;
const state={};
for(const lang of ['en','fr','es','it']){
 state[lang]={};
 for(const row of data.rows)state[lang][row.name]={...row.versions[lang]};
}
function persist(){output.value=JSON.stringify(state);}
for(const holder of root.querySelectorAll('[data-contact-language]')){
 const lang=holder.dataset.contactLanguage, label=holder.dataset.label;
 const card=document.createElement('section');card.className='hml-i18n-contact-language';
 const title=document.createElement('h3');title.textContent=lang.toUpperCase()+'  '+label;card.append(title);
 for(const row of data.rows){
  const value=state[lang][row.name],fieldLabel=document.createElement('label');
  fieldLabel.textContent=row.label;card.append(fieldLabel);
  const input=document.createElement('textarea');input.value=value.text||'';input.maxLength=30000;input.rows=3;
  input.addEventListener('input',()=>{value.text=input.value;value.dirty=true;persist();});card.append(input);
  if(value.stale){const warning=document.createElement('p');warning.className='hml-i18n-stale';warning.textContent='Übersetzung überprüfen: Deutscher Originaltext wurde geändert';card.append(warning);}
 }
  // One shared status selector per language, rather than one per translated field.
  // Existing per-field statuses remain untouched until the user changes this selector.
  const statuses=data.rows.map(row=>state[lang][row.name].status||'draft');
  const status=document.createElement('select');
  // VP owns this select: prevent the second (HML) dropdown enhancer.
  status.dataset.hrEnhanced='1';
  for(const [code,text] of [['draft','Entwurf'],['review','Zur Prüfung'],['published','Veröffentlicht']])status.add(new Option(text,code));
  status.value=statuses.every(s=>s===statuses[0])?statuses[0]:'draft';
  if(!statuses.every(s=>s===statuses[0])){
    const mixed=new Option('Unterschiedliche Status – bitte wählen','mixed');
    status.add(mixed);status.value='mixed';
  }
  status.setAttribute('aria-label','Status '+label);
  status.addEventListener('change',()=>{
    if(status.value==='mixed')return;
    for(const row of data.rows){const value=state[lang][row.name];value.status=status.value;value.dirty=true;}
    const mixed=status.querySelector('option[value="mixed"]');if(mixed)mixed.remove();
    persist();
  });
  card.append(status);
  // Hide the underlying native select when the custom HAMMEL dropdown is present.
  const hideNative=()=>{if(status.closest('.hml-dropdown'))status.style.setProperty('display','none','important');};
  hideNative();
  new MutationObserver(hideNative).observe(card,{childList:true,subtree:true});
 holder.append(card);
}

// Contact-only invariant: exactly one status control per language card.
// The shared dropdown enhancer may wrap native selects after this script runs.
function enforceOneStatusPerLanguage(){
 for(const card of root.querySelectorAll('.hml-i18n-contact-language')){
   const selects=Array.from(card.querySelectorAll('select'));
   if(selects.length<=1)continue;
   const keep=selects[0];
   for(const extra of selects.slice(1)){
     const wrapper=extra.closest('.hml-dropdown');
     if(wrapper&&card.contains(wrapper))wrapper.remove();
     else extra.remove();
   }
 }
}
enforceOneStatusPerLanguage();
const statusObserver=new MutationObserver(()=>enforceOneStatusPerLanguage());
statusObserver.observe(root,{childList:true,subtree:true});

form.addEventListener('submit',persist);persist();
})();