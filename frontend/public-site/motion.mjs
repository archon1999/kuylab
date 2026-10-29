// Progressive enhancement: public content remains visible without JavaScript.
export const landingMotionScript = `(()=>{
const root=document.documentElement;
const reduced=matchMedia('(prefers-reduced-motion:reduce)');
root.dataset.landingMotion='ready';
function sync(){
root.dataset.landingPaused=String(reduced.matches);
if(reduced.matches)document.querySelectorAll('[data-reveal="pending"]').forEach(node=>node.dataset.reveal='visible');
}
reduced.addEventListener?.('change',sync);sync();
document.addEventListener('visibilitychange',()=>{root.dataset.landingHidden=String(document.hidden)});
if(!('IntersectionObserver'in window)||reduced.matches)return;
const observer=new IntersectionObserver(entries=>{for(const entry of entries){
if(entry.isIntersecting){entry.target.dataset.reveal='visible';observer.unobserve(entry.target);}
}},{threshold:0.12});
document.querySelectorAll('[data-reveal]').forEach(node=>{if(node.getBoundingClientRect().top>innerHeight-24)node.dataset.reveal='pending';observer.observe(node)});
})()`;

export function demoBootstrapScript(moduleUrl) {
  return `(()=>{
const host=document.querySelector('[data-demo]');if(!host)return;
host.dataset.enhanced='true';let pending;
function player(){return pending||(pending=import(${JSON.stringify(moduleUrl)}).then(module=>module.mountLandingDemo(host)).catch(()=>{
pending=undefined;host.dataset.state='error';host.querySelector('[data-demo-error]').hidden=false;throw Error('demo-load');
}))}
const invoke=action=>{void player().then(action).catch(()=>{})};
host.querySelector('[data-demo-start]').addEventListener('click',()=>invoke(p=>p.play()));
host.querySelector('[data-demo-toggle]').addEventListener('click',()=>invoke(p=>p.toggle()));
host.querySelector('[data-demo-mute]').addEventListener('click',()=>invoke(p=>p.mute()));
host.querySelectorAll('[data-demo-speed]').forEach(button=>button.addEventListener('click',()=>invoke(p=>p.speed(Number(button.dataset.demoSpeed)))));
document.querySelector('[data-demo-trigger]')?.addEventListener('click',event=>{
if(event.metaKey||event.ctrlKey||event.shiftKey||event.altKey)return;event.preventDefault();
host.scrollIntoView({block:'center',behavior:matchMedia('(prefers-reduced-motion:reduce)').matches?'instant':'smooth'});invoke(p=>p.play());
});
})()`;
}
