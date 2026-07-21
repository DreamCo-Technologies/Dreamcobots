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
