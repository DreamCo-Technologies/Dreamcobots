'use strict';

/**
 * DreamCo — Workflow System Tests
 *
 * Validates that all workflow JSON files are well-formed,
 * have required fields, and the master registry is consistent.
 */

const fs = require('fs');
const path = require('path');

const WORKFLOWS_DIR = path.resolve(__dirname, '..', 'workflows');
const REGISTRY_FILE = path.resolve(__dirname, '..', 'workflows.json');

const WORKFLOW_FILES = [
  'fiverr.json',
  'real_estate.json',
  'grants.json',
  'legal_money.json',
  'crypto.json',
];

const REQUIRED_TOP_LEVEL = [
  'id',
  'name',
  'description',
  'trigger',
  'steps',
  'monetization',
  'automation',
  'created_at',
  'version',
];
const REQUIRED_STEP = ['id', 'name', 'action', 'params', 'on_success', 'on_failure'];
const REQUIRED_MONETIZATION = ['model', 'revenue_per_cycle', 'payment_processor'];
const REQUIRED_TRIGGER = ['type'];

// ---------------------------------------------------------------------------
// Load workflows once for efficiency
// ---------------------------------------------------------------------------
const workflows = {};
let registry = null;

beforeAll(() => {
  WORKFLOW_FILES.forEach((file) => {
    const filePath = path.join(WORKFLOWS_DIR, file);
    expect(fs.existsSync(filePath)).toBe(true);
    const raw = fs.readFileSync(filePath, 'utf8');
    workflows[file] = JSON.parse(raw);
  });

  expect(fs.existsSync(REGISTRY_FILE)).toBe(true);
  registry = JSON.parse(fs.readFileSync(REGISTRY_FILE, 'utf8'));
});

// ---------------------------------------------------------------------------
// workflows.json registry
// ---------------------------------------------------------------------------
describe('workflows.json registry', () => {
  test('registry file exists and is valid JSON', () => {
    expect(registry).toBeDefined();
    expect(typeof registry).toBe('object');
  });

  test('registry has version field', () => {
    expect(registry).toHaveProperty('version');
    expect(typeof registry.version).toBe('string');
  });

  test('registry has workflows array with 5 entries', () => {
    expect(Array.isArray(registry.workflows)).toBe(true);
    expect(registry.workflows.length).toBe(5);
  });

  test('each registry entry has id, file, enabled, priority', () => {
    registry.workflows.forEach((entry) => {
      expect(entry).toHaveProperty('id');
      expect(entry).toHaveProperty('file');
      expect(typeof entry.enabled).toBe('boolean');
      expect(typeof entry.priority).toBe('number');
    });
  });

  test('registry has global_settings', () => {
    expect(registry).toHaveProperty('global_settings');
    expect(registry.global_settings).toHaveProperty('max_concurrent_workflows');
    expect(registry.global_settings).toHaveProperty('default_retry_attempts');
    expect(registry.global_settings).toHaveProperty('notify_on_failure');
  });

  test('registry workflow IDs match the 5 expected IDs', () => {
    const ids = registry.workflows.map((w) => w.id);
    expect(ids).toContain('fiverr');
    expect(ids).toContain('real_estate');
    expect(ids).toContain('grants');
    expect(ids).toContain('legal_money');
    expect(ids).toContain('crypto');
  });

  test('each registry file path points to an existing workflow file', () => {
    registry.workflows.forEach((entry) => {
      const fullPath = path.resolve(__dirname, '..', entry.file);
      expect(fs.existsSync(fullPath)).toBe(true);
    });
  });

  test('priorities are unique', () => {
    const priorities = registry.workflows.map((w) => w.priority);
    const uniquePriorities = new Set(priorities);
    expect(uniquePriorities.size).toBe(priorities.length);
  });
});

