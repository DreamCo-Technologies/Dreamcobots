let deferredInstallPrompt = null;
let catalog = null;
let latestPlan = null;

const installButton = document.getElementById('install-button');
const installState = document.getElementById('install-state');
const installGuidance = document.getElementById('install-guidance');
const deviceLabel = document.getElementById('device-label');
const familyFilter = document.getElementById('family-filter');
const targetResults = document.getElementById('target-results');
const serviceResults = document.getElementById('service-results');

function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

function detectDevice() {
  const ua = navigator.userAgent.toLowerCase();
  const standalone = matchMedia('(display-mode: standalone)').matches || navigator.standalone === true;
  if (standalone) return { label: 'Installed app', kind: 'installed', guidance: 'Buddy is already running as an installed app on this device.' };
  if (/iphone|ipad|ipod/.test(ua)) return { label: 'Apple mobile device', kind: 'ios', guidance: 'In Safari, open Share, choose Add to Home Screen, then confirm Add.' };
  if (/android/.test(ua)) return { label: 'Android device', kind: 'android', guidance: 'Use Install Buddy when the browser prompt is ready, or open the browser menu and choose Install app.' };
  if (/smart-tv|smarttv|appletv|googletv|hbbtv|roku|tizen|webos/.test(ua)) return { label: 'TV or living-room device', kind: 'tv', guidance: 'Use Buddy in this browser now. A native TV-store version requires the target-specific package and store review shown below.' };
  if (/windows/.test(ua)) return { label: 'Windows device', kind: 'desktop', guidance: 'Use Install Buddy when supported by this browser. A signed Windows package can be prepared through the release planner.' };
  if (/macintosh|mac os/.test(ua)) return { label: 'Mac device', kind: 'desktop', guidance: 'Use Install Buddy in a supported browser, or plan a signed and notarized macOS release below.' };
  if (/linux|cros/.test(ua)) return { label: 'Linux or ChromeOS device', kind: 'desktop', guidance: 'Use Install Buddy in a supported browser, or prepare a Linux or ChromeOS package through the planner.' };
  return { label: 'Browser-connected device', kind: 'browser', guidance: 'Buddy works from this HTTPS page. Native installation depends on the device browser or its official store.' };
}

const device = detectDevice();
deviceLabel.textContent = device.label;
if (device.kind === 'installed') {
  installButton.textContent = 'Buddy installed';
  installButton.disabled = true;
  installState.textContent = 'Installed and ready on this device.';
} else if (device.kind === 'ios') {
  installState.textContent = 'Home Screen installation is available through Safari.';
} else {
  installState.textContent = 'Buddy works now in this browser. Install support depends on this device and browser.';
}

window.addEventListener('beforeinstallprompt', (event) => {
  event.preventDefault();
  deferredInstallPrompt = event;
  installButton.disabled = false;
  installState.textContent = 'This browser is ready to install Buddy.';
});

window.addEventListener('appinstalled', () => {
  deferredInstallPrompt = null;
  installButton.textContent = 'Buddy installed';
  installButton.disabled = true;
  installState.textContent = 'Installation completed on this device.';
  installGuidance.hidden = true;
});

installButton.addEventListener('click', async () => {
  if (deferredInstallPrompt) {
    deferredInstallPrompt.prompt();
    const choice = await deferredInstallPrompt.userChoice;
    installState.textContent = choice.outcome === 'accepted'
      ? 'Installation accepted. Buddy will appear with your apps.'
      : 'Installation was not completed. Buddy remains available in the browser.';
    deferredInstallPrompt = null;
    return;
  }
  installGuidance.textContent = device.guidance;
  installGuidance.hidden = false;
});

document.getElementById('share-button').addEventListener('click', async () => {
  const shareData = { title: 'Buddy by DreamCo', text: 'Install or open Buddy.', url: new URL('buddy.html', location.href).href };
  try {
    if (navigator.share) await navigator.share(shareData);
    else {
      await navigator.clipboard.writeText(shareData.url);
      installGuidance.textContent = 'Buddy link copied.';
      installGuidance.hidden = false;
    }
  } catch (error) {
    if (error.name !== 'AbortError') {
      installGuidance.textContent = 'Use the browser address to share Buddy from this device.';
      installGuidance.hidden = false;
    }
  }
});

function renderTargets() {
  const selectedFamily = familyFilter.value;
  const targets = catalog.targets.filter((target) => selectedFamily === 'all' || target.family === selectedFamily);
  targetResults.innerHTML = targets.map((target) => `<article class="target-row">
      <span class="target-family">${escapeHtml(target.family.replaceAll('_', ' '))}</span>
      <h3>${escapeHtml(target.name)}</h3>
      <p class="target-details"><strong>Package:</strong> ${escapeHtml(target.artifact)}<br /><strong>Account:</strong> ${escapeHtml(target.account_requirement)}<br /><strong>Gate:</strong> ${escapeHtml(target.release_gate)}</p>
      <span class="target-state ${target.public_status.startsWith('available_now') ? 'ready' : ''}">${escapeHtml(target.public_status.replaceAll('_', ' '))}</span>
    </article>`).join('');
}

function servicePrompt(service) {
  return `Scope DreamCo launch service ${service.name} for my project. Identify target packages, owner accounts, provider fees, evidence gates, timeline, and a written quote. Do not submit, spend, or publish without my exact approval.`;
}

