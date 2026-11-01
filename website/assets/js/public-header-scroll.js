(function(){
function init(){
 const h=document.querySelector('header.top');if(!h)return;
 const hero=document.querySelector('.hero--video, .hammel-page-hero video, .hammel-page-hero__video, .hero-background-video, main video[autoplay]');
 h.classList.toggle('has-video-hero',!!hero);
 function update(){h.classList.toggle('is-scrolled',window.scrollY>36)}
 update();window.addEventListener('scroll',update,{passive:true});
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();