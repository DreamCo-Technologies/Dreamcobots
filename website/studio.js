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
};

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
  renderEmptyState(type);
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

useVoice.addEventListener('change', updateMediaControls);
useImage.addEventListener('change', updateMediaControls);
document.getElementById('project-type').addEventListener('change', event => applyPreset(event.target.value));

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
  const avatar = useImage.checked ? `<img class="studio-avatar-preview" src="${imageObjectUrl}" alt="Approved creator likeness preview" />` : '<div class="studio-generated-avatar">B</div>';
  const label = useVoice.checked || useImage.checked ? '<p class="studio-media-label">AI-assisted media using the adult creator\'s approved voice or likeness</p>' : '';
  stage.innerHTML = `
    <article class="studio-built-project">
      ${avatar}
      <div>
        <p class="studio-project-eyebrow">${copy.eyebrow}</p>
        <h2>${copy.title}</h2>
        <p>${copy.body}</p>
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
    readiness.textContent = useVoice.checked || useImage.checked ? 'Prototype ready · media renderer needed' : 'Prototype ready';
    readiness.className = useVoice.checked || useImage.checked ? 'badge badge-amber' : 'badge badge-green';
    document.getElementById('result-code').textContent = 'Prototype ready';
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