function renderServices() {
  serviceResults.innerHTML = catalog.service_packages.map((service) => `<article class="service-row">
      <span class="service-model">${escapeHtml(service.commercial_model.replaceAll('_', ' '))}</span>
      <h3>${escapeHtml(service.name)}</h3>
      <p class="service-deliverables">${escapeHtml(service.deliverables.join(' · '))}</p>
      <a class="btn btn-primary btn-sm" href="buddy.html?prompt=${encodeURIComponent(servicePrompt(service))}">Start free assessment</a>
    </article>`).join('');
}

function renderTargetOptions() {
  document.getElementById('release-target-options').innerHTML = catalog.targets.map((target) => `<label class="release-target-option">
      <input type="checkbox" name="release-target" value="${escapeHtml(target.target_id)}" ${target.target_id === 'web_browser' || target.target_id === 'pwa' ? 'checked' : ''} />
      <span>${escapeHtml(target.name)}</span>
    </label>`).join('');
}

document.querySelectorAll('[data-view]').forEach((button) => {
  button.addEventListener('click', () => {
    document.querySelectorAll('[data-view]').forEach((item) => item.classList.remove('active'));
    document.querySelectorAll('.distribution-view').forEach((item) => item.classList.remove('active'));
    button.classList.add('active');
    document.getElementById(`${button.dataset.view}-view`).classList.add('active');
  });
});

familyFilter.addEventListener('change', renderTargets);

function buildLocalPlan() {
  const targetIds = [...document.querySelectorAll('input[name="release-target"]:checked')].map((input) => input.value);
  const targets = catalog.targets.filter((target) => targetIds.includes(target.target_id));
  const productType = document.getElementById('project-type').value;
  const services = catalog.service_packages.filter((service) => (
    service.project_types.includes(productType)
    && targets.some((target) => service.target_families.includes(target.family))
  ));
  return {
    schema: 'dreamco.public_distribution_brief.v1',
    created_at: new Date().toISOString(),
    project: {
      name: document.getElementById('project-name').value.trim(),
      type: productType,
      audience: document.getElementById('project-audience').value.trim(),
      source_reference: document.getElementById('source-reference').value.trim(),
      rights_confirmed: document.getElementById('rights-confirmed').checked,
      targets_children: document.getElementById('targets-children').checked,
    },
    targets,
    matched_services: services.map((service) => ({ service_id: service.service_id, name: service.name })),
    gates: ['build', 'tests', 'security', 'privacy', 'accessibility', 'rights', 'rollback'],
    automatic_submission: false,
    automatic_payment: false,
    quote_status: 'scoped_assessment_required',
  };
}

function renderPlan(plan) {
  const output = document.getElementById('release-output');
  const project = plan.project;
  const targetNames = plan.targets.map((target) => target.name).join(', ');
  const prompt = `Prepare a scoped distribution assessment for ${project.name}, a ${project.type}. Audience: ${project.audience}. Targets: ${targetNames}. Source: ${project.source_reference}. Rights confirmed: ${project.rights_confirmed}. Children: ${project.targets_children}. Show package requirements, account and provider fees, evidence gates, delivery phases, and a written quote. Stop before any payment, upload, submission, or publication.`;
  output.innerHTML = `<h3>Release brief ready</h3>
    <div class="release-summary">
      <div><span>Project</span><strong>${escapeHtml(project.name)}</strong></div>
      <div><span>Targets</span><strong>${plan.targets.length}</strong></div>
      <div><span>Service matches</span><strong>${plan.matched_services.length}</strong></div>
      <div><span>External action</span><strong>Owner approval required</strong></div>
    </div>
    <div class="release-output-actions">
      <button id="download-release-plan" class="btn btn-outline" type="button">Download plan</button>
      <a class="btn btn-primary" href="buddy.html?prompt=${encodeURIComponent(prompt)}">Request scoped quote</a>
    </div>`;
  output.hidden = false;
  document.getElementById('download-release-plan').addEventListener('click', () => {
    const blob = new Blob([JSON.stringify(plan, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${project.name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'project'}-distribution-plan.json`;
    link.click();
    URL.revokeObjectURL(url);
  });
}

document.getElementById('release-form').addEventListener('submit', (event) => {
  event.preventDefault();
  const status = document.getElementById('release-form-status');
  const targetCount = document.querySelectorAll('input[name="release-target"]:checked').length;
  if (!targetCount) {
    status.textContent = 'Select at least one release target.';
    return;
  }
  status.textContent = '';
  latestPlan = buildLocalPlan();
  renderPlan(latestPlan);
});

fetch('data/buddy-distribution-catalog.json', { cache: 'no-store' })
  .then((response) => response.ok ? response.json() : Promise.reject(new Error(`Distribution catalog returned ${response.status}`)))
  .then((data) => {
    catalog = data;
    document.getElementById('target-count').textContent = data.summary.targets;
    document.getElementById('family-count').textContent = data.summary.families;
    document.getElementById('service-count').textContent = data.summary.services;
    const families = [...new Set(data.targets.map((target) => target.family))].sort();
    familyFilter.insertAdjacentHTML('beforeend', families.map((family) => `<option value="${escapeHtml(family)}">${escapeHtml(family.replaceAll('_', ' '))}</option>`).join(''));
    renderTargets();
    renderServices();
    renderTargetOptions();
  })
  .catch((error) => {
    targetResults.innerHTML = `<p class="target-row">${escapeHtml(error.message)}</p>`;
  });
