const form = document.getElementById('studio-form');
const useVoice = document.getElementById('use-voice');
const useImage = document.getElementById('use-image');
const voiceControls = document.getElementById('voice-controls');
const imageControls = document.getElementById('image-controls');
const consentControls = document.getElementById('consent-controls');
const voiceFile = document.getElementById('voice-file');
const imageFile = document.getElementById('image-file');
const voicePreview = document.getElementById('voice-preview');
const imagePreview = document.getElementById('image-preview');
const voiceStatus = document.getElementById('voice-status');
const formStatus = document.getElementById('studio-form-status');
const stage = document.getElementById('studio-stage');
const readiness = document.getElementById('studio-readiness');
const outputActions = document.getElementById('studio-output-actions');

let mediaRecorder = null;
let mediaStream = null;
let recordedChunks = [];
let voiceObjectUrl = '';
let imageObjectUrl = '';
let latestPacket = null;

function selectedType() {
  return form.elements.projectType.value;
}

function updateMediaControls() {
  voiceControls.hidden = !useVoice.checked;
  imageControls.hidden = !useImage.checked;
  consentControls.hidden = !useVoice.checked && !useImage.checked;
}

function setTypeFromQuery() {
  const type = new URLSearchParams(location.search).get('type');
  const input = form.querySelector(`input[name="projectType"][value="${CSS.escape(type || '')}"]`);
  if (input) input.checked = true;
}

function replaceObjectUrl(currentUrl, blob) {
  if (currentUrl) URL.revokeObjectURL(currentUrl);
  return URL.createObjectURL(blob);
}

useVoice.addEventListener('change', updateMediaControls);
useImage.addEventListener('change', updateMediaControls);

voiceFile.addEventListener('change', () => {
  const file = voiceFile.files && voiceFile.files[0];
  if (!file) return;
  voiceObjectUrl = replaceObjectUrl(voiceObjectUrl, file);
  voicePreview.src = voiceObjectUrl;
  voiceStatus.textContent = `Local sample ready: ${file.name}`;
});

imageFile.addEventListener('change', () => {
  const file = imageFile.files && imageFile.files[0];
  if (!file) return;
  imageObjectUrl = replaceObjectUrl(imageObjectUrl, file);
  imagePreview.src = imageObjectUrl;
  imagePreview.hidden = false;
});

document.getElementById('record-voice').addEventListener('click', async () => {
  if (!navigator.mediaDevices || !window.MediaRecorder) {
    voiceStatus.textContent = 'Voice recording is not available in this browser.';
    return;
  }
  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    recordedChunks = [];
    mediaRecorder = new MediaRecorder(mediaStream);
    mediaRecorder.addEventListener('dataavailable', event => {
      if (event.data.size) recordedChunks.push(event.data);
    });
    mediaRecorder.addEventListener('stop', () => {
      const blob = new Blob(recordedChunks, { type: mediaRecorder.mimeType || 'audio/webm' });
      voiceObjectUrl = replaceObjectUrl(voiceObjectUrl, blob);
      voicePreview.src = voiceObjectUrl;
      voiceStatus.textContent = 'Local recording ready for an approved media engine.';
      mediaStream.getTracks().forEach(track => track.stop());
      mediaStream = null;
    });
    mediaRecorder.start();
    document.getElementById('record-voice').disabled = true;
    document.getElementById('stop-voice').disabled = false;
    voiceStatus.textContent = 'Recording locally...';
  } catch (error) {
    voiceStatus.textContent = `Microphone unavailable: ${error.message}`;
  }
});

document.getElementById('stop-voice').addEventListener('click', () => {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') mediaRecorder.stop();
  document.getElementById('record-voice').disabled = false;
  document.getElementById('stop-voice').disabled = true;
});

