(() => {
  'use strict';

  const families = {
    'Hip-Hop & Rap': ['Hip-hop','Boom bap','Trap','Drill','Lo-fi hip-hop','Alternative hip-hop','Jazz rap','Southern rap','West Coast rap','East Coast rap','Conscious rap','Cloud rap','Phonk','Grime','UK rap','Latin trap'],
    'R&B, Soul & Funk': ['R&B','Contemporary R&B','Neo-soul','Soul','Motown-inspired soul','Funk','P-funk-inspired','Quiet storm','New jack swing','Alternative R&B','Gospel soul','Disco-funk'],
    'Pop': ['Pop','Dance-pop','Electropop','Synth-pop','Indie pop','Dream pop','Bedroom pop','Art pop','Teen pop','Power pop','Hyperpop','K-pop-inspired pop','J-pop-inspired pop','Latin pop','Afropop','Pop rock'],
    'Rock & Metal': ['Rock','Classic rock','Alternative rock','Indie rock','Garage rock','Punk rock','Post-punk','Hard rock','Progressive rock','Psychedelic rock','Shoegaze','Emo','Pop punk','Metal','Heavy metal','Thrash metal','Death metal','Black metal','Doom metal','Metalcore','Nu metal','Progressive metal'],
    'Electronic & Dance': ['House','Deep house','Tech house','Progressive house','Future house','Acid house','Techno','Minimal techno','Detroit techno','Trance','Progressive trance','Psytrance','Drum and bass','Jungle','Dubstep','Future bass','UK garage','2-step','Breakbeat','Electro','EDM','Ambient electronic','Downtempo','Trip-hop','Chillwave','Synthwave','Vaporwave','Hardstyle'],
    'Jazz & Blues': ['Jazz','Bebop','Hard bop','Cool jazz','Free jazz','Fusion','Smooth jazz','Swing','Big band','Dixieland','Blues','Delta blues','Chicago blues','Electric blues','Soul blues','Jazz-funk','Latin jazz','Afro-Cuban jazz'],
    'Country, Folk & Americana': ['Country','Traditional country','Outlaw country','Country pop','Country rock','Bluegrass','Americana','Folk','Contemporary folk','Indie folk','Folk rock','Appalachian','Western swing','Honky-tonk','Singer-songwriter'],
    'Latin & Caribbean': ['Reggaeton','Salsa','Bachata','Merengue','Cumbia','Mambo','Cha-cha-cha','Bolero','Son cubano','Latin jazz','Samba','Bossa nova','Forró','Funk carioca','Dembow','Dancehall','Reggae','Dub','Soca','Calypso','Zouk','Kompa'],
    'African & Diaspora': ['Afrobeats','Afrobeat','Amapiano','Highlife','Hiplife','Juju','Fuji','Makossa','Soukous','Kwaito','Gqom','Mbalax','Afro-house','Afro-soul','Afro-jazz','Palm-wine'],
    'Middle Eastern & North African': ['Arabic pop','Raï','Chaabi','Gnawa','Maqam-inspired','Khaleeji','Dabke','Persian pop','Turkish pop','Anatolian rock','Mizrahi','North African fusion'],
    'South Asian': ['Bollywood-inspired','Hindustani classical-inspired','Carnatic-inspired','Bhangra','Punjabi pop','Desi hip-hop','Ghazal-inspired','Qawwali-inspired','Indian electronic','Tamil film-inspired','South Asian folk fusion'],
    'East & Southeast Asian': ['J-pop-inspired','K-pop-inspired','City pop','Enka-inspired','Cantopop-inspired','Mandopop-inspired','Chinese traditional fusion','Gamelan-inspired','Thai pop-inspired','Vietnamese pop-inspired','T-pop-inspired','Pinoy pop-inspired'],
    'Classical & Cinematic': ['Classical','Baroque-inspired','Romantic-era-inspired','Modern classical','Minimalism','Orchestral','Chamber music','Piano solo','String quartet','Opera-inspired','Cinematic score','Trailer music','Epic orchestral','Suspense score','Horror score','Fantasy score','Sci-fi score','Documentary score','Game soundtrack'],
    'Ambient, Experimental & Wellness': ['Ambient','Drone','Soundscape','New age','Meditation','Sleep music','Nature fusion','Experimental','Avant-garde','Musique concrète-inspired','Glitch','Noise','Electroacoustic','Generative music'],
    'Religious & Spiritual Traditions': ['Gospel','Contemporary Christian','Worship','Spirituals-inspired','Sacred choral','Nasheed-inspired','Devotional fusion','Meditative spiritual'],
    'Children, Education & Utility': ['Children’s music','Nursery style','Educational song','Learning rap','Sing-along','Theme song','Jingle','Podcast intro','Streamer intro','Notification sound','Brand sonic logo','Workout music','Focus music','Study music','Sports anthem'],
    'Hybrid & Custom': ['Genre fusion','Acoustic remix','Orchestral remix','Electronic remix','Live-band version','Unplugged version','Cinematic version','Club version','Radio edit','Extended mix','Instrumental','A cappella','Custom hybrid']
  };

  const builds = [
    ['Original song','Create an original complete song with concept, structure, chords/harmony, rhythm, melody direction, lyrics if requested, instrumentation, arrangement, vocal direction, production notes, mix/master plan, artwork brief, metadata, and platform variants.'],
    ['Beat','Create an original beat with BPM, groove, drum pattern direction, bass design, harmonic loop, arrangement, sound palette, transitions, drops, and mix notes.'],
    ['Instrumental','Create an original instrumental composition with structure, melody, harmony, rhythm, instrumentation, dynamics, and mix notes.'],
    ['Film / game score','Create an original cinematic or game score package with themes, motifs, scene cues, instrumentation, tempo map, emotional arc, stems plan, and implementation notes.'],
    ['Theme song','Create an original theme song for a show, game, podcast, streamer, business, or character with hooks and short/long variants.'],
    ['Jingle / sonic brand','Create an original short brand jingle or sonic logo with multiple duration variants and usage notes.'],
    ['Podcast music pack','Create original intro, outro, bumper, transition, ad-bed, and background music directions for a podcast.'],
    ['Streamer music pack','Create original stream intro, countdown, intermission, alert, victory, background, and outro music directions.'],
    ['Remix my owned track','Create a transformation plan for a track the user owns or is licensed to remix, preserving rights metadata and generating style variants.'],
    ['Album / EP','Build an original album or EP plan with concept, track list, sonic palette, narrative arc, production schedule, singles, artwork, metadata, and release rollout.'],
    ['Music video package','Build the song-to-video package: treatment, performance direction, scenes, shot list, choreography concepts, edit rhythm, visual effects, thumbnail, clips, and rollout.'],
    ['Live performance arrangement','Create a live arrangement with band roles, backing tracks, cues, transitions, rehearsal notes, set-list placement, and stage direction.']
  ];

  const styleInput = document.getElementById('music-style');
  const familyTabs = document.getElementById('family-tabs');
  const styleCloud = document.getElementById('style-cloud');
  const buildGrid = document.getElementById('music-build-grid');
  const status = document.getElementById('music-status');
  let selectedFamily = Object.keys(families)[0];

  const buddyUrl = (prompt) => `buddy.html?prompt=${encodeURIComponent(prompt)}`;

  function renderBuilds() {
    buildGrid.innerHTML = builds.map(([title, prompt]) => `<article class="music-card"><h3>${title}</h3><p>${prompt}</p><button class="build-button" type="button" data-build="${encodeURIComponent(prompt)}">Make ${title}</button></article>`).join('');
  }

  function renderFamilies() {
    familyTabs.innerHTML = Object.keys(families).map((family) => `<button type="button" class="${family === selectedFamily ? 'active' : ''}" data-family="${family}">${family}</button>`).join('');
    renderStyles();
  }

  function renderStyles() {
    styleCloud.innerHTML = families[selectedFamily].map((style) => `<button class="style-button" type="button" data-style="${style}">${style}</button>`).join('');
  }

  familyTabs.addEventListener('click', (event) => {
    const button = event.target.closest('[data-family]');
    if (!button) return;
    selectedFamily = button.dataset.family;
    renderFamilies();
  });

  styleCloud.addEventListener('click', (event) => {
    const button = event.target.closest('[data-style]');
    if (!button) return;
    styleInput.value = button.dataset.style;
    styleCloud.querySelectorAll('.style-button').forEach((item) => item.classList.toggle('active', item === button));
    status.textContent = `${button.dataset.style} selected. You can combine it with another style in the Primary style field.`;
  });

  buildGrid.addEventListener('click', (event) => {
    const button = event.target.closest('[data-build]');
    if (!button) return;
    location.href = buddyUrl(`${decodeURIComponent(button.dataset.build)} Let me choose or combine styles from Music Creator. Keep all material original and editable. Do not imitate an unlicensed real artist or copy a protected song.`);
  });

  function projectPrompt(mode) {
    const title = document.getElementById('music-title').value.trim();
    const style = styleInput.value.trim();
    const bpm = document.getElementById('music-bpm').value;
    const key = document.getElementById('music-key').value.trim();
    const length = document.getElementById('music-length').value.trim();
    const use = document.getElementById('music-use').value.trim();
    const mood = document.getElementById('music-mood').value.trim();
    const sound = document.getElementById('music-sound').value.trim();
    const vocals = document.getElementById('music-vocals').value.trim();
    return `${mode} for "${title}". Style: ${style}. BPM: ${bpm}. Key/mode: ${key}. Length: ${length}. Use: ${use}. Mood/story: ${mood}. Instrumentation/sound: ${sound}. Vocal/lyrics direction: ${vocals}. Create original material, keep it editable, include arrangement and production details, and prepare platform-ready metadata and artwork direction. Do not clone a protected song or unlicensed real artist identity/voice.`;
  }

  document.getElementById('music-form').addEventListener('submit', (event) => {
    event.preventDefault();
    location.href = buddyUrl(projectPrompt('Build a complete original track'));
  });
  document.getElementById('instrumental-only').addEventListener('click', () => {
    location.href = buddyUrl(projectPrompt('Build an instrumental-only original track'));
  });
  document.getElementById('release-pack').addEventListener('click', () => {
    location.href = buddyUrl(`${projectPrompt('Build the release package')} Add cover-art brief, credits, rights/provenance checklist, ISRC/UPC placeholders, clean/explicit version planning if relevant, lyric sheet, captions/visualizer plan, short clips, platform metadata, distribution checklist, and launch calendar. Stop before publishing or spending.`);
  });

  renderBuilds();
  renderFamilies();
})();
