/**
 * DreamCo Control Tower — Repo Manager
 *
 * Provides GitHub repository monitoring via the Octokit REST client:
 *   - Open pull requests
 *   - Open issues
 *   - Latest commit metadata
 *   - Recent workflow runs
 *
 * Usage (module):
 *   import { getRepoStatus } from "./repo-manager.js";
 *   const status = await getRepoStatus("ireanjordan24", "Dreamcobots", token);
 */

import { Octokit } from '@octokit/rest';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Fetch open pull requests for a repository.
 *
 * @param {Octokit} octokit
 * @param {string} owner
 * @param {string} repo
 * @returns {Promise<object[]>}
 */
async function getOpenPRs(octokit, owner, repo) {
  try {
    const { data } = await octokit.pulls.list({
      owner,
      repo,
      state: 'open',
      per_page: 20,
    });
    return data.map((pr) => ({
      number: pr.number,
      title: pr.title,
      author: pr.user?.login,
      branch: pr.head?.ref,
      createdAt: pr.created_at,
      updatedAt: pr.updated_at,
      url: pr.html_url,
    }));
  } catch {
    return [];
  }
}

/**
 * Fetch open issues (excludes PRs) for a repository.
 *
 * @param {Octokit} octokit
 * @param {string} owner
 * @param {string} repo
 * @returns {Promise<object[]>}
 */
async function getOpenIssues(octokit, owner, repo) {
  try {
    const { data } = await octokit.issues.listForRepo({
      owner,
      repo,
      state: 'open',
      per_page: 20,
    });
    // GitHub returns PRs in the issues list — filter them out.
    const issues = data.filter((i) => !i.pull_request);
    return issues.map((i) => ({
      number: i.number,
      title: i.title,
      author: i.user?.login,
      labels: i.labels?.map((l) => l.name) ?? [],
      createdAt: i.created_at,
      updatedAt: i.updated_at,
      url: i.html_url,
    }));
  } catch {
    return [];
  }
}

/**
 * Fetch the latest commit on the default branch.
 *
 * @param {Octokit} octokit
 * @param {string} owner
 * @param {string} repo
 * @param {string} branch
 * @returns {Promise<object|null>}
 */
async function getLatestCommit(octokit, owner, repo, branch = 'main') {
  try {
    const { data } = await octokit.repos.listCommits({
      owner,
      repo,
      sha: branch,
      per_page: 1,
    });
    if (!data.length) {
      return null;
    }
    const c = data[0];
    return {
      sha: c.sha?.slice(0, 7),
      message: c.commit?.message?.split('\n')[0],
      author: c.commit?.author?.name,
      date: c.commit?.author?.date,
      url: c.html_url,
    };
  } catch {
    return null;
  }
}

/**
 * Fetch the latest workflow runs.
 *
 * @param {Octokit} octokit
 * @param {string} owner
 * @param {string} repo
 * @returns {Promise<object[]>}
 */
async function getWorkflowRuns(octokit, owner, repo) {
  try {
    const { data } = await octokit.actions.listWorkflowRunsForRepo({
      owner,
      repo,
      per_page: 5,
    });
    return data.workflow_runs.map((r) => ({
      id: r.id,
      name: r.name,
      status: r.status,
      conclusion: r.conclusion,
      branch: r.head_branch,
      createdAt: r.created_at,
      url: r.html_url,
    }));
  } catch {
    return [];
  }
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Retrieve a full status snapshot for a GitHub repository.
 *
 * @param {string} owner - GitHub username or organisation.
 * @param {string} repo  - Repository name.
 * @param {string} token - GitHub personal access token.
 * @returns {Promise<object>}
 */
export async function getRepoStatus(owner, repo, token) {
  const octokit = new Octokit({ auth: token });

  const [openPRs, openIssues, latestCommit, workflowRuns] = await Promise.all([
    getOpenPRs(octokit, owner, repo),
    getOpenIssues(octokit, owner, repo),
    getLatestCommit(octokit, owner, repo),
    getWorkflowRuns(octokit, owner, repo),
  ]);

  const latestWorkflow = workflowRuns[0] ?? null;
  const hasConflicts = openPRs.some((pr) => pr.title?.toLowerCase().includes('conflict'));

  return {
    owner,
    repo,
    openPRs,
    openIssues,
    latestCommit,
    workflowRuns,
    summary: {
      openPRCount: openPRs.length,
      openIssueCount: openIssues.length,
      lastWorkflowStatus: latestWorkflow?.conclusion ?? 'unknown',
      hasConflicts,
    },
    timestamp: new Date().toISOString(),
  };
}

/**
 * Create a pull request in the given repository.
 *
 * @param {object} options
 * @param {string} options.owner
 * @param {string} options.repo
 * @param {string} options.token
 * @param {string} options.title
 * @param {string} options.head  - Source branch.
 * @param {string} [options.base="main"] - Target branch.
 * @param {string} [options.body=""]     - PR description.
 * @returns {Promise<object>}
 */
export async function createPullRequest({
  owner,
  repo,
  token,
  title,
  head,
  base = 'main',
  body = '',
}) {
  const octokit = new Octokit({ auth: token });
  const { data } = await octokit.pulls.create({
    owner,
    repo,
    title,
    head,
    base,
    body,
  });
  return {
    number: data.number,
    url: data.html_url,
    title: data.title,
    branch: data.head?.ref,
  };
}
