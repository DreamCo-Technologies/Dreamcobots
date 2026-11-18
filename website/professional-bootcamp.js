export function promotionCheck({baseline,candidate,holdout,regression,repetitions}){
  const values=[baseline,candidate,holdout,regression,repetitions].map(Number);
  if(values.some(value=>!Number.isFinite(value)||value<0))throw new Error('Benchmark values must be nonnegative numbers.');
  if([baseline,candidate,holdout,regression].some(value=>Number(value)>100))throw new Error('Scores must be 0 to 100.');
  const checks={repetitions:Number(repetitions)>=3,improvement:Number(candidate)-Number(baseline)>=5,holdout:Number(holdout)>=75,regression:Number(regression)<=2};
  return {promote:Object.values(checks).every(Boolean),checks};
}

export function trainingHandoff(values){
  if(!values.rightsVerified)throw new Error('Verify the model and dataset rights first.');
  if(!/^[a-f0-9]{64}$/i.test(values.datasetSha256||''))throw new Error('Dataset hash must be a 64-character SHA-256.');
  if(!(Number(values.maxCostUsd)>0))throw new Error('Set a positive cost ceiling.');
  return {schema:'dreamco.professional_training_handoff.v1',base_model_and_revision:values.baseModel,method:values.method,dataset_sha256:values.datasetSha256,hardware:values.hardware,max_cost_usd:Number(values.maxCostUsd),private_output_repository:values.outputRepo,required_splits:['train','validation','hidden_test'],monitoring:'Trackio or equivalent',status:'manifest_only_no_job_submitted',weights_trained:false};
}

function download(name,data){const blob=new Blob([JSON.stringify(data,null,2)+'\n'],{type:'application/json'});const link=document.createElement('a');link.href=URL.createObjectURL(blob);link.download=name;link.click();URL.revokeObjectURL(link.href);}

if(typeof document!=='undefined'){
  let taskPacket=null;
  fetch('data/professional-bootcamp.json').then(response=>{if(!response.ok)throw new Error(`HTTP ${response.status}`);return response.json();}).then(data=>{
    document.getElementById('truth-status').textContent=`${data.tracks.length} tracks · ${data.truth.trained_weight_artifacts} trained weight artifacts · ${data.truth.professional_deployments_verified} verified deployments`;
    const tracks=document.getElementById('tracks');
    data.tracks.forEach(track=>{const article=document.createElement('article');article.className='track-card';const title=document.createElement('h3');title.textContent=track.label;const text=document.createElement('p');text.textContent=track.practice.join(' → ');const button=document.createElement('button');button.className='btn btn-outline';button.type='button';button.textContent='Choose track';button.addEventListener('click',()=>{document.querySelectorAll('.track-card').forEach(node=>node.classList.remove('selected-track'));article.classList.add('selected-track');document.getElementById('task-goal').focus();});article.append(title,text,button);tracks.append(article);});
    const pad=document.getElementById('gesture-pad');data.gesture_control.commands.forEach(command=>{const button=document.createElement('button');button.type='button';button.className='btn btn-outline';button.textContent=command.replaceAll('_',' ');button.addEventListener('click',()=>document.getElementById('gesture-result').textContent=`Mapped command: ${command}. Simulation only; camera remains off and no task was executed.`);pad.append(button);});
  }).catch(error=>document.getElementById('truth-status').textContent=`Contract unavailable: ${error.message}`);

  document.getElementById('task-form').addEventListener('submit',event=>{event.preventDefault();if(!document.getElementById('task-consent').checked)return;taskPacket={schema:'dreamco.professional_task_example.draft.v1',profession:document.getElementById('profession').value.trim(),goal:document.getElementById('task-goal').value.trim(),wrapper_and_revision:document.getElementById('wrapper').value.trim(),verified_result:document.getElementById('task-result').value.trim(),customization:document.getElementById('customization').value.trim(),attestations:{capture_consent:true,training_consent:true,rights_verified:true,redacted:true},status:'draft_requires_runtime_validation'};document.getElementById('task-output').textContent=JSON.stringify(taskPacket,null,2);document.getElementById('download-task').disabled=false;});
  document.getElementById('download-task').addEventListener('click',()=>taskPacket&&download('buddy-task-example.json',taskPacket));
  document.getElementById('benchmark-form').addEventListener('submit',event=>{event.preventDefault();try{const result=promotionCheck({baseline:document.getElementById('baseline').value,candidate:document.getElementById('candidate').value,holdout:document.getElementById('holdout').value,regression:document.getElementById('regression').value,repetitions:document.getElementById('repetitions').value});document.getElementById('benchmark-result').textContent=result.promote?'Promotion gate passed for the entered evidence. Preserve the underlying run records for review.':`Promotion blocked: ${Object.entries(result.checks).filter(([,passed])=>!passed).map(([name])=>name).join(', ')}.`;}catch(error){document.getElementById('benchmark-result').textContent=error.message;}});
  document.getElementById('training-form').addEventListener('submit',event=>{event.preventDefault();try{const result=trainingHandoff({baseModel:document.getElementById('base-model').value.trim(),method:document.getElementById('method').value,datasetSha256:document.getElementById('dataset-hash').value.trim(),hardware:document.getElementById('hardware').value.trim(),maxCostUsd:document.getElementById('max-cost').value,outputRepo:document.getElementById('output-repo').value.trim(),rightsVerified:document.getElementById('rights').checked});document.getElementById('training-output').textContent=JSON.stringify(result,null,2);}catch(error){document.getElementById('training-output').textContent=error.message;}});
}
