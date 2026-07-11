import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import ActionsPage from '../ActionsPage.jsx';

const libraryPayload = {
  bot_count: 1247,
  builders: [
    { id: 'full-bot-system', name: 'Full Bot System Builder', icon: '🤖', outputs: ['profile', 'api', 'webhook', 'sandbox'], approval: 'pull_request_required' },
    { id: 'apis-builder', name: 'API Builder', icon: '🔌', outputs: ['api', 'tests'], approval: 'pull_request_required' },
  ],
  libraries: [
    { id: 'tools', name: 'Tools Library', icon: '🔧', count: 1247, description: 'Typed tools.' },
    { id: 'apis', name: 'Apis Library', icon: '🔌', count: 1247, description: 'Versioned APIs.' },
    { id: 'webhooks', name: 'Webhooks Library', icon: '🪝', count: 1247, description: 'Signed webhooks.' },
    { id: 'workflows', name: 'Workflows Library', icon: '🔁', count: 1247, description: 'Reusable workflows.' },
    { id: 'skills', name: 'Skills Library', icon: '🧠', count: 1247, description: 'Versioned skills.' },
    { id: 'sandboxes', name: 'Sandboxes Library', icon: '🧪', count: 1247, description: 'Isolated tests.' },
  ],
};

const buddyCapabilityPayload = {
  generated_at: '2026-07-11T10:04:34.383589+00:00',
  summary: {
    bot_profiles_scanned: 1247,
    registry_division_count: 45,
    workflows: 40,
    test_files: 244,
    buddy_related_files: 179,
    buddy_related_bots: 14,
    build_states: {
      built_and_test_covered: 366,
      built_contract_ready: 874,
    },
    test_states: {
      ready_for_contract_testing: 874,
      ready_for_test_run: 368,
      needs_implementation_before_testing: 5,
    },
    coding_path_states: {
      needs_placeholder_review: 1109,
      needs_direct_test_coverage: 22,
      on_full_code_path: 109,
      needs_core_implementation: 5,
      needs_existing_system_mapping: 2,
    },
    bots_with_full_coding_path: 1247,
    all_bots_have_full_coding_path: true,
    production_readiness_states: {
      not_ready_placeholder_review: 1109,
      not_ready_needs_tests: 22,
      production_ready: 101,
      not_ready_missing_implementation: 7,
      production_candidate_approval_required: 8,
    },
    fully_coded_bots: 109,
    production_ready_bots: 101,
    all_bots_fully_coded: false,
    all_bots_production_ready: false,
    placeholder_marker_bots: 1109,
  },
  buddy_bots: [
    { slug: 'buddy_core', name: 'Buddy Core', build_state: 'built_and_test_covered', test_state: 'ready_for_test_run' },
    { slug: 'buddy_orchestrator', name: 'Buddy Orchestrator', build_state: 'built_and_test_covered', test_state: 'ready_for_test_run' },
  ],
  attention: {
    needs_implementation: [
      { slug: 'payment_autocollector', name: 'Payment AutoCollector', division: 'DreamFinance' },
    ],
    needs_direct_test_coverage: [
      { slug: 'buddy-tool-builder', name: 'Buddy Tool Library Builder Bot', division: 'DreamCodeLab' },
    ],
    needs_existing_system_mapping: [
      { slug: 'ai_enablement_hub', name: 'AI Enablement Hub', division: 'DreamAIInfra' },
      { slug: 'elite_scraper', name: 'Elite Scraper', division: 'DreamSalesPro' },
    ],
  },
};

function StubActionsMonitor() {
  return <div>Actions monitor panel</div>;
}

beforeEach(() => {
  global.fetch = vi.fn((url) => {
    const payload = url === '/api/buddy-capabilities'
      ? buddyCapabilityPayload
      : libraryPayload;
    return Promise.resolve({
      ok: true,
      json: async () => payload,
    });
  });
});

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

