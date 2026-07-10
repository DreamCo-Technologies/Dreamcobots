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

function StubActionsMonitor() {
  return <div>Actions monitor panel</div>;
}

beforeEach(() => {
  global.fetch = vi.fn().mockResolvedValue({
    ok: true,
    json: async () => libraryPayload,
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
    expect(screen.getByRole('heading', { name: 'Generated libraries' })).toBeInTheDocument();
    expect(screen.getByText('Actions monitor panel')).toBeInTheDocument();
    await waitFor(() => expect(screen.getByText('Source: live')).toBeInTheDocument());
    expect(screen.getByText('1,247')).toBeInTheDocument();
    expect(screen.getByText('7,482')).toBeInTheDocument();
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
