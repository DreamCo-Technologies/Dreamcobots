(() => {
  const learning = window.BUDDY_OPEN_MODEL_CODING_LAB.buddy_open_core.learning_system;
  const catalog = window.BUDDY_LEARNING_STRATEGIES;
  const byId = (id) => document.getElementById(id);
  const title = (value) => value.replaceAll('_', ' ').replace(/\b\w/g, (letter) => letter.toUpperCase());
  const mean = (scores) => scores.reduce((sum, score) => sum + score, 0) / scores.length;
  const computeRank = new Map(['low', 'medium', 'high', 'very_high'].map((level, index) => [level, index]));
  let evidence = null;
  let study = null;

  byId('method-count').textContent = catalog.techniques.length;
  byId('failure-count').textContent = catalog.failure_controls.length;
  byId('cycle-count').textContent = learning.required_cycle.length;
  byId('method').innerHTML = catalog.techniques.map((technique) => `<option value="${technique.id}">${technique.label}</option>`).join('');
  const categories = [...new Set(catalog.techniques.map((technique) => technique.category))];
  byId('category-filter').innerHTML = '<option value="all">All categories</option>' + categories.map((category) => `<option value="${category}">${title(category)}</option>`).join('');
  byId('objective-filter').innerHTML = '<option value="all">All goals</option>' + catalog.objectives.map((objective) => `<option value="${objective}">${title(objective)}</option>`).join('');
  byId('study-objective').innerHTML = catalog.objectives.map((objective) => `<option value="${objective}">${title(objective)}</option>`).join('');
  byId('study-objective').value = 'study_efficiency';
  const renderTechniques = () => {
    const category = byId('category-filter').value;
    const objective = byId('objective-filter').value;
    const techniques = catalog.techniques.filter((technique) => (category === 'all' || technique.category === category) && (objective === 'all' || technique.objectives.includes(objective)));
    byId('method-grid').innerHTML = techniques.map((technique) => `<article class="card"><h3>${technique.label}</h3><p>${technique.purpose}</p><p class="muted">${title(technique.category)} · ${title(technique.compute)} compute · ${title(technique.status)}</p><a target="_blank" rel="noopener" href="${technique.official_source}">Research source</a></article>`).join('');
  };
  byId('category-filter').addEventListener('change', renderTechniques);
  byId('objective-filter').addEventListener('change', renderTechniques);
  renderTechniques();
  byId('failure-grid').innerHTML = catalog.failure_controls.map((control) => `<article class="card"><h3>${title(control.id)}</h3><p>${control.purpose}</p><p class="muted">${title(control.action)} · ${control.direction} ${control.threshold}</p></article>`).join('');
  byId('innovation-grid').innerHTML = learning.innovation_tracks.map((track) => `<article class="card"><p>${track}</p></article>`).join('');
  byId('reference-grid').innerHTML = learning.research_references.map((reference) => `<article class="card"><h3>${reference.label}</h3><p>${reference.buddy_extension}</p><p class="muted">${title(reference.comparison_status)}</p><a class="btn btn-outline" target="_blank" rel="noopener" href="${reference.official_source}">Official source</a></article>`).join('');
  byId('cycle-grid').innerHTML = learning.required_cycle.map((step, index) => `<article class="card"><strong>${index + 1}</strong><p>${step}</p></article>`).join('');

  const readScores = (id) => {
    const parts = byId(id).value.split(',').map((value) => value.trim());
    const values = parts.map(Number);
    if (values.length < learning.promotion_thresholds.minimum_repetitions || parts.some((value) => !value) || values.some((value) => !Number.isFinite(value) || value < 0 || value > 1)) {
      throw new Error(`${title(id)} needs at least ${learning.promotion_thresholds.minimum_repetitions} scores between 0 and 1.`);
    }
    return values;
  };

  const techniquePriority = (technique, objective) => {
    let score = technique.objectives.includes(objective) ? 10 : 0;
    if (technique.objectives.includes('study_efficiency')) score += 3;
    if (technique.compute === 'low') score += 3;
    if (technique.compute === 'medium') score += 2;
    if (technique.category === 'experiment_optimization') score -= 1;
    return score;
  };

  byId('study-form').addEventListener('submit', (event) => {
    event.preventDefault();
    try {
      const seedParts = byId('study-seeds').value.split(',').map((value) => value.trim());
      const seeds = seedParts.map(Number);
      if (seeds.length < catalog.study_optimizer.minimum_repetitions || seedParts.some((value) => !value) || seeds.some((seed) => !Number.isInteger(seed) || seed < 1) || new Set(seeds).size !== seeds.length) throw new Error(`Use at least ${catalog.study_optimizer.minimum_repetitions} unique positive integer seeds.`);
      if (byId('study-dataset-hash').value.toLowerCase() === byId('study-holdout-hash').value.toLowerCase()) throw new Error('Training and hidden-holdout manifests must be different.');
      const objective = byId('study-objective').value;
      const maximumCompute = byId('study-compute').value;
      const maximumTechniques = Number(byId('study-technique-count').value);
      const techniques = catalog.techniques
        .filter((technique) => technique.objectives.includes(objective) && computeRank.get(technique.compute) <= computeRank.get(maximumCompute))
        .sort((left, right) => techniquePriority(right, objective) - techniquePriority(left, objective) || left.id.localeCompare(right.id))
        .slice(0, maximumTechniques);
      if (techniques.length < 2) throw new Error('The selected goal and compute ceiling need at least two eligible techniques.');
      const trialCount = techniques.length * seeds.length;
      const maximumGpuHours = Number(byId('study-gpu-hours').value);
      const maximumCostUsd = Number(byId('study-cost').value);
      const trials = techniques.flatMap((technique) => seeds.map((seed) => ({ trial_id: `${byId('study-id').value}-${technique.id}-${seed}`, technique_id: technique.id, seed, stage: technique.stage, compute: technique.compute, status: 'scheduled_not_executed', isolated_sandbox_required: true, maximum_gpu_hours: maximumGpuHours / trialCount, maximum_cost_usd: maximumCostUsd / trialCount })));
      study = {
        schema: 'dreamco.buddy_learning_study.v1', study_id: byId('study-id').value, capability_id: byId('study-capability').value,
        base_release_id: byId('study-base-release').value, objective, maximum_compute: maximumCompute,
        dataset_manifest_sha256: byId('study-dataset-hash').value, hidden_holdout_manifest_sha256: byId('study-holdout-hash').value,
        techniques, seeds, trials, trial_count: trialCount, same_fixtures_across_techniques: true, controlled_ablation_required: true,
        failure_controls: catalog.failure_controls, scoring: catalog.study_optimizer.default_score_weights,
        status: !byId('study-owner-approval').checked ? 'owner_training_approval_required' : maximumGpuHours <= 0 ? 'execution_resources_required' : 'sandbox_execution_adapter_required',
        automatic_training_started: false, production_weights_modified: false, automatic_production_promotion: false,
      };
      byId('study-grid').innerHTML = techniques.map((technique) => `<article class="card"><h3>${technique.label}</h3><p>${seeds.length} repeat runs · ${title(technique.compute)} compute</p><span class="muted">Scheduled, not executed</span></article>`).join('');
      byId('study-status').textContent = `${trialCount} controlled trials prepared across ${techniques.length} techniques. Status: ${title(study.status)}. No training started.`;
      byId('download-study').disabled = false;
    } catch (error) {
      study = null; byId('download-study').disabled = true; byId('study-grid').innerHTML = '';
      byId('study-status').textContent = error instanceof Error ? error.message : 'Invalid learning study.';
    }
  });

  const downloadJson = (payload, filename) => {
    const link = document.createElement('a');
    link.href = URL.createObjectURL(new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' }));
    link.download = filename; link.click();
    setTimeout(() => URL.revokeObjectURL(link.href), 500);
  };

  byId('download-study').addEventListener('click', () => {
    if (study) downloadJson(study, `${study.study_id}-study.json`);
  });

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
    downloadJson(evidence, `${evidence.cycle_id}-learning-evidence.json`);
  });
})();
