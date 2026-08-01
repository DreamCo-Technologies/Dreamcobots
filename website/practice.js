(function () {
  'use strict';

  const catalog = window.BUDDY_PRACTICE_LAB;
  const byId = (id) => document.getElementById(id);
  let latestPlan = null;
  let questions = [];
  let questionIndex = 0;
  let answers = [];
  let recorder = null;
  let stream = null;
  let chunks = [];
  let audioBlob = null;
  let audioUrl = '';
  let recordingTimer = null;

  function escapeHtml(value) {
    return String(value).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;').replaceAll("'", '&#39;');
  }

  function downloadJson(value, filename) {
    const blob = new Blob([JSON.stringify(value, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
  }

  async function fingerprint(blob) {
    if (!blob || !crypto.subtle) return null;
    const digest = await crypto.subtle.digest('SHA-256', await blob.arrayBuffer());
    return [...new Uint8Array(digest)].map(item => item.toString(16).padStart(2, '0')).join('');
  }

  function selectedMode() {
    return catalog.modes.find(mode => mode.id === byId('practice-mode').value) || catalog.modes[0];
  }

  function usesVoice() {
    return ['voice', 'text_and_voice'].includes(byId('practice-answer-mode').value);
  }

  function renderGuide() {
    const mode = selectedMode();
    byId('practice-guide-title').textContent = mode.label;
    byId('practice-opening').textContent = mode.opening;
    byId('practice-specialists').innerHTML = mode.specialists.map(slug => `<a href="bots.html?prospectus=${encodeURIComponent(slug)}"><span>${escapeHtml(slug.replaceAll('-', ' '))}</span><strong>Prospectus</strong></a>`).join('');
    byId('practice-dimensions').innerHTML = catalog.review_dimensions.map(item => `<li>${escapeHtml(item)}</li>`).join('');
  }

  function updateVoiceControls() {
    const enabled = usesVoice();
    byId('practice-voice-rights-row').hidden = !enabled;
    byId('practice-voice-controls').hidden = !enabled;
  }

  function initializeSelectors() {
    byId('practice-mode').innerHTML = catalog.modes.map(mode => `<option value="${escapeHtml(mode.id)}">${escapeHtml(mode.label)}</option>`).join('');
    byId('practice-difficulty').innerHTML = catalog.difficulty_levels.map(level => `<option value="${escapeHtml(level.id)}">${escapeHtml(level.label)}</option>`).join('');
    byId('practice-mode').value = 'job_interview';
    byId('practice-difficulty').value = 'realistic';
    renderGuide();
    updateVoiceControls();
  }

  function renderQuestion() {
    const session = byId('practice-session');
    session.hidden = false;
    if (questionIndex >= questions.length) {
      byId('practice-progress').textContent = `${answers.length} answers saved`;
      byId('practice-session-title').textContent = 'Practice round complete';
      byId('practice-question').textContent = 'Review your evidence, repeat any weak answer, or continue with Buddy for adaptive follow-up questions.';
      byId('practice-save-answer').disabled = true;
      byId('practice-skip').disabled = true;
      return;
    }
    byId('practice-progress').textContent = `Round ${questionIndex + 1} of ${questions.length}`;
    byId('practice-session-title').textContent = selectedMode().label;
    byId('practice-question').textContent = questions[questionIndex];
    byId('practice-answer').value = '';
    byId('practice-save-answer').disabled = false;
    byId('practice-skip').disabled = false;
    resetAudio();
  }

  function renderAnswers() {
    byId('practice-answer-history').innerHTML = answers.map((answer, index) => `
      <article class="practice-answer-row"><span>Round ${index + 1}</span><strong>${escapeHtml(answer.question)}</strong><p>${answer.text ? escapeHtml(answer.text.slice(0, 180)) : 'Voice answer recorded locally'}${answer.voice_sha256 ? ' · voice evidence hashed' : ''}</p></article>
    `).join('');
  }

  function resetAudio() {
    if (stream) stream.getTracks().forEach(track => track.stop());
    if (recordingTimer) clearTimeout(recordingTimer);
    if (audioUrl) URL.revokeObjectURL(audioUrl);
    stream = null;
    recorder = null;
    audioBlob = null;
    audioUrl = '';
    chunks = [];
    byId('practice-audio').removeAttribute('src');
    byId('practice-record').disabled = false;
    byId('practice-stop').disabled = true;
    byId('practice-audio-status').textContent = 'Raw audio stays in this browser session and is not embedded in the practice packet.';
  }

  function buildPlan(event) {
    event.preventDefault();
    const goals = byId('practice-goals').value.split('\n').map(value => value.trim()).filter(Boolean).slice(0, 8);
    if (!goals.length || !byId('practice-form').reportValidity()) return;
    if (usesVoice() && !byId('practice-voice-rights').checked) {
      byId('practice-status').textContent = 'Voice practice requires adult subject rights confirmation.';
      return;
    }
    const mode = selectedMode();
    if (['job_interview', 'career_plan'].includes(mode.id) && !byId('practice-candidate-only').checked) {
      byId('practice-status').textContent = 'Job preparation cannot impersonate a candidate in a real interview or assessment.';
      return;
    }
    const rounds = Math.max(1, Math.min(12, Number(byId('practice-rounds').value || 1)));
    questions = [mode.opening, ...mode.questions].slice(0, rounds);
    latestPlan = {
      schema: 'dreamco.buddy_practice_session_plan.v1',
      created_at: new Date().toISOString(),
      status: 'private_sandbox_ready',
      mode: mode.id,
      target_role: byId('practice-role').value.trim(),
      context: byId('practice-context').value.trim(),
      goals,
      difficulty: byId('practice-difficulty').value,
      rounds,
      answer_mode: byId('practice-answer-mode').value,
      specialist_slugs: mode.specialists,
      questions,
      review_dimensions: catalog.review_dimensions,
      job_prep_outputs: ['job_interview', 'career_plan'].includes(mode.id) ? catalog.job_prep_outputs : [],
      answers: [],
      controls: {
        private_practice_only: true,
        candidate_impersonation_allowed: false,
        automated_employment_decision_allowed: false,
        protected_trait_inference_allowed: false,
        fabricated_credentials_allowed: false,
        raw_voice_stored_in_packet: false,
        exact_approval_before_external_action: true,
        live_external_action_taken: false,
      },
      hard_boundaries: catalog.hard_boundaries,
    };
    questionIndex = 0;
    answers = [];
    renderAnswers();
    renderQuestion();
    byId('practice-status').textContent = `${mode.label} session ready with ${mode.specialists.length} verified specialist routes.`;
    byId('practice-session').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  async function saveAnswer(skip = false) {
    if (!latestPlan || questionIndex >= questions.length) return;
    const text = byId('practice-answer').value.trim();
    if (!skip && byId('practice-answer-mode').value !== 'voice' && !text) {
      byId('practice-audio-status').textContent = 'Write an answer or choose Skip question.';
      return;
    }
    if (!skip && usesVoice() && byId('practice-answer-mode').value === 'voice' && !audioBlob) {
      byId('practice-audio-status').textContent = 'Record an answer or choose Skip question.';
      return;
    }
    const answer = {
      question: questions[questionIndex],
      text: skip ? '' : text,
      skipped: skip,
      voice_sha256: skip ? null : await fingerprint(audioBlob),
      raw_voice_embedded: false,
      self_review_dimensions: catalog.review_dimensions,
    };
    answers.push(answer);
    latestPlan.answers = answers;
    renderAnswers();
    questionIndex += 1;
    renderQuestion();
  }

  byId('practice-form').addEventListener('submit', buildPlan);
  byId('practice-mode').addEventListener('change', renderGuide);
  byId('practice-answer-mode').addEventListener('change', updateVoiceControls);
  byId('practice-save-answer').addEventListener('click', () => saveAnswer(false));
  byId('practice-skip').addEventListener('click', () => saveAnswer(true));
  byId('practice-record').addEventListener('click', async () => {
    if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) {
      byId('practice-audio-status').textContent = 'Voice recording is unavailable in this browser.';
      return;
    }
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      chunks = [];
      recorder = new MediaRecorder(stream);
      recorder.addEventListener('dataavailable', event => { if (event.data.size) chunks.push(event.data); });
      recorder.addEventListener('stop', () => {
        if (recordingTimer) clearTimeout(recordingTimer);
        if (stream) stream.getTracks().forEach(track => track.stop());
        stream = null;
        audioBlob = new Blob(chunks, { type: recorder.mimeType || 'audio/webm' });
        if (audioUrl) URL.revokeObjectURL(audioUrl);
        audioUrl = URL.createObjectURL(audioBlob);
        byId('practice-audio').src = audioUrl;
        byId('practice-record').disabled = false;
        byId('practice-stop').disabled = true;
        byId('practice-audio-status').textContent = 'Voice answer ready locally. Only its SHA-256 evidence enters the packet.';
      });
      recorder.start();
      recordingTimer = setTimeout(() => { if (recorder?.state !== 'inactive') recorder.stop(); }, 120000);
      byId('practice-record').disabled = true;
      byId('practice-stop').disabled = false;
      byId('practice-audio-status').textContent = 'Recording locally...';
    } catch (error) {
      byId('practice-audio-status').textContent = `Microphone unavailable: ${error.message}`;
    }
  });
  byId('practice-stop').addEventListener('click', () => { if (recorder?.state !== 'inactive') recorder.stop(); });
  byId('practice-download').addEventListener('click', () => {
    if (latestPlan) downloadJson(latestPlan, 'buddy-practice-session.json');
  });
  byId('practice-send-buddy').addEventListener('click', () => {
    if (!latestPlan) return;
    const prompt = `Run a private ${latestPlan.mode.replaceAll('_', ' ')} role-play for ${latestPlan.target_role}. Context: ${latestPlan.context}. Goals: ${latestPlan.goals.join('; ')}. Difficulty: ${latestPlan.difficulty}. Route through ${latestPlan.specialist_slugs.join(', ')}. Do not impersonate me in a real interview, invent credentials, infer protected traits, or take any external action.`;
    location.href = `buddy.html?prompt=${encodeURIComponent(prompt)}`;
  });

  initializeSelectors();
})();
