/* Shared actions for page information. Ordinary text remains readable and selectable. */
(() => {
  'use strict';
  if(window.DreamcoRepositoryActions)return;
  window.DreamcoRepositoryActions=true;
  const base=new URL('.',document.currentScript.src);
  const site=path=>new URL(path,base).href;
  const page=decodeURIComponent(location.pathname.split('/').pop()||'index.html');
  const css=document.createElement('link');css.rel='stylesheet';css.href=site('repository-actions.css');document.head.append(css);
  const el=(tag,text)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;return n;};
  const link=(label,url)=>{const a=el('a',label);a.className='rw-button';a.href=url;return a;};
  const button=(label,fn)=>{const b=el('button',label);b.type='button';b.className='rw-button';b.addEventListener('click',fn);return b;};
  function explore(title,content){
    const d=el('dialog');d.className='rw-dialog';const close=button('Close',()=>d.close());d.append(close,el('h2',title),el('p',content||'Use the source page and ask Buddy to explain this section.'));
    const controls=el('div');controls.className='rw-controls';
    controls.append(link('Explain with Buddy',site('buddy.html?prompt='+encodeURIComponent(`Explain this for a beginner on ${page}: ${title}. Context: ${content}. Separate source facts from plans and suggest one small next step.`))),link('Find related files',site('buddy-command-center.html?view=files&q='+encodeURIComponent(title))),link('Plan a change to this page',site('buddy-command-center.html?file='+encodeURIComponent('website/'+page))));d.append(controls);document.body.append(d);d.addEventListener('close',()=>d.remove());d.showModal();
  }
  function init(){
    const dock=el('nav');dock.className='rw-page-dock';dock.setAttribute('aria-label','Buddy repository controls');
    const controls=el('div');controls.className='rw-controls';let selected='';let infoMode=false;
    document.addEventListener('click',event=>{
      if(!infoMode||event.target.closest('a,button,input,textarea,select,.rw-dialog,.rw-shell,.rw-page-dock'))return;
      const target=event.target.closest('p,li,dt,dd,td,th,pre,code,span,strong,h1,h2,h3,h4,h5,h6');
      if(target&&target.textContent.trim()){event.preventDefault();explore('Page information',target.textContent.trim().slice(0,1500));}
    });
    const mode=button('Explore info mode: off',()=>{infoMode=!infoMode;mode.textContent='Explore info mode: '+(infoMode?'on':'off');mode.setAttribute('aria-pressed',String(infoMode));document.body.classList.toggle('rw-information-mode',infoMode);});mode.setAttribute('aria-pressed','false');controls.append(mode);
    document.addEventListener('selectionchange',()=>{const selection=String(window.getSelection()||'').trim();if(selection)selected=selection.slice(0,1500);});
    controls.append(link('Command center',site('buddy-command-center.html')),link('All pages',site('buddy-command-center.html?view=pages')),link('All files',site('buddy-command-center.html?view=files')),link('Bot portfolios',site('buddy-command-center.html?view=bots')),button('Explore selected text',()=>explore('Selected information',selected||'Select text on this page first, then use this button.')),link('Manage this page',site('buddy-command-center.html?file='+encodeURIComponent('website/'+page))));dock.append(controls);
    const main=document.querySelector('main')||document.querySelector('body > .container')||document.body;main.prepend(dock);
    if(['buddy-command-center.html','dashboard.html'].includes(page)){
      const mount=el('section');mount.id='repository-workbench';dock.after(mount);const script=el('script');script.src=site('repository-workbench.js');document.body.append(script);
    }
    function connectInfo(){
      document.querySelectorAll('h2,h3').forEach(heading=>{
        if(heading.dataset.repoInfo||heading.closest('.rw-shell,.rw-dialog,.rw-page-dock,.buddy-page-actions'))return;
        heading.dataset.repoInfo='true';const title=heading.textContent.trim();if(!title)return;
        const b=button('Explore info',()=>{let text='';let n=heading.nextElementSibling;for(let i=0;n&&i<3;i++,n=n.nextElementSibling){if(/^H[1-3]$/.test(n.tagName))break;text+=' '+n.textContent;}explore(title,text.trim().slice(0,1500));});b.className='rw-info-button';b.setAttribute('aria-label','Explore '+title);heading.append(b);
      });
    }
    connectInfo();let scheduled=false;new MutationObserver(()=>{if(scheduled)return;scheduled=true;requestAnimationFrame(()=>{scheduled=false;connectInfo();});}).observe(document.body,{childList:true,subtree:true});
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
