(() => {
  'use strict';

  const makers = [
    ['podcast','Podcast episode','Write the episode outline, host script, guest questions, intro/outro, ad slots, chapter markers, show notes, title options, cover-art brief, audiogram clips, transcript, captions, and publishing package.'],
    ['podcast','Podcast clip','Turn a podcast moment into short vertical clips with hook, captions, title, thumbnail text, and platform variants.'],
    ['podcast','Podcast trailer','Build a show trailer with positioning, host intro, music/sound brief, CTA, cover art, description, and launch checklist.'],
    ['streamer','Live stream','Build a run of show, scenes, overlays, alerts, talking points, moderation plan, sponsor moments, clips plan, and post-stream recap.'],
    ['streamer','Stream highlight','Create a polished highlight from a stream with hook, cuts, captions, title, thumbnail, description, and short-form variants.'],
    ['streamer','Gaming stream','Prepare game-specific stream title, tags, scenes, challenge format, chat prompts, clip markers, and safety/moderation setup.'],
    ['creator','Long video','Build a complete long-form video: research plan, script, shot list, B-roll list, voiceover, edit plan, thumbnail, title, description, chapters, captions, and clips.'],
    ['creator','Short video','Create a 9:16 short with hook, script, shot list, captions, sound/music brief, CTA, thumbnail frame, and platform variants.'],
    ['creator','Image post','Create the image brief, composition, caption, CTA, accessibility alt text, tags, and platform-ready sizes.'],
    ['creator','Carousel','Create a multi-slide educational or promotional carousel with hook, slide copy, visual direction, CTA, caption, and alt text.'],
    ['creator','Story','Create a story sequence with frames, polls/questions, stickers/CTA plan, captions, and visual directions.'],
    ['creator','Blog/newsletter','Create a long-form article or newsletter with outline, draft, images, SEO metadata, excerpts, social promo, and email subject options.'],
    ['creator','Thumbnail','Create thumbnail concepts, text variants, visual hierarchy, subject framing, and A/B testing ideas.'],
    ['creator','Channel brand kit','Create channel name ideas, positioning, bio, banner brief, profile image brief, content pillars, intro/outro, posting cadence, and visual language.'],
    ['creator','Sponsor package','Create media kit, rate-card draft, sponsor pitch, integration formats, disclosure checklist, deliverables, and campaign reporting template.']
  ];

  const platforms = [
    {name:'YouTube', modes:['podcast','streamer','creator'], kind:'Video / Live / Shorts', make:'Create a YouTube-ready video, Short, live show, or video podcast', post:'Prepare this project for YouTube upload or scheduling'},
    {name:'YouTube Music', modes:['podcast','creator'], kind:'Podcast / Music', make:'Create a YouTube Music-ready podcast or music release package', post:'Prepare this project for YouTube Music distribution where supported'},
    {name:'Spotify', modes:['podcast','creator'], kind:'Podcast / Video Podcast', make:'Create a Spotify-ready podcast or video podcast episode', post:'Prepare this episode for Spotify publishing through an approved host or connector'},
    {name:'Apple Podcasts', modes:['podcast'], kind:'Podcast', make:'Create an Apple Podcasts-ready episode and metadata package', post:'Prepare this episode for Apple Podcasts through the connected podcast host/feed'},
    {name:'Amazon Music / Audible', modes:['podcast','creator'], kind:'Podcast / Audio', make:'Create an Amazon Music or Audible-ready audio package', post:'Prepare this audio project for an approved Amazon publishing path'},
    {name:'TikTok', modes:['streamer','creator'], kind:'Short Video / Live', make:'Create a TikTok-ready short or live-stream package', post:'Prepare this project for TikTok posting or scheduling'},
    {name:'Instagram', modes:['podcast','streamer','creator'], kind:'Reels / Feed / Stories / Live', make:'Create Instagram Reel, feed, Story, or Live variants from this project', post:'Prepare approved Instagram variants for posting or scheduling'},
    {name:'Facebook', modes:['podcast','streamer','creator'], kind:'Video / Reels / Posts / Live', make:'Create Facebook video, Reel, post, or Live variants', post:'Prepare approved Facebook variants for posting or scheduling'},
    {name:'Threads', modes:['podcast','creator'], kind:'Text / Images / Clips', make:'Turn this project into Threads posts and conversation prompts', post:'Prepare the Threads post set for publishing'},
    {name:'X', modes:['podcast','streamer','creator'], kind:'Posts / Video / Spaces', make:'Create posts, clips, threads, or a Spaces promotion package', post:'Prepare approved X content for publishing'},
    {name:'Twitch', modes:['streamer'], kind:'Live Streaming', make:'Build a Twitch stream package with scenes, overlays, titles, tags, moderation, and clips', post:'Prepare this stream for Twitch launch through the connected account'},
    {name:'Kick', modes:['streamer'], kind:'Live Streaming', make:'Build a Kick-ready stream package with scenes, title, category, moderation, and clip plan', post:'Prepare this stream for Kick launch through the connected account'},
    {name:'Discord', modes:['podcast','streamer','creator'], kind:'Community / Events / Clips', make:'Create a Discord community post, event, stage, clip, or announcement package', post:'Prepare approved Discord publishing through the connected server'},
    {name:'Reddit', modes:['podcast','streamer','creator'], kind:'Posts / Communities', make:'Create subreddit-aware post variants with title, body, media, disclosure, and community-fit notes', post:'Prepare this content for the selected Reddit community after rules review'},
    {name:'LinkedIn', modes:['podcast','creator'], kind:'Professional Posts / Video / Articles', make:'Create professional LinkedIn post, article, clip, carousel, or newsletter variants', post:'Prepare approved LinkedIn content for publishing'},
    {name:'Pinterest', modes:['creator'], kind:'Pins / Video Pins', make:'Create Pinterest-ready pins, boards, titles, descriptions, and visual sizes', post:'Prepare approved pins for publishing'},
    {name:'Snapchat', modes:['streamer','creator'], kind:'Stories / Spotlight', make:'Create Snapchat Story or Spotlight variants', post:'Prepare approved Snapchat content for publishing where connector support exists'},
    {name:'Patreon', modes:['podcast','streamer','creator'], kind:'Membership Content', make:'Create member posts, bonus episodes, behind-the-scenes content, tiers, and release notes', post:'Prepare approved member content for Patreon publishing'},
    {name:'Substack', modes:['podcast','creator'], kind:'Newsletter / Podcast', make:'Create Substack newsletter or podcast content with title, body, audio notes, and email preview', post:'Prepare approved Substack content for publishing'},
    {name:'Medium', modes:['creator'], kind:'Articles', make:'Turn this project into a Medium-ready article with headline, deck, body, images, and tags', post:'Prepare the article for Medium publishing'},
    {name:'Tumblr', modes:['creator'], kind:'Posts / Images / GIFs', make:'Create Tumblr-ready visual and text post variants', post:'Prepare approved Tumblr content for publishing'},
    {name:'Rumble', modes:['podcast','streamer','creator'], kind:'Video / Live', make:'Create a Rumble-ready video or live-stream package', post:'Prepare this project for Rumble upload or scheduling'},
    {name:'Dailymotion', modes:['creator'], kind:'Video', make:'Create a Dailymotion-ready video package', post:'Prepare this video for Dailymotion upload'},
    {name:'SoundCloud', modes:['podcast','creator'], kind:'Audio', make:'Create a SoundCloud-ready audio release with artwork and metadata', post:'Prepare the audio project for SoundCloud publishing'},
    {name:'RSS Podcast Feed', modes:['podcast'], kind:'Open Podcast Distribution', make:'Create a standards-ready podcast episode package for an RSS host', post:'Prepare enclosure, metadata, show notes, chapters, transcript, and feed-ready release data'}
  ];

  const makerGrid = document.getElementById('maker-grid');
  const platformGrid = document.getElementById('platform-grid');
  const status = document.getElementById('creator-status');
  let activeMode = 'all';

  function buddyUrl(prompt) {
    return `buddy.html?prompt=${encodeURIComponent(prompt)}`;
  }

  function renderMakers() {
    makerGrid.innerHTML = makers.filter(([mode]) => activeMode === 'all' || mode === activeMode).map(([mode,title,prompt]) => `
      <article class="maker-card" data-mode="${mode}">
        <small>${mode}</small><h3>${title}</h3><p>${prompt}</p>
        <button class="make" type="button" data-make="${encodeURIComponent(prompt)}">Make ${title}</button>
      </article>`).join('');
  }

  function renderPlatforms() {
    platformGrid.innerHTML = platforms.filter((platform) => activeMode === 'all' || platform.modes.includes(activeMode)).map((platform) => `
      <article class="platform-card">
        <small>${platform.kind}</small><h3>${platform.name}</h3><p>${platform.modes.join(' · ')}</p>
        <div class="platform-actions">
          <a class="make" href="${buddyUrl(`${platform.make}. Reuse my existing Creator Studio project if one exists, otherwise start a new editable project. Do not publish yet.`)}">Make</a>
          <a class="post" href="${buddyUrl(`${platform.post}. First verify the correct authenticated connector, account permissions, platform requirements, rights, disclosures, format, title, description, captions, thumbnail/artwork, tags, audience settings, monetization settings, and scheduled time. Show me a final preview and stop before the external write unless my publishing approval covers this exact action.`)}">Post / Prepare</a>
        </div>
      </article>`).join('');
  }

  document.querySelectorAll('[data-mode]').forEach((button) => button.addEventListener('click', () => {
    activeMode = button.dataset.mode;
    document.querySelectorAll('[data-mode]').forEach((item) => item.classList.toggle('active', item === button));
    renderMakers(); renderPlatforms();
    status.textContent = `${button.textContent} tools ready.`;
  }));

  makerGrid.addEventListener('click', (event) => {
    const button = event.target.closest('[data-make]');
    if (!button) return;
    const task = decodeURIComponent(button.dataset.make);
    location.href = buddyUrl(`${task} Keep everything editable, generate platform variants from one master project, and bring me back to the Creator Platform Hub when the package is ready.`);
  });

  renderMakers();
  renderPlatforms();
})();
