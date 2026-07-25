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
const imageCamera = document.getElementById('image-camera');
const imageCanvas = document.getElementById('image-canvas');
const voiceStatus = document.getElementById('voice-status');
const imageStatus = document.getElementById('image-status');
const formStatus = document.getElementById('studio-form-status');
const stage = document.getElementById('studio-stage');
const readiness = document.getElementById('studio-readiness');
const outputActions = document.getElementById('studio-output-actions');
const academyTrack = document.getElementById('academy-track');
const academyGrid = document.getElementById('academy-grid');
const academySummary = document.getElementById('academy-summary');
const actorControls = document.getElementById('actor-controls');
const actorMode = document.getElementById('actor-mode');
const simulationControls = document.getElementById('simulation-controls');
const simulationModelSource = document.getElementById('simulation-model-source');
const simulationFidelity = document.getElementById('simulation-fidelity');
const simulationPaint = document.getElementById('simulation-paint');
const simulationAdditions = document.getElementById('simulation-additions');
const simulationToGame = document.getElementById('simulation-to-game');

let mediaRecorder = null;
let mediaStream = null;
let imageStream = null;
let recordedChunks = [];
let recordingTimer = null;
let voiceBlob = null;
let imageBlob = null;
let voiceObjectUrl = '';
let imageObjectUrl = '';
let latestPacket = null;
let latestConsentReceipt = null;
const academy = window.BUDDY_SPECIALIZED_HUBS?.creative;
const productionRegistry = window.BUDDY_PRODUCTION_GROUP;
const hollywoodGroup = productionRegistry?.hollywood_production_group;
const simulationFoundry = productionRegistry?.simulation_foundry;

function academyCard(index, label, items, kind) {
  const card = document.createElement('article');
  card.className = 'studio-academy-card';
  const step = document.createElement('small');
  step.textContent = `${kind} ${index + 1}`;
  const heading = document.createElement('h3');
  heading.textContent = label;
  const list = document.createElement('ul');
  items.forEach(item => {
    const row = document.createElement('li');
    row.textContent = item;
    list.append(row);
  });
  card.append(step, heading, list);
  return card;
}

function renderAcademy() {
  academyGrid.replaceChildren();
  if (!academy) {
    academySummary.textContent = 'Production academy catalog is unavailable.';
    return;
  }
  if (academyTrack.value === 'film') {
    const rows = hollywoodGroup?.departments || academy.film_standard.phases;
    rows.forEach((row, index) => academyGrid.append(academyCard(index, row.label, row.outputs, row.lead_bot ? 'Department' : 'Phase')));
    academySummary.textContent = hollywoodGroup
      ? `${rows.length} production departments · ${hollywoodGroup.quality_gates.length} picture, sound, rights, accessibility, and master quality gates · rendered evidence required`
      : `${rows.length} production phases · ${academy.film_standard.quality_gates.length} release gates · delivery specs verified for each target platform`;
  } else if (academyTrack.value === 'music') {
    const rows = academy.music_standard.genre_families;
    rows.forEach((row, index) => academyGrid.append(academyCard(index, row.label, row.study, 'Family')));
    academySummary.textContent = `${rows.length} genre families · original composition workflow · composition, recording, sample, performance, sync, voice, and likeness rights gates`;
  } else {
    const rows = simulationFoundry?.domains || [];
    rows.forEach((row, index) => academyGrid.append(academyCard(index, row.label, [row.review], 'Domain')));
    academySummary.textContent = `${rows.length} simulation domains · ${simulationFoundry?.model_sources?.length || 0} governed model sources · every simulation can produce a deterministic practice-game plan`;
  }
}

