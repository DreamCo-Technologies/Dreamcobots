(function () {
  'use strict';

  const repository = {
    owner: 'DreamCo-Technologies',
    name: 'Dreamcobots',
    url: 'https://github.com/DreamCo-Technologies/Dreamcobots',
    actions: 'https://github.com/DreamCo-Technologies/Dreamcobots/actions',
    issues: 'https://github.com/DreamCo-Technologies/Dreamcobots/issues',
    pulls: 'https://github.com/DreamCo-Technologies/Dreamcobots/pulls',
    pages: 'https://dreamco-technologies.github.io/Dreamcobots/',
  };

  function launcher(id, label, prompt, workspace, options) {
    return {
      id,
      label,
      prompt,
      workspace,
      options: options.map((option, index) => ({
        id: `${id}-${String(index + 1).padStart(2, '0')}`,
        label: option,
      })),
    };
  }

  const launchers = [
    launcher('prototype', 'Build a prototype', 'Build a working prototype from my idea with acceptance criteria, a local preview, tests, ROI, and a reversible launch plan.', 'codelab.html', [
      'Define the customer problem', 'Choose the target user', 'Write acceptance criteria', 'Map the core workflow', 'Choose web, mobile, desktop, or device',
      'Select a prototype fidelity', 'Create the information architecture', 'Draft the data model', 'Design the API contract', 'Plan authentication',
      'Plan local-first storage', 'Choose accessibility requirements', 'Create responsive layouts', 'Build the smallest working feature', 'Add realistic sample data',
      'Create a live preview', 'Add unit tests', 'Add end-to-end tests', 'Add security checks', 'Add privacy checks',
      'Estimate build cost', 'Calculate customer ROI', 'Create a rollback checkpoint', 'Prepare GitHub branch changes', 'Prepare a pull request',
      'Prepare deployment configuration', 'Create monitoring checks', 'Write user documentation', 'Run a launch-readiness review', 'Package the prototype for delivery',
    ]),
    launcher('movie', 'Make a movie', 'Build an original movie or music-video production packet with a governed production group, rights records, accessibility, quality gates, and a renderer plan.', 'studio.html?type=feature_film', [
      'Define the audience and format', 'Develop the original concept', 'Write the treatment', 'Build the screenplay outline', 'Create the character bible',
      'Assign character roles', 'Tune character personality traits', 'Choose original, owner, performer, or mascot identity', 'Create the director treatment', 'Build storyboards',
      'Create a previs animatic plan', 'Design sets and locations', 'Plan wardrobe and props', 'Create the camera and lens plan', 'Create the lighting plan',
      'Select local voice and image engines', 'Plan virtual production', 'Build the VFX shot manifest', 'Create sound-design direction', 'Create an original-score brief',
      'Build the music-video treatment', 'Prepare the edit decision plan', 'Plan color and finishing', 'Create captions and transcripts', 'Plan audio description',
      'Create localization materials', 'Build consent, rights, and provenance records', 'Run identity, quality, and safety benchmarks', 'Define delivery masters', 'Prepare the release and audience test',
    ]),
    launcher('simulation', 'Build a simulation game', 'Turn an approved vehicle, building, product, job, classroom, or custom idea into a model-based simulation and optional practice game.', 'studio.html?type=skills_training_simulation', [
      'Choose the simulation domain', 'Define the learning objective', 'Choose a procedural model', 'Import an owner-provided model', 'Record model ownership evidence',
      'Set concept fidelity', 'Set training fidelity', 'Prepare an engineering-review packet', 'Configure paint and materials', 'Configure parts and additions',
      'Build before-and-after views', 'Define legal player actions', 'Create the rules engine', 'Create measurable outcomes', 'Add guided practice',
      'Add feedback after each action', 'Build a difficulty ladder', 'Add safe failure and reset', 'Create scoring and progress', 'Build instructor controls',
      'Create accessibility settings', 'Create a vehicle repair scenario', 'Create a vehicle customization scenario', 'Create a home addition scenario', 'Create a construction practice scenario',
      'Create a product prototype scenario', 'Create a science lab scenario', 'Create a business operations scenario', 'Run deterministic playtests', 'Package the simulation as a game',
    ]),
    launcher('connection', 'Connect an app', 'Prepare a permissioned app connection. Start read-only, minimize scopes, test in a sandbox, and request exact approval before every write.', 'connections.html', [
      'Connect GitHub read-only', 'Prepare GitHub write approval', 'Connect Google Drive', 'Connect Gmail', 'Connect Google Calendar',
      'Connect Microsoft Outlook', 'Connect Microsoft OneDrive', 'Connect Slack', 'Connect Microsoft Teams', 'Connect Discord',
      'Connect a CRM', 'Connect a customer database', 'Connect a business server', 'Connect a REST API', 'Connect a GraphQL API',
      'Connect a webhook', 'Connect Stripe read-only', 'Connect PayPal read-only', 'Connect Square read-only', 'Connect accounting software',
      'Connect an ecommerce store', 'Connect a social account', 'Connect an app-store account', 'Connect cloud storage', 'Connect a local folder',
      'Choose minimum permissions', 'Create a secret reference', 'Build a sandbox connection test', 'Create a revocation plan', 'Run a connection security review',
    ]),
    launcher('domain', 'Launch a domain', 'Prepare a free preview first, then compare domain choices, DNS, renewal costs, certificates, publishing evidence, and exact purchase approval.', 'install.html', [
      'Use the free GitHub Pages address', 'Use the free Vercel preview address', 'Prepare a custom domain search', 'Generate brandable domain ideas', 'Check domain naming risks',
      'Compare registrar prices', 'Compare renewal prices', 'Check transfer fees', 'Choose a top-level domain', 'Check international domains',
      'Prepare a subdomain', 'Prepare DNS records', 'Prepare email DNS records', 'Prepare domain verification', 'Prepare an SSL certificate',
      'Configure HTTPS redirects', 'Configure the home-page route', 'Configure a custom 404 page', 'Create a staging domain', 'Create a production domain',
      'Plan domain privacy', 'Plan account recovery', 'Plan registrar lock', 'Plan automatic renewal', 'Set a renewal reminder',
      'Prepare GitHub Pages deployment', 'Prepare static-host deployment', 'Run link and route tests', 'Create rollback instructions', 'Prepare purchase and publish approval',
    ]),
    launcher('specialist', 'Choose a specialist', 'Find the best verified Buddy specialist, show capability evidence, and prepare a sandbox task packet.', 'bots.html', [
      'Match by desired outcome', 'Match by declared capability', 'Match by business division', 'Match by industry', 'Match by software tool',
      'Match by API requirement', 'Match by privacy level', 'Match by risk level', 'Match by professional license need', 'Match by physical work need',
      'Choose a coding specialist', 'Choose a sales specialist', 'Choose a payments specialist', 'Choose a government specialist', 'Choose a real-estate specialist',
      'Choose a creative specialist', 'Choose a game specialist', 'Choose an education specialist', 'Choose a legal support specialist', 'Choose a medical admin specialist',
      'Choose a security specialist', 'Choose a data specialist', 'Choose an automation specialist', 'Choose a marketing specialist', 'Choose a finance support specialist',
      'Compare specialist capability tests', 'Review the specialist prospectus', 'Open the specialist ROI calculator', 'Build a specialist team', 'Call the selected specialist in Buddy',
    ]),
    launcher('government', 'Find government help', 'Find official government resources for my jurisdiction, verify dates and eligibility, and prepare a checklist without submitting anything.', 'government.html', [
      'Find federal programs', 'Find state programs', 'Find county programs', 'Find city programs', 'Find tribal government programs',
      'Find government contracts', 'Find requests for proposal', 'Find procurement notices', 'Find small-business set-asides', 'Find grants',
      'Find business loans', 'Find tax-credit information', 'Find workforce programs', 'Find training programs', 'Find export assistance',
      'Find disaster assistance', 'Find housing resources', 'Find education resources', 'Find health program information', 'Find benefits screening resources',
      'Find licensing requirements', 'Find permit requirements', 'Find business registration steps', 'Find nonprofit resources', 'Find research funding',
      'Verify the official source', 'Verify jurisdiction', 'Verify eligibility rules', 'Track deadlines and documents', 'Prepare an approval-ready application checklist',
    ]),
    launcher('models', 'Compare coding models', 'Compare licensed models on reproducible coding checkpoints, hardware, privacy, quality, latency, and cost without scoring by nationality.', 'models.html', [
      'Compare code generation', 'Compare repository understanding', 'Compare bug diagnosis', 'Compare test generation', 'Compare code review',
      'Compare dependency repair', 'Compare frontend development', 'Compare backend development', 'Compare API development', 'Compare database work',
      'Compare mobile development', 'Compare browser automation', 'Compare long-context handling', 'Compare tool calling', 'Compare structured output',
      'Compare reasoning evidence', 'Compare hallucination rate', 'Compare security behavior', 'Compare privacy and local use', 'Compare open licenses',
      'Compare hardware requirements', 'Compare memory requirements', 'Compare latency', 'Compare energy use', 'Compare paid cost',
      'Compare free-tier limits', 'Run signed benchmark fixtures', 'Compare against the prior release', 'Select the best model per task', 'Prepare a reproducible benchmark report',
    ]),
    launcher('discover', 'Help me figure it out', 'Help me define an unfamiliar task, identify the right level of automation, teach the missing steps, and begin safely.', 'buddy.html', [
      'Define what success looks like', 'Identify the people affected', 'List known constraints', 'Choose time, cost, or quality priority', 'Break the goal into tasks',
      'Classify fully automatable tasks', 'Classify approval-gated tasks', 'Identify human-supervised work', 'Identify licensed-professional work', 'Identify physical work',
      'Reject prohibited or deceptive work', 'Find the required specialists', 'Find the required tools', 'Find the required APIs', 'Find official learning resources',
      'Create a beginner explanation', 'Create a step-by-step lesson', 'Create a practice exercise', 'Create a sandbox demonstration', 'Create acceptance tests',
      'Estimate costs', 'Estimate time', 'Identify privacy risks', 'Identify safety risks', 'Identify missing credentials',
      'Compare possible approaches', 'Choose the smallest first step', 'Create an approval map', 'Create a checkpoint and rollback plan', 'Start the safe parts with Buddy',
    ]),
    launcher('search', 'Search the web', 'Prepare a focused, source-aware web or repository search. Prefer official sources and do not submit, sign in, scrape, or change accounts.', 'open-model-lab.html', [
      'Search official documentation', 'Search government sources', 'Search GitHub repositories', 'Search GitHub issues', 'Search GitHub pull requests',
      'Search open-source licenses', 'Search software releases', 'Search security advisories', 'Search research papers', 'Search model documentation',
      'Search API documentation', 'Search webhook documentation', 'Search app-store requirements', 'Search domain documentation', 'Search cloud documentation',
      'Search grants', 'Search government contracts', 'Search requests for proposal', 'Search public job listings', 'Search market demand',
      'Search competitors', 'Search pricing and free tiers', 'Search product reviews', 'Search accessibility standards', 'Search privacy requirements',
      'Search legal information sources', 'Search health information sources', 'Compare multiple sources', 'Save a source checklist', 'Open one approved browser search',
    ]),
    launcher('customize', 'Customize Buddy', 'Create an owner-controlled Buddy identity with roles, personality, original presets or approved adult media, consent, rights, provenance, revocation, and local quality benchmarks.', 'studio.html', [
      'Choose the Buddy display name', 'Choose personal or business use', 'Assign the primary Buddy role', 'Assign supporting Buddy roles', 'Set the warmth level',
      'Set the directness level', 'Set the curiosity level', 'Set the humor level', 'Set the patience level', 'Set the energy level',
      'Set the formality level', 'Set the creativity level', 'Choose an original avatar preset', 'Upload an approved company mascot', 'Configure an adult owner likeness',
      'Configure a licensed adult performer', 'Choose a free browser voice', 'Select the OpenVoice V2 adapter', 'Select the Chatterbox adapter', 'Record an approved voice sample',
      'Capture an approved image sample', 'Create a scoped consent receipt', 'Create a written rights receipt', 'Configure the synthetic-media label', 'Configure the provenance manifest',
      'Configure revocation controls', 'Run a local media license review', 'Run the voice quality benchmark', 'Run image and lip-sync benchmarks', 'Save the owner-controlled profile',
    ]),
    launcher('workspace', 'Group apps and tasks', 'Build a permissioned workspace that groups apps, repositories, data, specialists, and timed tasks around one outcome without granting background control.', 'connections.html', [
      'Name the outcome workspace', 'Define the finished result', 'Add a repository', 'Add an owner-approved local folder', 'Add a read-only cloud folder',
      'Add a customer database', 'Add a business server', 'Add a browser research source', 'Add a communication channel', 'Add a calendar',
      'Add a CRM connection', 'Add a payment read view', 'Choose the lead specialist', 'Add supporting specialists', 'Map task dependencies',
      'Group related apps', 'Group related browser tabs', 'Create a read-only connection pass', 'Create one-action write approvals', 'Set credential reference boundaries',
      'Choose local-first storage', 'Choose useful-data retention rules', 'Create a recurring task', 'Create an indefinite schedule', 'Set per-run time limits',
      'Add checkpoints and rollback', 'Add pause and cancel controls', 'Create a workspace audit log', 'Run the workspace sandbox test', 'Open the owner-approved workspace',
    ]),
    launcher('sales-team', 'Build a sales department', 'Configure the attached governed sales worker teams for research, preparation, coaching, CRM operations, proposals, closing support, and customer success with permission and approval gates.', 'leads.html', [
      'Set revenue goals and capacity', 'Define the ideal customer profile', 'Choose permitted lead sources', 'Create candidate deduplication', 'Build company research',
      'Map decision makers lawfully', 'Detect source-backed buying signals', 'Create pain-point evidence', 'Build the lead scoring rubric', 'Create the owner review queue',
      'Draft permission-aware email', 'Draft permission-aware messages', 'Create an approved call script', 'Configure one-message approval', 'Configure opt-out suppression',
      'Build the follow-up timing plan', 'Create appointment preparation', 'Create the needs assessment', 'Create objection practice', 'Create a product demonstration plan',
      'Build a proposal template', 'Build a quote calculator', 'Build an ROI calculator', 'Create price scenarios', 'Prepare a contract draft',
      'Create a negotiation sandbox', 'Create a closing checklist', 'Create customer onboarding', 'Build the sales dashboard', 'Run the sales quality certification',
    ]),
    launcher('opportunity', 'Find paid work', 'Use the Shadow Mode opportunity engine to analyze authorized demand signals, classify tasks A-F, match real Buddy specialists, build sandbox services, and prepare owner-controlled next steps without promising earnings.', 'buddy.html', [
      'Add an owner-supplied opportunity', 'Add a public listing reference', 'Add an authorized opportunity feed', 'Extract job responsibilities', 'Classify level A digital work',
      'Classify level B approval work', 'Classify level C supervised work', 'Classify level D professional work', 'Classify level E physical work', 'Reject level F prohibited work',
      'Detect sensitive data needs', 'Match real Buddy specialists', 'Identify licensed professionals', 'Estimate automation percentage', 'Estimate human effort',
      'Estimate delivery cost', 'Prepare a suggested price', 'Calculate estimated margin', 'Record that earnings are not guaranteed', 'Create the service definition',
      'Create acceptance criteria', 'Build a synthetic sandbox demo', 'Run feasibility tests', 'Run the risk review', 'Prepare the owner approval packet',
      'Prepare a truthful proposal', 'Prepare a permissioned outreach draft', 'Create delivery quality gates', 'Create invoice approval steps', 'Add outcome learning evidence',
    ]),
    launcher('payments', 'Set up payments', 'Prepare a provider-neutral payment operations plan with verified fees, sandbox evidence, quotes, invoices, subscriptions, reconciliation, notifications, and fresh approval before every charge or transfer.', 'payments.html', [
      'Choose the payment use case', 'Choose supported currencies', 'Compare card processing', 'Compare bank transfers', 'Compare digital wallets',
      'Review crypto payment limits', 'Verify each provider identity', 'Verify regional availability', 'Verify current provider fees', 'Verify settlement timing',
      'Choose the lowest-cost route', 'Choose the most reliable route', 'Create a quote template', 'Create an estimate template', 'Create an invoice template',
      'Create a subscription plan', 'Create an installment plan', 'Create a revenue-share plan', 'Create an affiliate payout plan', 'Create a commission calculator',
      'Configure tax record fields', 'Configure payment notifications', 'Configure reconciliation checks', 'Configure chargeback assistance', 'Create a financial forecast',
      'Create backend secret references', 'Run provider sandbox fixtures', 'Preview one transaction', 'Request one-transaction approval', 'Create the immutable audit record',
    ]),
    launcher('practice', 'Practice a role', 'Build a private job-prep or role-play session with verified specialists, realistic rounds, voice practice, evidence review, and no real-world impersonation or external action.', 'practice.html', [
      'Prepare for a job interview', 'Build a career evidence map', 'Review resume achievements', 'Create STAR answer stories', 'Practice role-specific questions',
      'Practice a sales discovery call', 'Practice handling objections', 'Practice customer support', 'Practice a manager conversation', 'Practice giving feedback',
      'Practice a negotiation', 'Practice a presentation', 'Practice investor questions', 'Practice an acting audition', 'Practice a creator introduction',
      'Practice another language', 'Choose a supportive partner', 'Choose a realistic partner', 'Choose a challenging partner', 'Set the number of rounds',
      'Answer by text', 'Answer by voice', 'Record an approved owner voice', 'Review answer structure', 'Review specific evidence',
      'Review active listening', 'Review professional boundaries', 'Create a learning sprint', 'Prepare follow-up questions', 'Continue the role-play with Buddy',
    ]),
    launcher('benchmark', 'Benchmark a bot', 'Build a reproducible competition and quality benchmark for a Buddy bot, model, voice, image, video, workflow, or release using signed fixtures and measured evidence.', 'test-center.html', [
      'Choose the benchmark subject', 'Choose the comparison baseline', 'Create a feature matrix', 'Create a capability inventory', 'Detect missing capabilities',
      'Detect duplicate capabilities', 'Compare workflow completion', 'Compare user experience', 'Compare API behavior', 'Compare automation behavior',
      'Measure instruction following', 'Measure task accuracy', 'Measure latency', 'Measure memory use', 'Measure CPU use',
      'Measure GPU use', 'Measure reliability', 'Measure failure recovery', 'Measure scalability', 'Measure security behavior',
      'Measure accessibility', 'Measure voice identity', 'Measure voice intelligibility', 'Measure image identity', 'Measure lip synchronization',
      'Run rights and consent gates', 'Run license readiness checks', 'Compare against the prior release', 'Create an executive scorecard', 'Block unsupported quality claims',
    ]),
  ];

  window.BUDDY_SETUP_CATALOG = {
    schema: 'dreamco.buddy_setup_catalog.v1',
    repository,
    summary: {
      launcherCount: launchers.length,
      optionsPerLauncher: 30,
      setupOptionCount: launchers.reduce((total, item) => total + item.options.length, 0),
    },
    launchers,
  };
})();