describe('ActionsPage', () => {
  it('renders the system builder hub and live coverage', async () => {
    render(<ActionsPage ActionsMonitorComponent={StubActionsMonitor} />);

    expect(screen.getByText('🛠️ System Builder Hub')).toBeInTheDocument();
    expect(screen.getByText('Builder lanes')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: '🤝 Buddy capability tracker' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Generated libraries' })).toBeInTheDocument();
    expect(screen.getByText('Actions monitor panel')).toBeInTheDocument();
    await waitFor(() => expect(screen.getByText('Source: live')).toBeInTheDocument());
    expect(screen.getAllByText('1,247').length).toBeGreaterThan(0);
    expect(screen.getByText('7,482')).toBeInTheDocument();
  });

  it('shows Buddy capability readiness and implementation blockers', async () => {
    render(<ActionsPage ActionsMonitorComponent={StubActionsMonitor} />);

    await waitFor(() => expect(screen.getByText(/live ·/)).toBeInTheDocument());
    expect(screen.getByText('Built + test-covered')).toBeInTheDocument();
    expect(screen.getByText('Contract-ready')).toBeInTheDocument();
    expect(screen.getByText('Needs implementation before testing')).toBeInTheDocument();
    expect(screen.getByText('Path to fully coded')).toBeInTheDocument();
    expect(screen.getByText('All bots have a path')).toBeInTheDocument();
    expect(screen.getByText('Review placeholders')).toBeInTheDocument();
    expect(screen.getByText('Add direct tests')).toBeInTheDocument();
    expect(screen.getByText('Production readiness')).toBeInTheDocument();
    expect(screen.getByText('Production blockers remain')).toBeInTheDocument();
    expect(screen.getByText('Production ready')).toBeInTheDocument();
    expect(screen.getByText('Approval needed')).toBeInTheDocument();
    expect(screen.getByText('Payment AutoCollector')).toBeInTheDocument();
    expect(screen.getByText('Buddy Core')).toBeInTheDocument();
  });

  it('prepares a sandboxed pull-request build packet', () => {
    const onBuildRequest = vi.fn();
    render(
      <ActionsPage
        ActionsMonitorComponent={StubActionsMonitor}
        onBuildRequest={onBuildRequest}
      />,
    );

    fireEvent.click(screen.getByRole('button', { name: 'Prepare build packet' }));

    expect(onBuildRequest).toHaveBeenCalledWith(
      expect.objectContaining({
        builder: 'Full Bot System Builder',
        mode: 'sandbox_and_pull_request',
        approval: 'pull_request_required',
      }),
    );
    expect(screen.getByRole('status')).toHaveTextContent('sandbox-only');
  });

  it('switches builder and library lanes', async () => {
    render(<ActionsPage ActionsMonitorComponent={StubActionsMonitor} />);
    await waitFor(() => expect(screen.getByRole('tab', { name: 'API Builder' })).toBeInTheDocument());

    fireEvent.click(screen.getByRole('tab', { name: 'API Builder' }));
    expect(screen.getByRole('heading', { name: '🔌 API Builder' })).toBeInTheDocument();

    fireEvent.click(screen.getByRole('tab', { name: /Webhooks Library/ }));
    expect(screen.getByText('Signed webhooks.')).toBeInTheDocument();
  });

  it('keeps security and sandbox controls visible', () => {
    render(<ActionsPage ActionsMonitorComponent={StubActionsMonitor} />);

    expect(screen.getByText('Webhook integrity')).toBeInTheDocument();
    expect(screen.getByText('Least privilege')).toBeInTheDocument();
    expect(screen.getByText('No payments, purchases, transfers, or ad spend')).toBeInTheDocument();
    expect(screen.getByText('Pull request and human review before deployment')).toBeInTheDocument();
  });

  it('opens and closes the Buddy build console', () => {
    render(<ActionsPage ActionsMonitorComponent={StubActionsMonitor} />);

    fireEvent.click(screen.getByRole('button', { name: 'Open Buddy Build Console' }));
    expect(screen.getByRole('dialog')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Close Buddy Command Center' }));
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });
});