const TYPE_PRESETS = {
  game: {
    title: 'Fraction Quest',
    objective: 'Teach learners to compare fractions through a playable kitchen challenge.',
    subject: 'Fraction comparison',
    audience: 'Ages 9 to 11',
  },
  school_simulation: {
    title: 'Ecosystem Lab',
    objective: 'Let students test how resource changes affect a balanced virtual ecosystem.',
    subject: 'Food webs and ecosystem balance',
    audience: 'Grades 6 to 8',
  },
  parent_learning_video: {
    title: 'Family Science Night',
    objective: 'Create a short family lesson with a safe hands-on activity and discussion prompts.',
    subject: 'Everyday states of matter',
    audience: 'Families with children ages 7 to 10',
  },
  music_video: {
    title: 'City Lights',
    objective: 'Create a rights-aware music video treatment with a visual story and edit plan.',
    subject: 'An original song about finding confidence',
    audience: 'Independent music audiences',
  },
  biography: {
    title: 'My Story',
    objective: 'Create a sourced personal biography with a clear chronology and archive plan.',
    subject: 'A life story built from approved memories and records',
    audience: 'Family, friends, and future generations',
  },
  commercial: {
    title: 'Launch Story',
    objective: 'Create a truthful product commercial with substantiated claims and platform variants.',
    subject: 'A customer-focused product introduction',
    audience: 'Prospective customers',
  },
  college_course: {
    title: 'Applied AI Foundations',
    objective: 'Build a college course with measurable outcomes, labs, assessments, and rubrics.',
    subject: 'Responsible applied artificial intelligence',
    audience: 'First-year college learners',
  },
  feature_film: {
    title: 'Crossing Tomorrow',
    objective: 'Develop an original feature film package with a screenplay, continuity plan, production breakdown, and delivery specification.',
    subject: 'An original human story designed for responsible production',
    audience: 'Film audiences and production partners',
  },
  music_artist: {
    title: 'First Light Artist Plan',
    objective: 'Build an original artist identity, repertoire plan, rights manifest, release calendar, and audience test program.',
    subject: 'Original songs and a distinct artist identity',
    audience: 'Independent music listeners and collaborators',
  },
  logo_brand: {
    title: 'Signal Brand System',
    objective: 'Create editable original logo concepts, brand guidelines, a rights manifest, and a trademark search plan.',
    subject: 'A clear and accessible original brand identity',
    audience: 'Customers, partners, and product users',
  },
  invention_prototype: {
    title: 'Accessible Garden Monitor',
    objective: 'Design and test a low-power garden sensor with accessible alerts, replaceable parts, and a bounded prototype budget.',
    subject: 'Sensor, enclosure, local dashboard, and alert workflow',
    audience: 'Home gardeners with varied access needs',
  },
  vehicle_simulation: {
    title: 'Garage Practice Lab',
    objective: 'Build an owner-authorized vehicle inspection, repair-practice, paint, and addition simulation with measured limits and qualified-review gates.',
    subject: 'Vehicle inspection, repair sequence, paint, parts, and accessory variants',
    audience: 'Adult vehicle owners and qualified instructors',
  },
  building_simulation: {
    title: 'Home Design Lab',
    objective: 'Compare an owner-authorized home addition, materials, rooms, and construction sequence against measured site and building constraints.',
    subject: 'Home design, room addition, materials, utilities, and construction practice',
    audience: 'Property owners, learners, and qualified building professionals',
  },
  product_visualization: {
    title: 'Product Variant Lab',
    objective: 'Visualize an original product or invention with paint, material, component, and accessory variants plus a bench-test plan.',
    subject: 'Product model, materials, components, additions, and before-and-after comparison',
    audience: 'Inventors, customers, and product teams',
  },
  skills_training_simulation: {
    title: 'Practice Workshop',
    objective: 'Turn an approved procedure into a simulation game with legal actions, feedback, levels, safe failure, reset, and an after-action review.',
    subject: 'Owner-authorized job, classroom, equipment, or life-skill practice',
    audience: 'Learners and qualified instructors',
  },
};

const SIMULATION_TYPES = new Set([
  'vehicle_simulation',
  'building_simulation',
  'product_visualization',
  'skills_training_simulation',
]);
const ACTOR_TYPES = new Set(['feature_film', 'music_video', 'commercial', 'parent_learning_video', 'biography']);

function selectedType() {
  return form.elements.projectType.value;
}

function renderEmptyState(type) {
  const preset = TYPE_PRESETS[type];
  if (!preset) return;
  stage.innerHTML = `
    <div class="studio-stage-empty">
      <span>B</span>
      <h2>${escapeHtml(preset.title)}</h2>
      <p>Build the local ${escapeHtml(type.replaceAll('_', ' '))} prototype to open its governed preview.</p>
    </div>`;
  latestPacket = null;
  readiness.textContent = 'Ready to build';
  readiness.className = 'badge badge-green';
  document.getElementById('result-code').textContent = 'Waiting';
  document.getElementById('result-voice').textContent = 'Not requested';
  document.getElementById('result-image').textContent = 'Not requested';
  document.getElementById('result-tests').textContent = 'Waiting';
  outputActions.hidden = true;
}

