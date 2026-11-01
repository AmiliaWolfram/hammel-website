/* HAMMEL Karriere: Lesefokus beim Scrollen, ohne zusätzliche Bibliotheken */
(function(){
  function init(){
    var root=document.querySelector('.hr-journey-scroll');if(!root)return;
    var steps=Array.prototype.slice.call(root.querySelectorAll('.hr-journey-scroll__step'));
    var fill=root.querySelector('.hr-journey-scroll__progress span');
    var label=root.querySelector('.hr-journey-scroll__count');
    if(!steps.length)return;
    var motion=window.matchMedia('(prefers-reduced-motion: reduce)');
    if(motion.matches){steps.forEach(function(el){el.classList.add('is-active')});if(fill)fill.style.width='100%';if(label)label.textContent='DEIN BEWERBUNGSWEG';return;}
    var ticking=false;
    function update(){
      ticking=false;var target=window.innerHeight*.48;var chosen=0;var distance=Infinity;
      steps.forEach(function(el,i){var r=el.getBoundingClientRect();var center=r.top+r.height/2;var d=Math.abs(center-target);if(d<distance){distance=d;chosen=i;}});
      steps.forEach(function(el,i){el.classList.toggle('is-active',i===chosen)});
      if(fill)fill.style.width=((chosen+1)/steps.length*100)+'%';
      if(label)label.textContent=steps[chosen].querySelector('h3').textContent;
    }
    function request(){if(!ticking){ticking=true;window.requestAnimationFrame(update)}}
    window.addEventListener('scroll',request,{passive:true});window.addEventListener('resize',request);update();
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
