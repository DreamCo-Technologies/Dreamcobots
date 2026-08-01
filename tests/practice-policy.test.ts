import assert from "node:assert/strict";
import test from "node:test";

import { createPracticeSessionPlan } from "../server/practice-policy";

test("job interview practice routes real specialists without candidate impersonation", () => {
  const plan = createPracticeSessionPlan({
    mode: "job_interview",
    targetRole: "Junior software developer",
    context: "Prepare for a private mock interview using the owner's real experience.",
    goals: ["Practice STAR answers", "Prepare questions for the employer"],
    difficulty: "realistic",
    rounds: 6,
    answerMode: "text_and_voice",
    useOwnerVoice: true,
    adultVoiceRightsConfirmed: true,
    candidatePracticeOnly: true,
  });
  assert.deepEqual(plan.specialistSlugs, ["resume-builder-bot", "job-application-bot", "buddy-bot"]);
  assert.equal(plan.controls.candidateImpersonationAllowed, false);
  assert.equal(plan.controls.automatedEmploymentDecisionAllowed, false);
  assert.equal(plan.controls.rawVoiceStoredInPlan, false);
  assert.equal(plan.controls.liveExternalActionTaken, false);
});

test("job practice rejects real interview impersonation", () => {
  assert.throws(() => createPracticeSessionPlan({
    mode: "job_interview",
    targetRole: "Account manager",
    context: "Answer the real employer's live interview in place of the candidate.",
    goals: ["Get through the interview"],
    difficulty: "challenging",
    rounds: 4,
    answerMode: "voice",
    useOwnerVoice: true,
    adultVoiceRightsConfirmed: true,
    candidatePracticeOnly: false,
  }), /cannot impersonate/);
});

test("voice role-play requires adult owner rights", () => {
  assert.throws(() => createPracticeSessionPlan({
    mode: "presentation",
    targetRole: "Founder presenter",
    context: "Practice a private product presentation and skeptical questions.",
    goals: ["Improve the opening"],
    difficulty: "supportive",
    rounds: 3,
    answerMode: "voice",
    useOwnerVoice: true,
    adultVoiceRightsConfirmed: false,
    candidatePracticeOnly: true,
  }), /rights confirmation/);
});

test("sales role-play remains a private preparation plan", () => {
  const plan = createPracticeSessionPlan({
    mode: "sales_call",
    targetRole: "Service consultant",
    context: "Practice a truthful discovery call with a fictional customer.",
    goals: ["Ask better questions", "Handle a price objection"],
    difficulty: "challenging",
    rounds: 5,
    answerMode: "text",
    useOwnerVoice: false,
    adultVoiceRightsConfirmed: false,
    candidatePracticeOnly: true,
  });
  assert.equal(plan.status, "private_sandbox_ready");
  assert.equal(plan.controls.exactApprovalBeforeExternalAction, true);
  assert.equal(plan.controls.liveExternalActionTaken, false);
});