function applyPreset(type) {
  const preset = TYPE_PRESETS[type];
  if (!preset) return;
  document.getElementById('project-title').value = preset.title;
  document.getElementById('project-objective').value = preset.objective;
  document.getElementById('project-subject').value = preset.subject;
  document.getElementById('project-audience').value = preset.audience;
  updateProjectControls(type);
  renderEmptyState(type);
}

function updateProjectControls(type = selectedType()) {
  actorControls.hidden = !ACTOR_TYPES.has(type);
  simulationControls.hidden = !SIMULATION_TYPES.has(type);
  renderSimulationConcept();
}

function renderSimulationConcept() {
  if (!simulationPaint) return;
  document.getElementById('simulation-color-swatch').style.background = simulationPaint.value;
  const sourceLabel = simulationModelSource.options[simulationModelSource.selectedIndex]?.text || 'Model';
  const fidelityLabel = simulationFidelity.options[simulationFidelity.selectedIndex]?.text || 'Concept';
  document.getElementById('simulation-preview-title').textContent = TYPE_PRESETS[selectedType()]?.title || 'Concept variant';
  document.getElementById('simulation-preview-detail').textContent = `${sourceLabel} · ${fidelityLabel} · game conversion ${simulationToGame.checked ? 'on' : 'off'} · render engine not connected`;
}

function updateMediaControls() {
  voiceControls.hidden = !useVoice.checked;
  imageControls.hidden = !useImage.checked;
  consentControls.hidden = !useVoice.checked && !useImage.checked;
}

function setTypeFromQuery() {
  const type = new URLSearchParams(location.search).get('type');
  const select = document.getElementById('project-type');
  if (type && Array.from(select.options).some(option => option.value === type)) {
    select.value = type;
  }
  applyPreset(select.value);
}

function replaceObjectUrl(currentUrl, blob) {
  if (currentUrl) URL.revokeObjectURL(currentUrl);
  return URL.createObjectURL(blob);
}

function mediaExtension(blob, fallback) {
  const subtype = String(blob?.type || '').split('/')[1]?.split(';')[0]?.replace('jpeg', 'jpg');
  return subtype && /^[a-z0-9.+-]+$/i.test(subtype) ? subtype : fallback;
}

function downloadBlob(blob, filename) {
  if (!blob) return;
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

async function blobFingerprint(blob) {
  if (!blob || !window.crypto?.subtle) return null;
  const digest = await crypto.subtle.digest('SHA-256', await blob.arrayBuffer());
  return [...new Uint8Array(digest)].map(value => value.toString(16).padStart(2, '0')).join('');
}

async function textFingerprint(value) {
  const normalized = String(value || '').trim();
  if (!normalized || !window.crypto?.subtle) return null;
  const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(normalized));
  return [...new Uint8Array(digest)].map(item => item.toString(16).padStart(2, '0')).join('');
}

function stopImageCamera() {
  if (imageStream) imageStream.getTracks().forEach(track => track.stop());
  imageStream = null;
  imageCamera.srcObject = null;
  imageCamera.hidden = true;
  document.getElementById('start-camera').disabled = false;
  document.getElementById('take-photo').disabled = true;
  document.getElementById('stop-camera').disabled = true;
}

useVoice.addEventListener('change', updateMediaControls);
useImage.addEventListener('change', updateMediaControls);
document.getElementById('project-type').addEventListener('change', event => applyPreset(event.target.value));
actorMode.addEventListener('change', () => {
  if (actorMode.value === 'owner_digital_double') {
    formStatus.textContent = 'Choose your voice, likeness, or both below and complete the adult owner consent controls.';
  } else {
    formStatus.textContent = 'Original actor mode cannot imitate or use source media from a real person.';
  }
});
[simulationModelSource, simulationFidelity, simulationPaint, simulationAdditions, simulationToGame]
  .forEach(control => control.addEventListener('input', renderSimulationConcept));

