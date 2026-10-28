// Progressive enhancement: public content remains visible without JavaScript.
export const landingMotionScript = `(()=>{
const root=document.documentElement,preview=document.querySelector('.preview'),toggle=document.querySelector('[data-preview-motion]');
const reduced=matchMedia('(prefers-reduced-motion:reduce)');
root.dataset.landingMotion='ready';
let paused=false;
function sync(){
root.dataset.landingPaused=String(paused||reduced.matches);
if(toggle){toggle.hidden=reduced.matches;toggle.setAttribute('aria-pressed',String(paused));toggle.setAttribute('aria-label',toggle.dataset[paused?'resumeLabel':'pauseLabel']);}
if(reduced.matches)document.querySelectorAll('[data-reveal="pending"]').forEach(node=>node.dataset.reveal='visible');
}
toggle?.addEventListener('click',()=>{paused=!paused;sync()});
reduced.addEventListener?.('change',sync);sync();
document.addEventListener('visibilitychange',()=>{root.dataset.landingHidden=String(document.hidden)});
if(!('IntersectionObserver'in window)||reduced.matches)return;
const observer=new IntersectionObserver(entries=>{for(const entry of entries){
if(entry.target===preview)preview.dataset.active=String(entry.isIntersecting);
if(entry.isIntersecting){entry.target.dataset.reveal='visible';if(entry.target!==preview)observer.unobserve(entry.target);}
}},{threshold:0.12});
document.querySelectorAll('[data-reveal]').forEach(node=>{if(node.getBoundingClientRect().top>innerHeight-24)node.dataset.reveal='pending';observer.observe(node)});
})()`;
