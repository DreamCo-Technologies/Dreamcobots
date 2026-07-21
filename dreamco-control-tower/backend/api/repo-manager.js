/**
 * DreamCo Control Tower — Repo Manager
 *
 * Monitors GitHub repositories for each registered bot:
 *   - Open and merged pull requests
 *   - Recent commits
 *   - Workflow run results
 *   - Issue counts
 */

import { Octokit } from '@octokit/rest';
import { readBots, writeBots } from './bot-manager.js';

const octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });
const OWNER = process.env.GITHUB_OWNER || 'ireanjordan24';

// ---------------------------------------------------------------------------
// Pull request helpers
// ---------------------------------------------------------------------------

/**
 * List open pull requests for a given repo.
 */
export async function getOpenPRs(repoName) {
  const { data } = await octokit.pulls.list({
    owner: OWNER,
    repo: repoName,
    state: 'open',
    per_page: 10,
  });
  return data.map((pr) => ({
    number: pr.number,
    title: pr.title,
    url: pr.html_url,
    createdAt: pr.created_at,
  }));
}

/**
 * List recently merged pull requests for a given repo.
 */
export async function getMergedPRs(repoName, limit = 5) {
  const { data } = await octokit.pulls.list({
    owner: OWNER,
    repo: repoName,
    state: 'closed',
    per_page: limit,
    sort: 'updated',
    direction: 'desc',
  });
  return data
    .filter((pr) => pr.merged_at)
    .map((pr) => ({
      number: pr.number,
      title: pr.title,
      url: pr.html_url,
      mergedAt: pr.merged_at,
    }));
}

// ---------------------------------------------------------------------------
// Commit helpers
// ---------------------------------------------------------------------------

/**
 * Return the most recent commits on the default branch.
 */
export async function getRecentCommits(repoName, limit = 5) {
  const { data } = await octokit.repos.listCommits({
    owner: OWNER,
    repo: repoName,
    per_page: limit,
  });
  return data.map((c) => ({
    sha: c.sha.slice(0, 7),
    message: c.commit.message.split('\n')[0],
    author: c.commit.author.name,
    date: c.commit.author.date,
    url: c.html_url,
  }));
}

// ---------------------------------------------------------------------------
// Workflow helpers
// ---------------------------------------------------------------------------

/**
 * Return the latest workflow run result for a repo.
 */
export async function getLatestWorkflowRun(repoName) {
  const { data } = await octokit.actions.listWorkflowRunsForRepo({
    owner: OWNER,
    repo: repoName,
    per_page: 1,
  });
  const run = data.workflow_runs[0];
  if (!run) {
    return null;
  }
  return {
    id: run.id,
    name: run.name,
    status: run.status,
    conclusion: run.conclusion,
    url: run.html_url,
    runAt: run.run_started_at,
  };
}

// ---------------------------------------------------------------------------
// Full repo snapshot
// ---------------------------------------------------------------------------

/**
 * Gather a full activity snapshot for a bot's repository and persist
 * the workflow status back into bots.json.
 */
export async function getRepoSnapshot(bot) {
  const [openPRs, mergedPRs, commits, latestRun] = await Promise.all([
    getOpenPRs(bot.repoName),
    getMergedPRs(bot.repoName),
    getRecentCommits(bot.repoName),
    getLatestWorkflowRun(bot.repoName),
  ]);

  // Update workflowStatus in registry
  const bots = readBots();
  const record = bots.find((b) => b.name === bot.name);
  if (record) {
    record.workflowStatus = latestRun?.conclusion ?? 'unknown';
    writeBots(bots);
  }

  return {
    bot: bot.name,
    repo: bot.repoName,
    openPRs,
    mergedPRs,
    commits,
    latestWorkflowRun: latestRun,
  };
}