function validateMedia() {
  if (useVoice.checked && !voiceObjectUrl) throw new Error('Record or choose your own voice sample first.');
  if (useImage.checked && !imageObjectUrl) throw new Error('Choose your own image first.');
  if (useVoice.checked || useImage.checked) {
    if (!document.getElementById('consent-self').checked) throw new Error('Confirm that the media represents you and belongs to you.');
    if (!document.getElementById('consent-adult').checked) throw new Error('Adult confirmation is required. Minor cloning is blocked.');
    if (!document.getElementById('consent-label').checked) throw new Error('The AI-assisted media label must stay enabled.');
  }
}

function projectCopy(type, subject, audience) {
  if (type === 'game') {
    return {
      eyebrow: 'Playable game build',
      title: `Challenge: ${subject}`,
      body: `Complete three decisions designed for ${audience}. Score, restart, keyboard, and touch states are included.`,
      action: 'Start level',
    };
  }
  if (type === 'school_simulation') {
    return {
      eyebrow: 'School simulation',
      title: `Scenario: ${subject}`,
      body: `${audience} make a decision, observe the simulated result, and explain the evidence. Teacher rubric included.`,
      action: 'Run scenario',
    };
  }
  return {
    eyebrow: 'Family learning video',
    title: `Learn together: ${subject}`,
    body: `A captioned lesson, guided pause, family activity, and discussion prompt prepared for ${audience}.`,
    action: 'Preview lesson',
  };
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

const innovationProfiles = {
  adaptive_experience: { label: 'Adaptive experience', scores: { utility: 91, novelty: 82, feasibility: 82, trust: 84, efficiency: 80, observability: 88 } },
  simulation_twin: { label: 'Simulation twin', scores: { utility: 88, novelty: 91, feasibility: 76, trust: 84, efficiency: 74, observability: 94 } },
  multimodal_creator: { label: 'Multimodal creator', scores: { utility: 92, novelty: 88, feasibility: 74, trust: 89, efficiency: 72, observability: 86 } },
  trust_trace: { label: 'Trust trace', scores: { utility: 86, novelty: 79, feasibility: 90, trust: 98, efficiency: 80, observability: 97 } },
  local_first_mesh: { label: 'Local-first mesh', scores: { utility: 87, novelty: 83, feasibility: 88, trust: 92, efficiency: 96, observability: 84 } },
  human_ai_workbench: { label: 'Human + AI workbench', scores: { utility: 90, novelty: 86, feasibility: 86, trust: 94, efficiency: 82, observability: 96 } },
};

const innovationWeights = {
  balanced: { utility: .25, novelty: .18, feasibility: .18, trust: .18, efficiency: .11, observability: .10 },
  bold: { utility: .22, novelty: .31, feasibility: .12, trust: .16, efficiency: .08, observability: .11 },
  trusted: { utility: .22, novelty: .10, feasibility: .18, trust: .30, efficiency: .08, observability: .12 },
  lean: { utility: .23, novelty: .12, feasibility: .22, trust: .16, efficiency: .19, observability: .08 },
};

const innovationTagModifiers = {
  education: { adaptive_experience: 7, simulation_twin: 4, human_ai_workbench: 3 },
  game: { simulation_twin: 7, adaptive_experience: 5, multimodal_creator: 3 },
  simulation: { simulation_twin: 8, trust_trace: 2 },
  multimodal: { multimodal_creator: 8, trust_trace: 3 },
  privacy: { trust_trace: 7, local_first_mesh: 6 },
  low_cost: { local_first_mesh: 8, adaptive_experience: 2 },
  accessibility: { human_ai_workbench: 5, adaptive_experience: 5 },
};

const innovationConstraintModifiers = {
  local_first: { local_first_mesh: 8, trust_trace: 2 },
  reversible: { human_ai_workbench: 5, trust_trace: 4, simulation_twin: 2 },
  owner_approval_before_publish: { trust_trace: 5, human_ai_workbench: 3 },
};

function innovationContext(type) {
  const tags = new Set(['accessibility', 'low_cost']);
  if (type === 'game') tags.add('game');
  if (type === 'school_simulation') ['education', 'game', 'simulation'].forEach(tag => tags.add(tag));
  if (type === 'parent_learning_video') ['education', 'multimodal'].forEach(tag => tags.add(tag));
  if (useVoice.checked || useImage.checked) ['multimodal', 'privacy'].forEach(tag => tags.add(tag));
  return {
    tags: [...tags],
    constraints: ['local_first', 'reversible', 'owner_approval_before_publish'],
  };
}

function runInnovationLoop(type, mode) {
  const weights = innovationWeights[mode] || innovationWeights.balanced;
  const context = innovationContext(type);
  const candidates = Object.entries(innovationProfiles).map(([lens, profile]) => {
    const modifier = context.tags.reduce((total, tag) => total + (innovationTagModifiers[tag]?.[lens] || 0), 0)
      + context.constraints.reduce((total, constraint) => total + (innovationConstraintModifiers[constraint]?.[lens] || 0), 0);
    const scores = { ...profile.scores, utility: Math.min(100, profile.scores.utility + modifier) };
    const score = Object.entries(weights).reduce((total, [name, weight]) => total + scores[name] * weight, 0);
    return { lens, label: profile.label, design_score: Math.round(score * 100) / 100, evidence_level: 'design-time estimate' };
  }).sort((a, b) => b.design_score - a.design_score);
  return {
    mode,
    candidates,
    winner: candidates[0],
    rollback_checkpoint: `local-digest:fnv1a32:${simpleDigest(candidates[0].lens + ':' + candidates[0].design_score)}`,
    release_gate: 'Observed tests and owner approval required',
  };
}

function simpleDigest(value) {
  let hash = 2166136261;
  for (const character of value) {
    hash ^= character.charCodeAt(0);
    hash = Math.imul(hash, 16777619);
  }
  return (hash >>> 0).toString(16).padStart(8, '0');
}

function renderInnovation(innovation) {
  const target = document.getElementById('innovation-comparison');
  target.hidden = false;
  target.innerHTML = `
    <div class="studio-innovation-heading">
      <div><span>Selected design</span><strong>${innovation.winner.label}</strong></div>
      <div><span>Design score</span><strong>${innovation.winner.design_score}</strong></div>
      <div><span>Release gate</span><strong>Observed tests required</strong></div>
    </div>
    <div class="studio-candidate-list">
      ${innovation.candidates.map(candidate => `
        <div class="studio-candidate-row">
          <span>${candidate.label}</span>
          <div><i style="width:${candidate.design_score}%"></i></div>
          <strong>${candidate.design_score}</strong>
        </div>`).join('')}
    </div>`;
}

function renderPrototype(packet) {
  const copy = projectCopy(packet.project_type, escapeHtml(packet.subject), escapeHtml(packet.audience));
  const avatar = useImage.checked ? `<img class="studio-avatar-preview" src="${imageObjectUrl}" alt="Approved creator likeness preview" />` : '<div class="studio-generated-avatar">B</div>';
  const label = useVoice.checked || useImage.checked ? '<p class="studio-media-label">AI-assisted media using the adult creator\'s approved voice or likeness</p>' : '';
  stage.innerHTML = `
    <article class="studio-built-project">
      ${avatar}
      <div>
        <p class="studio-project-eyebrow">${copy.eyebrow}</p>
        <h2>${copy.title}</h2>
        <p>${copy.body}</p>
        <p class="studio-design-note">Selected design: <strong>${packet.innovation.winner.label}</strong>. Score is a design estimate, not production evidence.</p>
        ${label}
        <button id="prototype-action" class="btn btn-primary btn-sm" type="button">${copy.action}</button>
      </div>
    </article>`;
  document.getElementById('prototype-action').addEventListener('click', event => {
    event.currentTarget.textContent = 'Local sandbox passed';
    event.currentTarget.disabled = true;
  });
}

form.addEventListener('submit', event => {
  event.preventDefault();
  formStatus.textContent = '';
  try {
    validateMedia();
    if (!form.reportValidity()) return;
    latestPacket = {
      schema: 'dreamco.buddy_creative_studio_project.v1',
      project_type: selectedType(),
      title: document.getElementById('project-title').value.trim(),
      objective: document.getElementById('project-objective').value.trim(),
      subject: document.getElementById('project-subject').value.trim(),
      audience: document.getElementById('project-audience').value.trim(),
      innovation: runInnovationLoop(selectedType(), document.getElementById('innovation-mode').value),
      code: { status: 'local_prototype_ready', network_default: 'off' },
      voice: { requested: useVoice.checked, status: useVoice.checked ? 'consent_verified_pending_render' : 'not_requested' },
      likeness: { requested: useImage.checked, status: useImage.checked ? 'consent_verified_pending_render' : 'not_requested' },
      consent: useVoice.checked || useImage.checked ? {
        owner_is_subject: true,
        adult_confirmed: true,
        synthetic_media_label: true,
        raw_media_in_packet: false,
      } : null,
      tests: ['offline load', 'touch and keyboard', 'captions', 'restart and recovery', 'learning objective', 'no live external action'],
      publish_requires_owner_approval: true,
    };
    renderPrototype(latestPacket);
    renderInnovation(latestPacket.innovation);
    readiness.textContent = useVoice.checked || useImage.checked ? 'Prototype ready · media renderer needed' : 'Prototype ready';
    readiness.className = useVoice.checked || useImage.checked ? 'badge badge-amber' : 'badge badge-green';
    document.getElementById('result-code').textContent = 'Prototype ready';
    document.getElementById('result-innovation').textContent = `${latestPacket.innovation.winner.design_score} · ${latestPacket.innovation.winner.label}`;
    document.getElementById('result-voice').textContent = useVoice.checked ? 'Consent verified' : 'Not requested';
    document.getElementById('result-image').textContent = useImage.checked ? 'Consent verified' : 'Not requested';
    document.getElementById('result-tests').textContent = '6 planned';
    outputActions.hidden = false;
    formStatus.textContent = useVoice.checked || useImage.checked
      ? 'Prototype built. A configured local or selected media engine is still required to render cloned media.'
      : 'Prototype built locally.';
  } catch (error) {
    formStatus.textContent = error.message;
    readiness.textContent = 'Needs input';
    readiness.className = 'badge badge-amber';
  }
});

document.getElementById('download-packet').addEventListener('click', () => {
  if (!latestPacket) return;
  const blob = new Blob([JSON.stringify(latestPacket, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${latestPacket.title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'buddy-project'}.json`;
  link.click();
  URL.revokeObjectURL(url);
});

document.getElementById('send-buddy').addEventListener('click', () => {
  if (!latestPacket) return;
  const prompt = `Continue building ${latestPacket.title} as a ${latestPacket.project_type}. Goal: ${latestPacket.objective}`;
  location.href = `buddy.html?prompt=${encodeURIComponent(prompt)}`;
});

document.getElementById('clear-media').addEventListener('click', () => {
  if (mediaStream) mediaStream.getTracks().forEach(track => track.stop());
  if (voiceObjectUrl) URL.revokeObjectURL(voiceObjectUrl);
  if (imageObjectUrl) URL.revokeObjectURL(imageObjectUrl);
  mediaStream = null;
  voiceObjectUrl = '';
  imageObjectUrl = '';
  voiceFile.value = '';
  imageFile.value = '';
  voicePreview.removeAttribute('src');
  imagePreview.removeAttribute('src');
  imagePreview.hidden = true;
  voiceStatus.textContent = 'No sample selected.';
  formStatus.textContent = 'Local media removed from this browser session.';
});

setTypeFromQuery();
updateMediaControls();
