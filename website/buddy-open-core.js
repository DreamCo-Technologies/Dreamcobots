(() => {
  const core = window.BUDDY_OPEN_MODEL_CODING_LAB.buddy_open_core;
  const byId = (id) => document.getElementById(id);
  const option = (value, label = value) => `<option value="${value}">${label}</option>`;
  const gates = ['Source and license reviewed','Checksums verified','Sandbox load passed','Same-fixture benchmarks passed','Hidden holdout passed','Security review passed'];
  let manifest = null;
  byId('architecture-count').textContent = core.architecture_profiles.length;
  byId('capability-count').textContent = core.capability_tracks.length;
  byId('architecture-grid').innerHTML = core.architecture_profiles.map((item) => `<article class="card"><h3>${item.label}</h3><p>${item.purpose}</p><small>Expert routing: ${item.requires_expert_routing ? 'required' : 'optional'} · MTP: ${item.requires_mtp ? 'required' : 'optional'}</small></article>`).join('');
  byId('api-grid').innerHTML = core.api_compatibility.map((item) => `<div class="card"><code>${item}</code></div>`).join('');
  byId('architecture').innerHTML = core.architecture_profiles.map((item) => option(item.id,item.label)).join('');
  byId('compute-tier').innerHTML = core.compute_tiers.map((item) => option(item.id,`${item.id}: ${item.target}`)).join('');
  byId('weight-format').innerHTML = core.weight_formats.map((item) => option(item)).join('');
  byId('quantization').innerHTML = core.quantization_targets.map((item) => option(item)).join('');
  byId('evidence-checks').innerHTML = gates.map((gate,index) => `<label><input type="checkbox" data-gate="${index}"> ${gate}</label>`).join('');
  byId('architecture').addEventListener('change', () => { const sparse = byId('architecture').value.startsWith('sparse_moe'); if (!sparse) byId('active-parameters').value = byId('parameters').value; });
  byId('core-form').addEventListener('submit', (event) => {
    event.preventDefault(); const total=Number(byId('parameters').value),active=Number(byId('active-parameters').value),sparse=byId('architecture').value.startsWith('sparse_moe');
    if (active>total || (sparse && active>=total) || (!sparse && active!==total)) { byId('core-status').textContent=sparse?'Sparse MoE requires active parameters below total parameters.':'Dense and distilled profiles require equal active and total parameters.'; return; }
    const evidence=[...document.querySelectorAll('[data-gate]')].map((input,index)=>({gate:gates[index],passed:input.checked}));
    manifest={schema:'dreamco.buddy_open_core_manifest.v1',release_id:byId('release-id').value,model_name:byId('model-name').value,architecture_profile:byId('architecture').value,compute_tier:byId('compute-tier').value,total_parameter_billions:total,active_parameter_billions:active,context_tokens:Number(byId('context').value),weight_format:byId('weight-format').value,quantization:byId('quantization').value,source:byId('source').value,immutable_revision:byId('revision').value,declared_license:byId('license').value,evidence,status:evidence.every((item)=>item.passed)?'release_candidate_owner_review_required':'evidence_gates_remaining',trained_weights_created:false,inference_executed:false};
    byId('download-manifest').disabled=false; byId('release-state').textContent=manifest.status.replaceAll('_',' '); byId('core-status').textContent=`Manifest validated locally: ${evidence.filter((item)=>item.passed).length}/${evidence.length} evidence gates passed. No model was downloaded, trained, or released.`;
  });
  byId('download-manifest').addEventListener('click',()=>{if(!manifest)return;const link=document.createElement('a');link.href=URL.createObjectURL(new Blob([JSON.stringify(manifest,null,2)],{type:'application/json'}));link.download=`${manifest.release_id}.json`;link.click();setTimeout(()=>URL.revokeObjectURL(link.href),500);});
})();
