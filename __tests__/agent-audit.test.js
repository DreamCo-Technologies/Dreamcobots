const {
  validateBotsConfig,
  validateCommandCenterConfig,
  runAudit
} = require('../automation-tools/agents/agent-audit');

describe('agent audit', () => {
  it('passes for repository agent and command center configs', () => {
    const result = runAudit(process.cwd());
    expect(result.ok).toBe(true);
    expect(result.issues).toEqual([]);
    expect(result.checked.totalBots).toBeGreaterThan(0);
    expect(result.checked.totalLanes).toBeGreaterThan(0);
  });

  it('flags incomplete task statuses in command center tracks', () => {
    const issues = validateCommandCenterConfig({
      parallel_lanes: [{ lane_id: 'sync', owner: 'Automation', status: 'Pending', ship_decision: 'pending' }]
    });

    expect(issues.join('\n')).toMatch(/incomplete status/i);
  });

  it('flags invalid bot entries', () => {
    const issues = validateBotsConfig([{ status: 'active' }]);

    expect(issues.join('\n')).toMatch(/missing name/i);
  });
});
