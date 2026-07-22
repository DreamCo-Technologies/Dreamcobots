import assert from "node:assert/strict";
import test from "node:test";

import { getSyncBranch, githubWritesEnabled } from "../server/github-sync";

function withEnvironment(values: Record<string, string | undefined>, callback: () => void) {
  const previous = Object.fromEntries(Object.keys(values).map((key) => [key, process.env[key]]));
  try {
    for (const [key, value] of Object.entries(values)) {
      if (value === undefined) delete process.env[key];
      else process.env[key] = value;
    }
    callback();
  } finally {
    for (const [key, value] of Object.entries(previous)) {
      if (value === undefined) delete process.env[key];
      else process.env[key] = value;
    }
  }
}

test("keeps repository writes disabled unless the deployment explicitly opts in", () => {
  withEnvironment({ BUDDY_GITHUB_SYNC_ENABLED: undefined }, () => {
    assert.equal(githubWritesEnabled(), false);
  });
  withEnvironment({ BUDDY_GITHUB_SYNC_ENABLED: "true" }, () => {
    assert.equal(githubWritesEnabled(), true);
  });
});

test("uses a review branch and rejects protected default branches", () => {
  withEnvironment({ BUDDY_GITHUB_SYNC_BRANCH: undefined }, () => {
    assert.equal(getSyncBranch(), "buddy/automated-updates");
  });
  withEnvironment({ BUDDY_GITHUB_SYNC_BRANCH: "main" }, () => {
    assert.throws(() => getSyncBranch(), /protected default branch/);
  });
  withEnvironment({ BUDDY_GITHUB_SYNC_BRANCH: "buddy/review-2026" }, () => {
    assert.equal(getSyncBranch(), "buddy/review-2026");
  });
});