// ---------------------------------------------------------------------------
// Individual workflow validation
// ---------------------------------------------------------------------------
WORKFLOW_FILES.forEach((file) => {
  describe(`Workflow: ${file}`, () => {
    let wf;

    beforeAll(() => {
      wf = workflows[file];
    });

    test('has all required top-level fields', () => {
      REQUIRED_TOP_LEVEL.forEach((field) => {
        expect(wf).toHaveProperty(field);
      });
    });

    test('id is a non-empty string', () => {
      expect(typeof wf.id).toBe('string');
      expect(wf.id.length).toBeGreaterThan(0);
    });

    test('name is a non-empty string', () => {
      expect(typeof wf.name).toBe('string');
      expect(wf.name.length).toBeGreaterThan(0);
    });

    test('description is a non-empty string', () => {
      expect(typeof wf.description).toBe('string');
      expect(wf.description.length).toBeGreaterThan(0);
    });

    test('trigger has required fields', () => {
      REQUIRED_TRIGGER.forEach((field) => {
        expect(wf.trigger).toHaveProperty(field);
      });
      const validTypes = ['cron', 'webhook', 'manual'];
      expect(validTypes).toContain(wf.trigger.type);
    });

    test('steps is an array with at least 3 steps', () => {
      expect(Array.isArray(wf.steps)).toBe(true);
      expect(wf.steps.length).toBeGreaterThanOrEqual(3);
    });

    test('each step has all required step fields', () => {
      wf.steps.forEach((step) => {
        REQUIRED_STEP.forEach((field) => {
          expect(step).toHaveProperty(field);
        });
      });
    });

    test('step IDs are unique within the workflow', () => {
      const ids = wf.steps.map((s) => s.id);
      const unique = new Set(ids);
      expect(unique.size).toBe(ids.length);
    });

    test('monetization has required fields', () => {
      REQUIRED_MONETIZATION.forEach((field) => {
        expect(wf.monetization).toHaveProperty(field);
      });
    });

    test('monetization.revenue_per_cycle is a positive number', () => {
      expect(typeof wf.monetization.revenue_per_cycle).toBe('number');
      expect(wf.monetization.revenue_per_cycle).toBeGreaterThan(0);
    });

    test('monetization.payment_processor is stripe or paypal', () => {
      const valid = ['stripe', 'paypal'];
      expect(valid).toContain(wf.monetization.payment_processor);
    });

    test('monetization.affiliate_programs is an array', () => {
      expect(Array.isArray(wf.monetization.affiliate_programs)).toBe(true);
    });

    test('automation has retry_attempts and timeout_seconds', () => {
      expect(wf.automation).toHaveProperty('retry_attempts');
      expect(wf.automation).toHaveProperty('timeout_seconds');
      expect(typeof wf.automation.retry_attempts).toBe('number');
      expect(typeof wf.automation.timeout_seconds).toBe('number');
    });

    test('created_at is a valid ISO timestamp', () => {
      expect(() => new Date(wf.created_at)).not.toThrow();
      expect(new Date(wf.created_at).getFullYear()).toBeGreaterThanOrEqual(2020);
    });

    test('version follows semver pattern', () => {
      expect(wf.version).toMatch(/^\d+\.\d+\.\d+$/);
    });
  });
});

// ---------------------------------------------------------------------------
// Cross-workflow consistency checks
// ---------------------------------------------------------------------------
describe('Cross-workflow consistency', () => {
  test('all workflow IDs in registry match actual workflow file IDs', () => {
    registry.workflows.forEach((entry) => {
      const matchingFile = WORKFLOW_FILES.find((f) => f.startsWith(entry.id));
      if (matchingFile) {
        expect(workflows[matchingFile].id).toBe(entry.id);
      }
    });
  });

  test('total estimated revenue across all workflows is > $50,000', () => {
    const total = WORKFLOW_FILES.reduce((sum, file) => {
      return sum + (workflows[file].monetization.revenue_per_cycle || 0);
    }, 0);
    expect(total).toBeGreaterThan(50000);
  });

  test('all workflows have a version of 1.0.0', () => {
    WORKFLOW_FILES.forEach((file) => {
      expect(workflows[file].version).toBe('1.0.0');
    });
  });
});