voiceFile.addEventListener('change', () => {
  const file = voiceFile.files && voiceFile.files[0];
  if (!file) return;
  if (!file.type.startsWith('audio/') || file.size > 50 * 1024 * 1024) {
    voiceStatus.textContent = 'Choose an audio file no larger than 50 MB.';
    voiceFile.value = '';
    return;
  }
  voiceBlob = file;
  voiceObjectUrl = replaceObjectUrl(voiceObjectUrl, file);
  voicePreview.src = voiceObjectUrl;
  document.getElementById('download-voice').disabled = false;
  voiceStatus.textContent = `Local sample ready: ${file.name}`;
});

imageFile.addEventListener('change', () => {
  const file = imageFile.files && imageFile.files[0];
  if (!file) return;
  if (!file.type.startsWith('image/') || file.size > 20 * 1024 * 1024) {
    imageStatus.textContent = 'Choose an image no larger than 20 MB.';
    imageFile.value = '';
    return;
  }
  imageBlob = file;
  imageObjectUrl = replaceObjectUrl(imageObjectUrl, file);
  imagePreview.src = imageObjectUrl;
  imagePreview.hidden = false;
  document.getElementById('download-image').disabled = false;
  imageStatus.textContent = `Local image ready: ${file.name}`;
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
      if (recordingTimer) clearTimeout(recordingTimer);
      voiceBlob = new Blob(recordedChunks, { type: mediaRecorder.mimeType || 'audio/webm' });
      voiceObjectUrl = replaceObjectUrl(voiceObjectUrl, voiceBlob);
      voicePreview.src = voiceObjectUrl;
      document.getElementById('download-voice').disabled = false;
      voiceStatus.textContent = 'Local recording ready for an approved media engine.';
      if (mediaStream) mediaStream.getTracks().forEach(track => track.stop());
      mediaStream = null;
      document.getElementById('record-voice').disabled = false;
      document.getElementById('stop-voice').disabled = true;
    });
    mediaRecorder.start();
    recordingTimer = setTimeout(() => {
      if (mediaRecorder && mediaRecorder.state !== 'inactive') mediaRecorder.stop();
    }, 60_000);
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

document.getElementById('start-camera').addEventListener('click', async () => {
  if (!navigator.mediaDevices?.getUserMedia) {
    imageStatus.textContent = 'Camera capture is not available in this browser.';
    return;
  }
  try {
    imageStream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'user', width: { ideal: 1280 }, height: { ideal: 720 } },
      audio: false,
    });
    imageCamera.srcObject = imageStream;
    imageCamera.hidden = false;
    document.getElementById('start-camera').disabled = true;
    document.getElementById('take-photo').disabled = false;
    document.getElementById('stop-camera').disabled = false;
    imageStatus.textContent = 'Camera is on locally. Take a photo or close it.';
  } catch (error) {
    imageStatus.textContent = `Camera unavailable: ${error.message}`;
  }
});

document.getElementById('take-photo').addEventListener('click', () => {
  if (!imageStream || !imageCamera.videoWidth || !imageCamera.videoHeight) {
    imageStatus.textContent = 'Wait for the camera preview before taking a photo.';
    return;
  }
  const scale = Math.min(1, 1280 / imageCamera.videoWidth, 720 / imageCamera.videoHeight);
  imageCanvas.width = Math.max(1, Math.round(imageCamera.videoWidth * scale));
  imageCanvas.height = Math.max(1, Math.round(imageCamera.videoHeight * scale));
  imageCanvas.getContext('2d').drawImage(imageCamera, 0, 0, imageCanvas.width, imageCanvas.height);
  imageCanvas.toBlob((blob) => {
    if (!blob) {
      imageStatus.textContent = 'The camera image could not be created.';
      return;
    }
    imageBlob = blob;
    imageObjectUrl = replaceObjectUrl(imageObjectUrl, blob);
    imagePreview.src = imageObjectUrl;
    imagePreview.hidden = false;
    document.getElementById('download-image').disabled = false;
    imageStatus.textContent = 'Local camera image ready.';
    stopImageCamera();
  }, 'image/jpeg', 0.92);
});

document.getElementById('stop-camera').addEventListener('click', () => {
  stopImageCamera();
  imageStatus.textContent = imageBlob ? 'Camera closed. Local image is ready.' : 'Camera closed without saving an image.';
});

