(() => {
  const form = document.getElementById('dreamco-investigation-form');
  if (!form) return;
  const byId = (id) => document.getElementById(id);
  const select = byId('dreamco-target-kind');
  let policy;

  function downloadPlan(value) {
    const blob = new Blob([`${JSON.stringify(value, null, 2)}\n`], { type: 'application/json' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'dreamco-authorized-investigation-plan.json';
    link.click();
    URL.revokeObjectURL(link.href);
  }

  fetch('data/dreamco-investigation-profiles.json', { cache: 'no-store' })
    .then((response) => { if (!response.ok) throw new Error('profiles unavailable'); return response.json(); })
    .then((data) => {
      policy = data;
      Object.entries(data.profiles).forEach(([id, profile]) => {
        const option = document.createElement('option');
        option.value = id;
        option.textContent = profile.label;
        select.append(option);
      });
    })
    .catch(() => { byId('dreamco-investigation-status').textContent = 'Investigation profiles are unavailable. No plan was created.'; });

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    if (!policy) return;
    const kind = select.value;
    const reference = byId('dreamco-target-reference').value.trim();
    const revision = byId('dreamco-target-revision').value.trim();
    const scope = byId('dreamco-target-scope').value.replace(/\s+/g, ' ').trim();
    const customizations = [...form.querySelectorAll('input[name="dreamco-customization"]:checked')].map((input) => input.value);
    const differentiator = byId('dreamco-target-differentiator').value.replace(/\s+/g, ' ').trim();
    let validRemote = true;
    const windowsPath = /^[A-Za-z]:[\\/]/.test(reference);
    if (!windowsPath && /^[A-Za-z][A-Za-z0-9+.-]*:/.test(reference)) {
      try {
        const url = new URL(reference);
        validRemote = url.protocol === 'https:' && Boolean(url.hostname) && !url.username && !url.password;
      } catch { validRemote = false; }
    }
    const needsRevision = ['code_repository', 'open_weights_model'].includes(kind);
    const floating = ['main', 'master', 'latest', 'head', 'stable', 'dev', 'develop'].includes(revision.toLowerCase());
    const authorized = byId('dreamco-target-authorized').checked;
    const blockers = [];
    if (!authorized) blockers.push('owner_authorization_required');
    if (!reference || !validRemote) blockers.push('valid_local_reference_or_credential_free_https_url_required');
    if (scope.length < 20) blockers.push('specific_written_scope_required');
    if (needsRevision && (revision.length < 7 || floating)) blockers.push('immutable_revision_or_content_hash_required');
    if (customizations.length < 2) blockers.push('at_least_two_customizations_required');
    if (differentiator.length < 30) blockers.push('original_differentiator_required');
    if (blockers.length) {
      byId('dreamco-investigation-status').textContent = `Blocked: ${blockers.join(', ')}.`;
      return;
    }
    const profile = policy.profiles[kind];
    const plan = {
      schema: 'dreamco.authorized_investigation_plan.v1',
      system: 'DreamCo Code Workbench',
      target: { kind, label: profile.label, reference, revision: revision || null },
      authorization: { owner_confirmed: true, written_scope: scope },
      evidence_to_collect: profile.evidence,
      test_plan: profile.tests,
      execution_controls: {
        execution_requested: byId('dreamco-plan-run-intent').checked,
        execution_started: false,
        adapter_required: true,
        network_default: 'off',
        profile_controls: profile.execution,
        host_secrets_available: false,
        production_write_access: false,
      },
      customization: { areas: [...new Set(customizations)], original_differentiator: differentiator },
      universal_gates: policy.universal_gates,
      prohibited: policy.never_automate,
      truth_boundary: 'This is a plan, not a connection or test result. A configured isolated adapter must execute the plan and record evidence.',
    };
    downloadPlan(plan);
    byId('dreamco-investigation-status').textContent = 'Plan downloaded. No target was connected and no test ran.';
  });
})();
