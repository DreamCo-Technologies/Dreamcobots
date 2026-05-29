import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import AgentsPage from '../AgentsPage.jsx';

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

beforeEach(() => {
  vi.spyOn(global, 'fetch').mockImplementation((url) => {
    if (url === '/api/agents') {
      return Promise.resolve({
        json: async () => ({
          agents: [{ agent_id: 'buddy_bot', name: 'buddy-bot', category: 'AI Companion', status: 'active' }],
        }),
      });
    }
    if (url === '/api/agents/commands') {
      return Promise.resolve({
        json: async () => ({
          commands: [{ command_id: 'cmd_1', command: 'deploy', status: 'queued', selected_agent: { name: 'buddy-bot' } }],
        }),
      });
    }
    if (url === '/api/global-sources/connectivity') {
      return Promise.resolve({
        json: async () => ({
          total_modules: 2,
          connected_modules: 2,
          modules: [
            { module: 'a.py', status: 'connected' },
            { module: 'b.py', status: 'connected' },
          ],
        }),
      });
    }
    return Promise.reject(new Error('unexpected endpoint'));
  });
});

describe('AgentsPage', () => {
  it('renders agents, command queue, and connectivity checklist', async () => {
    render(<AgentsPage />);

    await waitFor(() => {
      expect(screen.getByText('🤝 Agents')).toBeInTheDocument();
      expect(screen.getByText('buddy-bot')).toBeInTheDocument();
      expect(screen.getByText('deploy')).toBeInTheDocument();
      expect(screen.getByText('2/2 modules connected')).toBeInTheDocument();
      expect(screen.getByText('a.py')).toBeInTheDocument();
    });
  });
});