document.getElementById('download-voice').addEventListener('click', () => {
  downloadBlob(voiceBlob, `buddy-owner-voice.${mediaExtension(voiceBlob, 'webm')}`);
});

document.getElementById('download-image').addEventListener('click', () => {
  downloadBlob(imageBlob, `buddy-owner-image.${mediaExtension(imageBlob, 'jpg')}`);
});

function validateMedia() {
  if (!actorControls.hidden && actorMode.value === 'owner_digital_double' && !useVoice.checked && !useImage.checked) {
    throw new Error('Choose your own voice, likeness, or both for an owner digital double.');
  }
  if (useVoice.checked && !voiceObjectUrl) throw new Error('Record or choose your own voice sample first.');
  if (useImage.checked && !imageObjectUrl) throw new Error('Choose your own image first.');
  if (useVoice.checked || useImage.checked) {
    if (!document.getElementById('consent-self').checked) throw new Error('Confirm that the media represents you and belongs to you.');
    if (!document.getElementById('consent-adult').checked) throw new Error('Adult confirmation is required. Minor cloning is blocked.');
    if (!document.getElementById('consent-label').checked) throw new Error('The AI-assisted media label must stay enabled.');
  }
}

function validateSimulation() {
  if (simulationControls.hidden) return;
  const source = simulationModelSource.value;
  const modelRef = document.getElementById('simulation-model-ref').value.trim();
  const rightsRef = document.getElementById('simulation-rights-ref').value.trim();
  if (source !== 'procedural_original' && (!modelRef || !rightsRef)) {
    throw new Error('Imported or scanned models require both a model reference and an ownership or license receipt.');
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
  if (type === 'parent_learning_video') return {
    eyebrow: 'Family learning video',
    title: `Learn together: ${subject}`,
    body: `A captioned lesson, guided pause, family activity, and discussion prompt prepared for ${audience}.`,
    action: 'Preview lesson',
  };
  if (type === 'music_video') return {
    eyebrow: 'Music video production',
    title: `Treatment: ${subject}`,
    body: `A rights-aware treatment, scene plan, shot list, edit timeline, and labeled creator-media workflow for ${audience}.`,
    action: 'Preview treatment',
  };
  if (type === 'biography') return {
    eyebrow: 'Sourced biography',
    title: `Life story: ${subject}`,
    body: `A source log, chronology, narrative structure, fact review, and archive-rights plan prepared for ${audience}.`,
    action: 'Preview chapter',
  };
  if (type === 'commercial') return {
    eyebrow: 'Commercial production',
    title: `Campaign: ${subject}`,
    body: `A truthful concept, substantiated claims, script, shot list, format variants, and measurement plan for ${audience}.`,
    action: 'Preview campaign',
  };
  if (type === 'feature_film') return {
    eyebrow: 'Feature film development',
    title: `Production: ${subject}`,
    body: `An original screenplay, continuity bible, production breakdown, rights log, edit plan, and delivery specification for ${audience}.`,
    action: 'Preview sequence',
  };
  if (type === 'music_artist') return {
    eyebrow: 'Artist development',
    title: `Artist plan: ${subject}`,
    body: `An original repertoire, production workflow, rights and split manifest, release calendar, and audience test plan for ${audience}.`,
    action: 'Preview release plan',
  };
  if (type === 'logo_brand') return {
    eyebrow: 'Logo and brand system',
    title: `Identity: ${subject}`,
    body: `Editable original concepts, brand guidelines, accessibility checks, rights records, and a clearance search plan for ${audience}.`,
    action: 'Preview identity',
  };
  if (type === 'invention_prototype') return {
    eyebrow: 'Invention workbench',
    title: `Prototype: ${subject}`,
    body: `Requirements, system architecture, component options, bill of materials, prior-art research, safety review, simulation, and a bench-test matrix prepared for ${audience}.`,
    action: 'Review test plan',
  };
  if (type === 'vehicle_simulation') return {
    eyebrow: 'Vehicle simulation foundry',
    title: `Garage lab: ${subject}`,
    body: `An owner-authorized model, paint and addition variants, measured assumptions, repair-practice loop, fitment review, and qualified safety gates prepared for ${audience}.`,
    action: 'Run concept scenario',
  };
  if (type === 'building_simulation') return {
    eyebrow: 'Building simulation foundry',
    title: `Design lab: ${subject}`,
    body: `A site and building model plan, material and addition variants, walkthrough, construction sequence, and code, structure, utility, fire, and access review prepared for ${audience}.`,
    action: 'Run concept walkthrough',
  };
  if (type === 'product_visualization') return {
    eyebrow: 'Product simulation foundry',
    title: `Variant lab: ${subject}`,
    body: `A rights-aware model plan, paint, material, component, and accessory variants, comparison views, tolerances, failure modes, and bench-test evidence prepared for ${audience}.`,
    action: 'Compare concept variants',
  };
  if (type === 'skills_training_simulation') return {
    eyebrow: 'Simulation-to-game workshop',
    title: `Practice game: ${subject}`,
    body: `A bounded state model, legal actions, feedback, scoring, difficulty ladder, safe failure, reset, bot playtest, and instructor controls prepared for ${audience}.`,
    action: 'Start practice loop',
  };
  return {
    eyebrow: 'College course production',
    title: `Course: ${subject}`,
    body: `A syllabus, outcomes, modules, labs, assessments, rubrics, and accessible lecture plan prepared for ${audience}.`,
    action: 'Preview module',
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

function renderPrototype(packet) {
  const copy = projectCopy(packet.project_type, escapeHtml(packet.subject), escapeHtml(packet.audience));
  const simulation = SIMULATION_TYPES.has(packet.project_type);
  const avatar = useImage.checked
    ? `<img class="studio-avatar-preview" src="${imageObjectUrl}" alt="Approved creator likeness preview" />`
    : simulation
      ? `<div class="studio-generated-avatar" style="background:${escapeHtml(packet.simulation.paint)}">SIM</div>`
      : '<div class="studio-generated-avatar">B</div>';
  const label = useVoice.checked || useImage.checked ? '<p class="studio-media-label">AI-assisted media using the adult creator\'s approved voice or likeness</p>' : '';
  const manifest = [
    packet.actor?.mode ? `Actor: ${packet.actor.mode.replaceAll('_', ' ')}` : null,
    packet.simulation?.model_source ? `Model: ${packet.simulation.model_source.replaceAll('_', ' ')}` : null,
    packet.simulation?.fidelity ? `Fidelity: ${packet.simulation.fidelity.replaceAll('_', ' ')}` : null,
    packet.simulation?.convert_to_game ? 'Practice game included' : null,
  ].filter(Boolean).map(item => `<span>${escapeHtml(item)}</span>`).join('');
  stage.innerHTML = `
    <article class="studio-built-project">
      ${avatar}
      <div>
        <p class="studio-project-eyebrow">${copy.eyebrow}</p>
        <h2>${copy.title}</h2>
        <p>${copy.body}</p>
        <div class="studio-project-manifest">${manifest}</div>
        ${label}
        <button id="prototype-action" class="btn btn-primary btn-sm" type="button">${copy.action}</button>
      </div>
    </article>`;
  document.getElementById('prototype-action').addEventListener('click', event => {
    event.currentTarget.textContent = 'Local sandbox passed';
    event.currentTarget.disabled = true;
  });
}

form.addEventListener('submit', async event => {
  event.preventDefault();
  formStatus.textContent = '';
  try {
    validateMedia();
    validateSimulation();
    if (!form.reportValidity()) return;
    latestConsentReceipt = useVoice.checked || useImage.checked ? {
      schema: 'dreamco.creator_media_consent.v1',
      created_at: new Date().toISOString(),
      owner_is_subject: true,
      adult_confirmed: true,
      permitted_uses: ['Buddy owner projects', 'owner-approved export to another platform'],
      prohibited_uses: ['minor cloning', 'another person impersonation', 'unapproved publishing', 'political or deceptive impersonation'],
      synthetic_media_label_required: true,
      revocable: true,
      voice_sha256: useVoice.checked ? await blobFingerprint(voiceBlob) : null,
      image_sha256: useImage.checked ? await blobFingerprint(imageBlob) : null,
      raw_media_embedded: false,
    } : null;
    const type = selectedType();
    const simulationModifications = simulationAdditions.value
      .split(/[,\n]/)
      .map(item => item.trim())
      .filter(Boolean)
      .slice(0, 50);
    const modelRef = document.getElementById('simulation-model-ref').value.trim();
    const rightsRef = document.getElementById('simulation-rights-ref').value.trim();
    const simulationPacket = SIMULATION_TYPES.has(type) ? {
      status: 'simulation_packet_ready',
      model_source: simulationModelSource.value,
      model_ref_sha256: await textFingerprint(modelRef),
      rights_ref_sha256: await textFingerprint(rightsRef),
      raw_references_stored: false,
      fidelity: simulationFidelity.value,
      paint: simulationPaint.value,
      modifications: simulationModifications,
      variant_controls: simulationFoundry?.variant_controls || [],
      render_state: 'renderer_configuration_required',
      convert_to_game: simulationToGame.checked,
      game_conversion: simulationToGame.checked ? {
        status: 'practice_game_plan_ready',
        stages: simulationFoundry?.simulation_to_game?.stages || [],
        required_evidence: simulationFoundry?.simulation_to_game?.required_evidence || [],
      } : null,
      truth_boundary: simulationFoundry?.truth_boundary || 'Measured evidence and qualified review remain required.',
    } : null;
    latestPacket = {
      schema: 'dreamco.buddy_creative_studio_project.v1',
      project_type: type,
      title: document.getElementById('project-title').value.trim(),
      objective: document.getElementById('project-objective').value.trim(),
      subject: document.getElementById('project-subject').value.trim(),
      audience: document.getElementById('project-audience').value.trim(),
      code: { status: 'local_prototype_ready', network_default: 'off' },
      voice: { requested: useVoice.checked, status: useVoice.checked ? 'consent_verified_pending_render' : 'not_requested' },
      likeness: { requested: useImage.checked, status: useImage.checked ? 'consent_verified_pending_render' : 'not_requested' },
      consent: useVoice.checked || useImage.checked ? {
        owner_is_subject: true,
        adult_confirmed: true,
        synthetic_media_label: true,
        raw_media_in_packet: false,
        receipt_schema: latestConsentReceipt.schema,
        voice_sha256: latestConsentReceipt.voice_sha256,
        image_sha256: latestConsentReceipt.image_sha256,
      } : null,
      actor: ACTOR_TYPES.has(type) ? {
        mode: actorMode.value,
        character_description: document.getElementById('actor-description').value.trim(),
        real_person_imitation_allowed: false,
        render_state: 'renderer_configuration_required',
        production_departments: hollywoodGroup?.departments?.map(item => item.id) || [],
        quality_gates: hollywoodGroup?.quality_gates || [],
        hard_blocks: hollywoodGroup?.actor_hard_blocks || [],
      } : null,
      simulation: simulationPacket,
      artifacts: type === 'invention_prototype'
        ? ['requirements', 'system block diagram', 'bill of materials', 'simulation plan', 'bench-test matrix', 'safety review', 'prior-art research plan', 'cost and ROI estimate']
        : SIMULATION_TYPES.has(type)
          ? ['model and rights manifest', 'variant workbench', 'before-and-after comparison', 'simulation state model', 'known-limits report', 'qualified-review gate', 'simulation-to-game plan']
        : ['source plan', 'test plan', 'rights manifest', 'release checklist'],
      tests: type === 'invention_prototype'
        ? ['core assumption', 'failure modes', 'electrical and mechanical safety', 'accessibility', 'repairability', 'no automatic ordering or manufacturing']
        : SIMULATION_TYPES.has(type)
          ? ['model rights and provenance', 'units and scale', 'legal actions', 'safe failure and reset', 'deterministic replay', 'known limits', 'accessibility', 'qualified review', 'bot playtest', 'no live machine control']
        : ['offline load', 'touch and keyboard', 'captions', 'restart and recovery', 'learning objective', 'no live external action'],
      production_academy: type === 'feature_film'
        ? { track: 'film', phases: academy?.film_standard?.phases?.map(item => item.id) || [], departments: hollywoodGroup?.departments?.map(item => item.id) || [], quality_gates: hollywoodGroup?.quality_gates || [] }
        : ['music_video', 'music_artist'].includes(type)
          ? { track: 'music', genre_families: academy?.music_standard?.genre_families?.map(item => item.id) || [], rights_gates: academy?.music_standard?.rights_gates || [] }
          : SIMULATION_TYPES.has(type)
            ? { track: 'simulation', domains: simulationFoundry?.domains?.map(item => item.id) || [], model_sources: simulationFoundry?.model_sources?.map(item => item.id) || [] }
          : null,
      publish_requires_owner_approval: true,
    };
    renderPrototype(latestPacket);
    const rendererNeeded = useVoice.checked || useImage.checked || SIMULATION_TYPES.has(type) || ACTOR_TYPES.has(type);
    readiness.textContent = rendererNeeded ? 'Packet ready · renderer needed' : 'Prototype ready';
    readiness.className = rendererNeeded ? 'badge badge-amber' : 'badge badge-green';
    document.getElementById('result-code').textContent = 'Prototype ready';
    document.getElementById('result-voice').textContent = useVoice.checked ? 'Consent verified' : 'Not requested';
    document.getElementById('result-image').textContent = useImage.checked ? 'Consent verified' : 'Not requested';
    document.getElementById('result-tests').textContent = SIMULATION_TYPES.has(type) ? '10 planned' : '6 planned';
    outputActions.hidden = false;
    document.getElementById('download-consent').disabled = !latestConsentReceipt;
    formStatus.textContent = rendererNeeded
      ? 'Production packet built. A configured local or selected render engine must produce and pass review before this is called a finished visual or media asset.'
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
  const simulationDetail = latestPacket.simulation
    ? ` Use the ${latestPacket.simulation.model_source} model path, apply ${latestPacket.simulation.modifications.join(', ') || 'the approved variants'}, and ${latestPacket.simulation.convert_to_game ? 'turn it into a practice game' : 'keep it as a simulation'}.`
    : '';
  const actorDetail = latestPacket.actor ? ` Actor mode: ${latestPacket.actor.mode}.` : '';
  const prompt = `Continue building ${latestPacket.title} as a ${latestPacket.project_type}. Goal: ${latestPacket.objective}.${actorDetail}${simulationDetail} Keep rights, evidence, quality, safety, and owner approval gates active.`;
  location.href = `buddy.html?prompt=${encodeURIComponent(prompt)}`;
});

document.getElementById('download-consent').addEventListener('click', () => {
  if (!latestConsentReceipt) return;
  downloadBlob(
    new Blob([JSON.stringify(latestConsentReceipt, null, 2)], { type: 'application/json' }),
    'buddy-creator-media-consent.json',
  );
});

document.getElementById('clear-media').addEventListener('click', () => {
  if (mediaStream) mediaStream.getTracks().forEach(track => track.stop());
  stopImageCamera();
  if (recordingTimer) clearTimeout(recordingTimer);
  if (voiceObjectUrl) URL.revokeObjectURL(voiceObjectUrl);
  if (imageObjectUrl) URL.revokeObjectURL(imageObjectUrl);
  mediaStream = null;
  mediaRecorder = null;
  voiceBlob = null;
  imageBlob = null;
  latestConsentReceipt = null;
  voiceObjectUrl = '';
  imageObjectUrl = '';
  voiceFile.value = '';
  imageFile.value = '';
  voicePreview.removeAttribute('src');
  imagePreview.removeAttribute('src');
  imagePreview.hidden = true;
  document.getElementById('download-voice').disabled = true;
  document.getElementById('download-image').disabled = true;
  document.getElementById('download-consent').disabled = true;
  voiceStatus.textContent = 'No sample selected.';
  imageStatus.textContent = 'Choose an image or open the camera.';
  formStatus.textContent = 'Local media removed from this browser session.';
});

academyTrack.addEventListener('change', renderAcademy);
document.getElementById('academy-use').addEventListener('click', () => {
  const select = document.getElementById('project-type');
  select.value = academyTrack.value === 'film'
    ? 'feature_film'
    : academyTrack.value === 'music'
      ? 'music_video'
      : 'skills_training_simulation';
  applyPreset(select.value);
  document.getElementById('project-title').focus();
  formStatus.textContent = academyTrack.value === 'film'
    ? 'The 12-department production group, synthetic-actor modes, and rendered quality gates will be included in this packet.'
    : academyTrack.value === 'music'
      ? 'Music genre study, production stages, rights gates, and music-video departments will be included in this packet.'
      : 'Model provenance, variants, known limits, qualified review, and simulation-to-game stages will be included in this packet.';
});

setTypeFromQuery();
updateMediaControls();
updateProjectControls();
renderSimulationConcept();
renderAcademy();
