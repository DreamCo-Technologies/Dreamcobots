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
    const rows = academy.film_standard.phases;
    rows.forEach((row, index) => academyGrid.append(academyCard(index, row.label, row.outputs, 'Phase')));
    academySummary.textContent = `${rows.length} production phases · ${academy.film_standard.quality_gates.length} release gates · delivery specs verified for each target platform`;
  } else {
    const rows = academy.music_standard.genre_families;
    rows.forEach((row, index) => academyGrid.append(academyCard(index, row.label, row.study, 'Family')));
    academySummary.textContent = `${rows.length} genre families · original composition workflow · composition, recording, sample, performance, sync, voice, and likeness rights gates`;
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
  if (type === 'invention_prototype') return {
    eyebrow: 'Invention workbench',
    title: `Prototype: ${subject}`,
    body: `Requirements, system architecture, component options, bill of materials, prior-art research, safety review, simulation, and a bench-test matrix prepared for ${audience}.`,
    action: 'Review test plan',
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

form.addEventListener('submit', async event => {
  event.preventDefault();
  formStatus.textContent = '';
  try {
    validateMedia();
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
        receipt_schema: latestConsentReceipt.schema,
        voice_sha256: latestConsentReceipt.voice_sha256,
        image_sha256: latestConsentReceipt.image_sha256,
      } : null,
      artifacts: selectedType() === 'invention_prototype'
        ? ['requirements', 'system block diagram', 'bill of materials', 'simulation plan', 'bench-test matrix', 'safety review', 'prior-art research plan', 'cost and ROI estimate']
        : ['source plan', 'test plan', 'rights manifest', 'release checklist'],
      tests: selectedType() === 'invention_prototype'
        ? ['core assumption', 'failure modes', 'electrical and mechanical safety', 'accessibility', 'repairability', 'no automatic ordering or manufacturing']
        : ['offline load', 'touch and keyboard', 'captions', 'restart and recovery', 'learning objective', 'no live external action'],
      production_academy: selectedType() === 'feature_film'
        ? { track: 'film', phases: academy?.film_standard?.phases?.map(item => item.id) || [], quality_gates: academy?.film_standard?.quality_gates || [] }
        : ['music_video', 'music_artist'].includes(selectedType())
          ? { track: 'music', genre_families: academy?.music_standard?.genre_families?.map(item => item.id) || [], rights_gates: academy?.music_standard?.rights_gates || [] }
          : null,
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
    document.getElementById('download-consent').disabled = !latestConsentReceipt;
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
  select.value = academyTrack.value === 'film' ? 'feature_film' : 'music_video';
  applyPreset(select.value);
  document.getElementById('project-title').focus();
  formStatus.textContent = academyTrack.value === 'film'
    ? 'Film production phases and quality gates will be included in this project packet.'
    : 'Music genre study, production stages, and rights gates will be included in this project packet.';
});

setTypeFromQuery();
updateMediaControls();
renderAcademy();
