(()=>{
  const $=id=>document.getElementById(id);
  const esc=value=>String(value).replace(/[&<>"']/g,character=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[character]));
  function route(raw){
    const text=raw.trim();if(!text){$('voice-status').textContent='Say or enter a command first.';return}
    const lower=text.toLowerCase();let target='buddy.html',params={prompt:text};
    if(/expert mode|seven.day sprint|learn.*resources|resource mastery|study.*resources/.test(lower)){target='buddy-expert-mode.html';params={goal:text}}
    else if(/invention|prototype|prior art|patent|idea to store|manufacturer|build my product/.test(lower)){target='buddy-invention-lab.html';params={idea:text}}
    else if(/family circle|consented family|safe place|check me in|missing-child/.test(lower)){target='family-circle.html';params={command:text}}
    else if(/food|rent.*help|utility help|childcare|transportation help|mental health|government office/.test(lower)){target='resource-211.html';params={need:text}}
    else if(/map|show|place|mark|note|remember|route|home|property|rental|hiring|jobs|inspector|repair|fire|earthquake|transit|weather|infrastructure|source|fresh|provider|mission/.test(lower)){target='world-lens.html';const category=/rental/.test(lower)?'rentals':/home|property/.test(lower)?'property_sale':/hiring|jobs/.test(lower)?'jobs':/food/.test(lower)?'food':/transit/.test(lower)?'transit':'any';params={q:text,category}}
    $('voice-status').textContent=`Prepared for ${target.replace('.html','').replaceAll('-',' ')}. Opening now…`;location.href=`${target}?${new URLSearchParams(params)}`;
  }
  fetch('data/buddy-world-lens-voice-commands.json',{cache:'no-store'}).then(response=>{if(!response.ok)throw Error(`catalog returned ${response.status}`);return response.json()}).then(data=>{$('voice-groups').innerHTML=data.groups.map(group=>`<article class="card"><h2>${esc(group.name)}</h2>${group.commands.map(command=>`<button class="command" data-command="${esc(command)}">${esc(command)}</button>`).join('')}</article>`).join('')}).catch(error=>{$('voice-status').textContent=`Command catalog unavailable: ${error.message}`});
  $('voice-groups').onclick=event=>{const command=event.target.dataset.command;if(command){$('voice-input').value=command;$('voice-status').textContent='Example selected. Replace words in braces, then run it.'}};
  $('voice-run').onclick=()=>route($('voice-input').value);
  $('voice-listen').onclick=()=>{const Recognition=window.SpeechRecognition||window.webkitSpeechRecognition;if(!Recognition){$('voice-status').textContent='Voice recognition is unavailable in this browser; type the command.';return}const recognition=new Recognition();recognition.lang=navigator.language||'en-US';recognition.interimResults=false;recognition.onresult=event=>{const text=event.results[0][0].transcript.trim();$('voice-input').value=text;route(text)};recognition.onerror=event=>{$('voice-status').textContent=`Voice error: ${event.error}`};$('voice-status').textContent='Listening for one Buddy command…';recognition.start()};
})();
