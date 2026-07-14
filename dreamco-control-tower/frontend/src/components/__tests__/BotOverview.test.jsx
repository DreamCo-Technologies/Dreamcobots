import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import BotOverview from '../BotOverview.jsx';

const botsPayload = [
  {
    name: 'Buddy',
    slug: 'buddy-bot',
    emoji: '🤖',
    team: 'CommandCore',
    status: 'active',
    workflowStatus: 'success',
    lastHeartbeat: new Date().toISOString(),
    pendingPRs: 0,
  },
  {
    name: 'Debug Agent',
    slug: 'debug-agent',
    emoji: '🧪',
    team: 'DreamCodeLab',
    status: 'error',
    workflowStatus: 'failure',
    lastHeartbeat: '2026-07-14T00:00:00Z',
    pendingPRs: 2,
  },
];

beforeEach(() => {
  global.fetch = vi.fn().mockResolvedValue({
    json: vi.fn().mockResolvedValue(botsPayload),
  });
});

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

describe('BotOverview', () => {
  it('shows the agent failure command deck and per-bot debug packet', async () => {
    render(<BotOverview />);

    await waitFor(() => expect(screen.getByText('Agent failure command deck')).toBeInTheDocument());
    expect(screen.getByRole('heading', { name: 'Debug every bot before client handoff' })).toBeInTheDocument();
    expect(screen.getByText('1 bot debug target(s)')).toBeInTheDocument();
    expect(screen.getByText('Debug Agent')).toBeInTheDocument();
    expect(screen.getByText('Buddy debug packet')).toBeInTheDocument();
    expect(screen.getByText(/Run the smallest bot smoke test/)).toBeInTheDocument();
  });
});
