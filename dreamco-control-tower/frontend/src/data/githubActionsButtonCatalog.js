const categories = [
  'Bot Health',
  'Buddy Wiring',
  'GitHub CI',
  'Revenue',
  'Sales',
  'Client Research',
  'Learning',
  'Dashboard',
  'Command Center',
  'Security',
  'Data Quality',
  'MCP Tools',
  'Model Routing',
  'Stripe',
  'Deployment',
  'Reports',
  'Memory',
  'Workflow',
  'Lead Gen',
  'Maintenance',
];

const verbs = [
  'Scan',
  'Repair',
  'Test',
  'Audit',
  'Sync',
  'Route',
  'Generate',
  'Validate',
  'Monitor',
  'Launch',
  'Review',
  'Score',
  'Summarize',
  'Dispatch',
  'Refresh',
  'Compare',
  'Map',
  'Recover',
  'Train',
  'Optimize',
  'Inspect',
  'Package',
  'Publish',
  'Queue',
  'Archive',
];

const workflows = [
  'dreamco-debug-audit.yml',
  'bot-health-scan.yml',
  'buddy-connectivity.yml',
  'stripe-revenue-tracking.yml',
  'repair-bot-metadata-pr.yml',
  'command-tower.yml',
  'dashboard-governance.yml',
  'dreamco-live-dashboard.yml',
];

const risks = ['low', 'medium', 'high'];
const modes = ['observe', 'diagnose', 'test', 'build', 'command'];

function slugify(value) {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
}

export const githubActionsButtonCatalog = Array.from({ length: 500 }, (_, index) => {
  const number = index + 1;
  const category = categories[index % categories.length];
  const verb = verbs[index % verbs.length];
  const risk = risks[index % risks.length];
  const enabled = number <= 120;

  return {
    id: `gha-${String(number).padStart(3, '0')}-${slugify(`${category}-${verb}-${number}`)}`,
    number,
    label: `${verb} ${category}`,
    category,
    workflow: workflows[index % workflows.length],
    risk,
    enabled,
    requiresApproval: risk !== 'low',
    mode: modes[index % modes.length],
    description: `${verb} ${category.toLowerCase()} through GitHub Actions with audit logging.`,
  };
});

export const actionCategories = categories;

export default githubActionsButtonCatalog;
