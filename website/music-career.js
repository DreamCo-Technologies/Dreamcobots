(() => {
  'use strict';
  const buddyUrl = (prompt) => `buddy.html?prompt=${encodeURIComponent(prompt)}`;
  let recorder = null;
  let chunks = [];
  let recordedBlob = null;
  const state = document.getElementById('record-state');
  const preview = document.getElementById('record-preview');

  async function startRecording() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      recorder = new MediaRecorder(stream);
      chunks = [];
      recorder.ondataavailable = (event) => { if (event.data.size) chunks.push(event.data); };
      recorder.onstop = () => {
        recordedBlob = new Blob(chunks, { type: recorder.mimeType || 'audio/webm' });
        preview.src = URL.createObjectURL(recordedBlob);
        preview.hidden = false;
        stream.getTracks().forEach((track) => track.stop());
        state.textContent = 'Recording captured locally. Use the demo/beat tools to prepare the next step.';
      };
      recorder.start();
      state.textContent = 'Recording…';
      document.getElementById('record-start').disabled = true;
      document.getElementById('record-stop').disabled = false;
    } catch (error) {
      state.textContent = 'Microphone permission was not granted or recording is unavailable in this browser.';
    }
  }

  function stopRecording() {
    if (recorder && recorder.state !== 'inactive') recorder.stop();
    document.getElementById('record-start').disabled = false;
    document.getElementById('record-stop').disabled = true;
  }

  function demoContext() {
    const file = document.getElementById('audio-upload').files[0];
    if (file) return `I selected an authorized demo named ${file.name}.`;
    if (recordedBlob) return 'I recorded an authorized demo in Music Career Studio.';
    return 'I have a vocal or song idea but have not attached the recording to Buddy yet.';
  }

  function go(prompt) { location.href = buddyUrl(prompt); }
  document.getElementById('record-start').addEventListener('click', startRecording);
  document.getElementById('record-stop').addEventListener('click', stopRecording);
  document.getElementById('match-beat').addEventListener('click', () => go(`${demoContext()} Prepare an audio-analysis and production plan to estimate tempo, cadence, phrase length, energy, key candidates, rhythmic pocket, hook moments, breath spaces, and performance needs, then propose at least five original beat directions. If the audio-analysis adapter is not connected, tell me the shortest step needed to pass the audio securely. Do not imitate an existing song.`));
  document.getElementById('build-track').addEventListener('click', () => go(`${demoContext()} Build an original track around my performance. Preserve my cadence and creative intent, propose beat, harmony, arrangement, drops, transitions, doubles, harmonies, ad-libs, punch-ins, mix notes, and alternate versions. Keep my source media private and require rights/consent before external use.`));
  document.getElementById('artist-build').addEventListener('click', () => {
    const mode = document.getElementById('artist-mode').value;
    const file = document.getElementById('artist-media').files[0];
    go(`Build my music artist identity in mode ${mode}. ${file ? `I selected authorized media named ${file.name}.` : 'No media is attached yet.'} Create an original visual system, artist bio, wardrobe/cover direction, logo/wordmark ideas, color system, thumbnail language, video look, social profile kit, and release branding. Do not imitate another real person.`);
  });
  document.getElementById('lyrics-build').addEventListener('click', () => {
    const mode = document.getElementById('lyric-mode').value;
    const style = document.getElementById('lyric-style').value;
    const text = document.getElementById('lyric-text').value;
    go(`Use Music Career lyrics mode ${mode}. Lyric style: ${style}. User material/idea: ${text || 'Start from a fresh original concept.'} Understand and apply rhyme, internal rhyme, multisyllabic rhyme, cadence, flow changes, imagery, wordplay, storytelling, hooks, bridges, melody-friendly phrasing, and genre-appropriate structure. Preserve user-written lines unless I asked for rewriting. Keep the result original.`);
  });
  document.getElementById('flow-build').addEventListener('click', () => {
    const style = document.getElementById('lyric-style').value;
    const text = document.getElementById('lyric-text').value;
    go(`Map flow and cadence for this original/user-owned writing. Style: ${style}. Text/idea: ${text || 'No text yet.'} Show bar/phrase structure, stressed syllables, rhyme pockets, breath points, tempo ranges, beat-pocket options, flow switches, hook opportunities, and delivery practice.`);
  });
  document.getElementById('random-project').addEventListener('click', () => go('Surprise me with an original music project. Randomly choose a coherent genre fusion, mood, tempo range, artist concept, lyrical theme, sonic palette, track concept, visual style, and release strategy. Give me several reroll controls so I can keep any parts I like.'));
  document.getElementById('album-build').addEventListener('click', () => go('Build a complete original album or CD-length project from concept to release: identity, project theme, track count, track concepts, sequencing, recurring motifs, interludes/transitions, singles, beat and lyric directions, recording plan, mixes/masters, clean/explicit/instrumental versions where relevant, artwork, credits, metadata, videos, short-form content, press kit, rollout calendar, and platform-ready packages.'));
  document.getElementById('video-build').addEventListener('click', () => go('Build a music video for my original/user-owned track. Offer performance, narrative, animated, lyric-video, visualizer, live-session, cinematic, and vertical-video routes. Include treatment, lookbook, storyboard, shots, performance direction, locations, wardrobe, lighting, edit rhythm, VFX, color, captions, thumbnail, clips, and publishing variants.'));
  document.getElementById('benchmark').addEventListener('click', () => go('Benchmark my original track against current radio/chart market trends. Use fresh licensed/public trend data when connected and compare measurable characteristics such as tempo distribution, song duration, intro length, time-to-hook, section count, hook recurrence, energy curve, vocal/instrumental balance, loudness range, genre mix, feature frequency, release cadence, and short-form readiness. Do not quote or copy lyrics/melodies/recordings. Return market-fit, originality, strengths, weaknesses, and experiments.'));
  document.getElementById('differentiate').addEventListener('click', () => go('Use current radio/chart trend benchmarks to find ways my original music can stand out rather than copy the market. Give me differentiation ideas in sound, arrangement, lyric angle, visuals, release format, performance, content strategy, and audience positioning.'));
})();
