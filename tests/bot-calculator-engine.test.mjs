import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';

import { calculateBotTemplate, formatCalculatorValue } from '../website/calculator-engine.js';

const registry = JSON.parse(readFileSync(new URL('../config/generated/bot_calculators.json', import.meta.url), 'utf8'));

test('calculates known real-estate and vehicle examples', () => {
  const realEstate = calculateBotTemplate('real_estate_flip', {
    purchase_price: 180000,
    repair_costs: 35000,
    after_repair_value: 290000,
    holding_cost_monthly: 1800,
    holding_months: 4,
    selling_costs: 18000,
  });
  assert.equal(realEstate.maximum_offer, 168000);
  assert.equal(realEstate.total_cost, 240200);
  assert.equal(realEstate.net_value, 49800);

  const vehicle = calculateBotTemplate('car_flip', {
    purchase_price: 8500,
    repair_costs: 1200,
    transport_costs: 300,
    fees: 400,
    sale_price: 13500,
  });
  assert.equal(vehicle.total_cost, 10400);
  assert.equal(vehicle.net_value, 3100);
});

test('executes every registered template with finite default outputs', () => {
  const templates = new Map();
  for (const calculator of registry.calculators) templates.set(calculator.template_id, calculator);
  assert.equal(templates.size, 13);
  for (const [templateId, calculator] of templates) {
    const input = Object.fromEntries(calculator.inputs.map((item) => [item.key, item.default]));
    const output = calculateBotTemplate(templateId, input);
    assert.deepEqual(Object.keys(output), calculator.outputs.map((item) => item.key));
    assert.equal(Object.values(output).every(Number.isFinite), true, templateId);
  }
});

test('zero denominators remain finite and values format by unit', () => {
  const output = calculateBotTemplate('sales_funnel', {
    leads: 0,
    conversion_rate: 0,
    average_value: 0,
    campaign_cost: 0,
  });
  assert.equal(Object.values(output).every(Number.isFinite), true);
  assert.equal(formatCalculatorValue(25.5, 'percent'), '25.50%');
  assert.match(formatCalculatorValue(1250, 'currency'), /1,250/);
});

test('rejects unknown calculator templates instead of evaluating input', () => {
  assert.throws(() => calculateBotTemplate('user_expression', { expression: '2 + 2' }), /Unsupported calculator template/);
});
