import { afterEach, describe, expect, it, vi } from 'vitest';
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import ActionsPage from '../ActionsPage.jsx';

function StubActionsMonitor() {
  return <div>Actions monitor panel</div>;
}

afterEach(() => {
  cleanup();
});

describe('ActionsPage', () => {
  it('renders actions page and monitor panel', () => {
    render(<ActionsPage ActionsMonitorComponent={StubActionsMonitor} />);

    expect(screen.getByText('⚡ Actions')).toBeInTheDocument();
    expect(screen.getByText('Actions monitor panel')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Open Agents Coordination' })).toBeInTheDocument();
  });

  it('opens and closes buddy command center modal', () => {
    render(<ActionsPage ActionsMonitorComponent={StubActionsMonitor} />);

    fireEvent.click(screen.getByRole('button', { name: 'Launch Full Buddy Command Center' }));
    expect(screen.getByRole('dialog')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Close Buddy Command Center' }));
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });

  it('submits command when Enter is pressed in input', () => {
    const onBuddyCommandSubmit = vi.fn();

    render(
      <ActionsPage
        ActionsMonitorComponent={StubActionsMonitor}
        onBuddyCommandSubmit={onBuddyCommandSubmit}
      />,
    );

    fireEvent.click(screen.getByRole('button', { name: 'Launch Full Buddy Command Center' }));

    const input = screen.getByRole('textbox', { name: 'Buddy command input' });
    fireEvent.change(input, { target: { value: 'deploy bot fleet' } });
    fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' });

    expect(onBuddyCommandSubmit).toHaveBeenCalledWith('deploy bot fleet');
    expect(screen.getByRole('log', { name: 'Buddy terminal output' })).toBeInTheDocument();
    expect(screen.getByText('$ deploy bot fleet')).toBeInTheDocument();
    expect(screen.getByText('[Buddy] Command queued: deploy bot fleet')).toBeInTheDocument();
  });

  it('renders core buddy command center panels', () => {
    render(<ActionsPage ActionsMonitorComponent={StubActionsMonitor} />);
    fireEvent.click(screen.getByRole('button', { name: 'Launch Full Buddy Command Center' }));

    expect(screen.getByText('Swarm Status')).toBeInTheDocument();
    expect(screen.getByText('HotStuff Consensus')).toBeInTheDocument();
    expect(screen.getByText('Economic Feedback Loops')).toBeInTheDocument();
  });

  it('renders latest dispatch summary with duplicate notice', () => {
    render(
      <ActionsPage
        ActionsMonitorComponent={StubActionsMonitor}
        lastDispatch={{
          duplicate: true,
          duplicate_of: 'cmd_123',
          command: { command: 'deploy bot fleet' },
          selected_agent: { name: 'buddy-bot' },
        }}
      />,
    );

    expect(screen.getByText('Latest command arbitration')).toBeInTheDocument();
    expect(screen.getByText('deploy bot fleet')).toBeInTheDocument();
    expect(screen.getByText('Duplicate detected — linked to cmd_123')).toBeInTheDocument();
  });

  it('navigates to agents page callback', () => {
    const onOpenAgentsPage = vi.fn();
    render(
      <ActionsPage
        ActionsMonitorComponent={StubActionsMonitor}
        onOpenAgentsPage={onOpenAgentsPage}
      />,
    );
    fireEvent.click(screen.getByRole('button', { name: 'Open Agents Coordination' }));
    expect(onOpenAgentsPage).toHaveBeenCalledTimes(1);
  });
});
