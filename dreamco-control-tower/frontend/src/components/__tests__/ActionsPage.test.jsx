import { afterEach, describe, expect, it, vi } from 'vitest';
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import ActionsPage from '../ActionsPage.jsx';
import githubActionsButtonCatalog from '../../data/githubActionsButtonCatalog.js';

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
    expect(screen.getByText('GitHub Action Button Grid')).toBeInTheDocument();
    expect(screen.getByText('Agents Section')).toBeInTheDocument();
    expect(screen.getByText('Issues Section')).toBeInTheDocument();
    expect(screen.getByText('Actions monitor panel')).toBeInTheDocument();
  });

  it('loads the full 500-control actions catalog', () => {
    render(<ActionsPage ActionsMonitorComponent={StubActionsMonitor} />);

    expect(githubActionsButtonCatalog).toHaveLength(500);
    expect(screen.getByText(/500 total controls/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Action 1: Scan Bot Health' })).toBeInTheDocument();
  });

  it('renders selected action workflow without a literal template expression', () => {
    render(<ActionsPage ActionsMonitorComponent={StubActionsMonitor} />);

    fireEvent.click(screen.getByRole('button', { name: 'Action 1: Scan Bot Health' }));

    expect(screen.getByText('Dispatch wiring pending')).toBeInTheDocument();
    expect(screen.getAllByText('dreamco-debug-audit.yml').length).toBeGreaterThan(1);
    expect(screen.queryByText('`{selectedAction.workflow}`')).not.toBeInTheDocument();
  });

  it('tracks agent and issue cleanup state', () => {
    render(<ActionsPage ActionsMonitorComponent={StubActionsMonitor} />);

    expect(screen.getByText('Missing Files Scanner')).toBeInTheDocument();
    expect(screen.getByText('Sandbox No-Hallucination Audit')).toBeInTheDocument();
    expect(screen.getByText('Buddy Connectivity Tester')).toBeInTheDocument();
    expect(screen.getByText('Actions detail rendering')).toBeInTheDocument();
    expect(screen.getByText('Workflow dispatch backend')).toBeInTheDocument();
    expect(screen.getByText('2 completed')).toBeInTheDocument();
    expect(screen.getByText('3 open')).toBeInTheDocument();
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
    expect(screen.getByText('[Buddy] Command queued with evidence policy: deploy bot fleet')).toBeInTheDocument();
  });

  it('renders expanded buddy autonomous operations panels and quick commands', () => {
    const onBuddyCommandSubmit = vi.fn();
    render(
      <ActionsPage
        ActionsMonitorComponent={StubActionsMonitor}
        onBuddyCommandSubmit={onBuddyCommandSubmit}
      />,
    );
    fireEvent.click(screen.getByRole('button', { name: 'Launch Full Buddy Command Center' }));

    expect(screen.getByText('Bot Test Lab')).toBeInTheDocument();
    expect(screen.getByText('Customer Discovery')).toBeInTheDocument();
    expect(screen.getByText('Tool & Skill Finder')).toBeInTheDocument();
    expect(screen.getByText('Social Draft Studio')).toBeInTheDocument();
    expect(screen.getByText('Cash Loop Tracker')).toBeInTheDocument();
    expect(screen.getByText('Memory & Learning')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'npm run autonomous:readiness' }));
    expect(onBuddyCommandSubmit).toHaveBeenCalledWith('npm run autonomous:readiness');
  });
});
