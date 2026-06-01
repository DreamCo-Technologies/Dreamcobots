import { loadEventContract, validateEventEnvelope } from '../backend/event_contract.js';

describe('shared event envelope contract (node)', () => {
  test('loads shared contract schema', () => {
    const contract = loadEventContract();
    expect(contract.schema).toBe('dreamco_event_envelope.v1');
    expect(contract.required_fields).toContain('event_type');
  });

  test('accepts valid envelope', () => {
    const result = validateEventEnvelope({
      event_type: 'bot.started',
      bot_id: 'dreambuddy_core',
      intent: 'add_todo',
      timestamp: '2026-06-01T00:00:00Z',
      status: 'running',
      correlation_id: 'corr-123',
    });
    expect(result).toBe(true);
  });

  test('rejects missing required fields', () => {
    expect(() =>
      validateEventEnvelope({
        event_type: 'bot.started',
        bot_id: 'dreambuddy_core',
      }),
    ).toThrow('missing required field: intent');
  });
});
