(() => {
  const learning = window.BUDDY_OPEN_MODEL_CODING_LAB.buddy_open_core.learning_system;
  const byId = (id) => document.getElementById(id);
  const title = (value) => value.replaceAll('_', ' ').replace(/\b\w/g, (letter) => letter.toUpperCase());
  const mean = (scores) => scores.reduce((sum, score) => sum + score, 0) / scores.length;
  let evidence = null;

  byId('method-count').textContent = learning.methods.length;
  byId('track-count').textContent = learning.innovation_tracks.length;
  byId('cycle-count').textContent = learning.required_cycle.length;
  byId('method').innerHTML = learning.methods.map((method) => `<option value="${method}">${title(method)}</option>`).join('');
  byId('method-grid').innerHTML = learning.methods.map((method) => `<article class="card"><h3>${title(method)}</h3><p class="muted">Governed candidate method; training adapter required.</p></article>`).join('');
  byId('innovation-grid').innerHTML = learning.innovation_tracks.map((track) => `<article class="card"><p>${track}</p></article>`).join('');
  byId('reference-grid').innerHTML = learning.research_references.map((reference) => `<article class="card"><h3>${reference.label}</h3><p>${reference.buddy_extension}</p><p class="muted">${title(reference.comparison_status)}</p><a class="btn btn-outline" target="_blank" rel="noopener" href="${reference.official_source}">Official source</a></article>`).join('');
  byId('cycle-grid').innerHTML = learning.required_cycle.map((step, index) => `<article class="card"><strong>${index + 1}</strong><p>${step}</p></article>`).join('');

  const readScores = (id) => {
    const values = byId(id).value.split(',').map((value) => Number(value.trim()));
    if (values.length < learning.promotion_thresholds.minimum_repetitions || values.some((value) => !Number.isFinite(value) || value < 0 || value > 1)) {
      throw new Error(`${title(id)} needs at least ${learning.promotion_thresholds.minimum_repetitions} scores between 0 and 1.`);
    }
    return values;
  };

  byId('learning-form').addEventListener('submit', (event) => {
    event.preventDefault();
    try {
      const scores = {
        baseline: readScores('baseline'), holdoutBefore: readScores('holdout-before'), holdoutAfter: readScores('holdout-after'),
        regressionBefore: readScores('regression-before'), regressionAfter: readScores('regression-after'),
        safetyBefore: readScores('safety-before'), safetyAfter: readScores('safety-after'),
      };
      const averages = Object.fromEntries(Object.entries(scores).map(([key, value]) => [key, mean(value)]));
      const thresholds = learning.promotion_thresholds;
      const gates = {
        failing_baseline_recorded: averages.baseline < thresholds.minimum_holdout_score,
        approved_sources_only: byId('approved-sources').checked,
        license_and_provenance_verified: byId('provenance').checked,
        private_data_excluded_or_consented: byId('privacy').checked,
        sandbox_training_passed: byId('sandbox').checked,
        hidden_holdout_improved: averages.holdoutAfter - averages.holdoutBefore >= thresholds.minimum_absolute_improvement,
        holdout_threshold_met: averages.holdoutAfter >= thresholds.minimum_holdout_score,
        regression_within_limit: averages.regressionBefore - averages.regressionAfter <= thresholds.maximum_regression,
        safety_not_regressed: averages.safetyAfter >= averages.safetyBefore,
        repeated_runs_present: Object.values(scores).every((values) => values.length >= thresholds.minimum_repetitions),
      };
      const improvementProven = Object.values(gates).every(Boolean);
      const ownerApproved = byId('owner-approval').checked;
      evidence = {
        schema: 'dreamco.buddy_learning_evidence.v1', cycle_id: byId('cycle-id').value, base_release_id: byId('base-release').value,
        capability_id: byId('capability-id').value, method: byId('method').value, scores, averages,
        absolute_improvement: averages.holdoutAfter - averages.holdoutBefore, gates,
        source_manifest_sha256: byId('source-hash').value, training_artifact_sha256: byId('artifact-hash').value,
        grader_version: byId('grader-version').value, improvement_proven: improvementProven,
        status: improvementProven ? (ownerApproved ? 'approved_release_candidate' : 'improvement_proven_owner_approval_required') : 'learning_evidence_failed',
        promoted_to_users: false, global_weights_modified: false,
      };
      byId('gate-results').innerHTML = Object.entries(gates).map(([gate, passed]) => `<article class="card gate"><span>${title(gate)}</span><strong class="${passed ? 'pass' : 'fail'}">${passed ? 'PASS' : 'FAIL'}</strong></article>`).join('');
      byId('learning-status').textContent = improvementProven ? `Improvement proven by this evidence packet. ${ownerApproved ? 'A signed, reversible release is still required.' : 'Owner approval is still required.'}` : 'Learning claim rejected. Review the failed gates; no release is allowed.';
      byId('download-evidence').disabled = false;
    } catch (error) {
      evidence = null; byId('download-evidence').disabled = true; byId('gate-results').innerHTML = '';
      byId('learning-status').textContent = error instanceof Error ? error.message : 'Invalid learning evidence.';
    }
  });

  byId('download-evidence').addEventListener('click', () => {
    if (!evidence) return;
    const link = document.createElement('a');
    link.href = URL.createObjectURL(new Blob([JSON.stringify(evidence, null, 2)], { type: 'application/json' }));
    link.download = `${evidence.cycle_id}-learning-evidence.json`; link.click();
    setTimeout(() => URL.revokeObjectURL(link.href), 500);
  });
})();
