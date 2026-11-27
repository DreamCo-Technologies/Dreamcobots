# The Buddy User's Guide
## How to Use Buddy to Learn, Build, Research, and Get Work Done

A plain-language guide for people using Buddy and DreamCo.

---

## Welcome to Buddy

Buddy is designed to help you move from an idea to a clear plan, then from a plan to work you can inspect and improve. You do not need to know every technical term before you begin. Tell Buddy what you are trying to accomplish, what you already have, and what a successful result should look like.

Buddy is DreamCo's coordinating assistant. It can help route work to the appropriate division or specialist bot, explain the plan, prepare learning paths, draft and review work, and coordinate approved tools. Its job is to make complex capabilities easier to use—not to hide risk or pretend unfinished work is complete.

This is a human-facing guide, not a claim that every planned integration or feature is already live. Available features depend on what has actually been implemented, configured, tested, and authorized in your DreamCo environment.

## 1. Start with a good request

A useful request includes:
- **Goal:** What do you want done?
- **Context:** What should Buddy know?
- **Constraints:** Budget, deadline, tools, privacy, or skill level.
- **Output:** What should the finished result look like?
- **Approval boundary:** What may Buddy do automatically, and what must it ask you first?

Example:

“I want to build a simple website for my landscaping business. I am a beginner. Use free tools where possible. First give me a plan, then help me build a working first version. Do not purchase anything or publish it without asking me.”

You can start with a rough idea. Buddy should help clarify it rather than force you to write a perfect prompt.

## 2. Meet the DreamCo divisions

DreamCo has specialist divisions for different areas of work. Buddy should:
1. Understand the request.
2. Identify the capabilities required.
3. Route it to the correct division or specialist.
4. Explain why that route was chosen.
5. Coordinate work where several divisions are needed.
6. Check the result and report unresolved gaps.

A division is a specialist team, not a guarantee of expertise. Buddy should use the division registry as the source of truth, show which specialist handled the task, and distinguish tested capabilities from planned ones.

For a multi-part request, Buddy may create a work plan with owners, dependencies, acceptance criteria, and review points. You should be able to see what is waiting, running, completed, failed, or blocked.

## 3. Use Buddy as your teacher

You can ask Buddy to teach you any subject at your level.

Try:
- “Teach me HTML as if I have never coded.”
- “Give me one exercise at a time.”
- “Let me try before you show the answer.”
- “Explain why my code failed.”
- “Create a seven-day beginner learning plan.”
- “Test me on what I learned yesterday.”
- “Show me what I need to practice before moving on.”

A good Buddy lesson should explain, demonstrate, guide, let you practice independently, and check what you can do. Ask for a project when you are ready to combine skills.

Buddy should track progress honestly. Reading or watching a lesson is not the same as completing practice. A capability should be marked mastered only after meaningful assessment, an unseen challenge, and regression checks.

## 4. Use the Bootcamp

The Buddy Bootcamp is the structured learning program behind Buddy's teaching workflow. It should help you:
- choose a subject and starting level
- identify prerequisites
- follow a sequence of short lessons
- practice in a safe sandbox
- build original projects
- take quizzes and practical assessments
- review weak areas
- record evidence and continue from where you stopped

If a lesson is too difficult, ask Buddy to explain the prerequisite in simpler language. If it is too easy, ask for a harder project. You should be able to learn at your own pace.

## 5. Ask Buddy to build something

Describe the problem before prescribing a technology.

Example:

“I need a simple customer appointment tracker. Customers should be able to request a time, and I need a private dashboard to manage requests. Start with a safe prototype using sample data. Explain the technology choices and show me how to test it.”

Buddy should return:
1. a short understanding of the goal
2. a proposed solution and architecture
3. assumptions and questions that affect correctness
4. a step-by-step build plan
5. a test and acceptance checklist
6. cost, privacy, security, and deployment considerations

For substantial work, ask Buddy to work in a feature branch and submit a pull request. Review the changes and checks before merging or deploying.

## 6. Research and use learning resources

Ask Buddy to find official documentation, courses, videos, books, research, and examples. Request the original links and why each resource is relevant.

Example:

“Find beginner-friendly resources for learning SQL. Organize them into lessons for the data division. Give me original practice exercises and a small project.”

Buddy should distinguish:
- discovered resources
- resources reviewed for relevance
- resources with verified rights/terms
- resources actually studied
- exercises completed
- skills independently assessed

A catalog entry is not proof of study. Do not ask Buddy to copy copyrighted course material or download media without permission. Ask for an original explanation and link to the source instead.

## 7. Understand the Actions and progress pages

When available in your DreamCo deployment, the Actions page should be the operational view of Buddy's work. It should show:
- the task and its owner
- the selected division and specialist
- current status and next action
- training, sandbox, and benchmark activity
- logs and evidence
- failures and blockers
- estimated cost or resource use where available
- approval requests and stop controls

A button should perform a real, documented action. If it is only a prototype or display, it must be labeled accordingly.

Use pause or stop controls when a task behaves unexpectedly. Ask Buddy to explain what will be stopped and whether any external process or deployment is affected.

## 8. Connect tools, apps, and accounts safely

Some tasks require external services such as GitHub, databases, cloud providers, model APIs, or business applications.

A good connection process should:
1. explain what the service does
2. explain why Buddy needs it
3. show the permissions requested
4. explain likely costs and free alternatives
5. let you authorize the connection yourself
6. store credentials in an approved secrets manager
7. test the connection without exposing the secret
8. show status, scope, and how to disconnect or rotate credentials

Never paste a private API key into a public issue, source file, chat shared with others, or log. Do not grant broad administrator access when a narrower permission is sufficient. Buddy should never claim a service is connected merely because a configuration entry exists.

## 9. Use GitHub with Buddy

GitHub stores code and tracks changes. Buddy can help inspect a repository, understand its structure, propose fixes, prepare branches, and review pull requests when the required permissions and tools are available.

A safe workflow is:
1. inspect the current branch and working tree
2. read the relevant code, tests, and project instructions
3. create a focused feature branch
4. make a small, reviewable change
5. run the relevant tests
6. run required repository checks
7. summarize the diff and evidence
8. open a pull request
9. request independent review
10. merge only after required approvals and checks pass

### What a good PR review looks like

Ask Buddy:

“Review this pull request like a senior engineer. Find correctness, security, privacy, performance, maintainability, test, documentation, and deployment risks. Separate blocking issues from suggestions. Cite the changed file and explain how to reproduce each issue.”

A useful review comment describes the problem, why it matters, and a concrete correction. Reviewers should verify that tests actually cover the changed behavior. Do not approve a PR just because its description sounds convincing.

### What a good CI/CD review looks like

CI runs automated checks when code changes. CD manages delivery and deployment. Ask Buddy to inspect:
- required workflows and branch protection
- dependency installation and lockfiles
- lint, type, and build checks
- unit, integration, and end-to-end tests
- security and secret scanning
- artifact generation and freshness
- workflow permissions and third-party actions
- deployment approvals, smoke tests, and rollback
- failure logs and flaky tests

When a check fails, ask for the first causal error, root cause, proposed repair, regression test, and rerun evidence. Never make a pipeline green by deleting meaningful tests, weakening assertions, hiding errors, or marking skipped checks as passed.

A green badge means the configured checks passed for that run. It does not prove every product feature or live integration works.

## 10. Review Buddy's answers and work

Buddy can make mistakes. Before relying on important output:
- ask for assumptions and sources
- verify calculations and external facts
- run the supplied code and tests
- inspect permissions and security implications
- ask what is unknown or unverified
- have a qualified person review high-impact decisions

For legal, medical, financial, safety, or other high-impact matters, use appropriate qualified professionals and authoritative sources. Buddy can help you prepare questions and understand information, but should not replace professional judgment.

## 11. Understand statuses

Use these meanings consistently:

- **Planned:** described but not implemented.
- **In progress:** work has started.
- **Implemented:** code or configuration exists.
- **Sandbox tested:** a controlled test passed.
- **Verified:** required evidence and review are complete.
- **Production ready:** the real deployment and operational requirements have been checked.
- **Blocked:** a specific dependency, permission, decision, or defect prevents progress.
- **Failed:** a required check did not pass.
- **Not tested:** no valid test evidence is available.

If Buddy cannot verify something, it should say so. Ask it to show the evidence rather than simply repeat a status label.

## 12. Control cost and risk

Before a task uses paid APIs, cloud compute, external messaging, publishing, purchases, or irreversible changes, ask Buddy for:
- the action it intends to take
- expected cost or cost range, if knowable
- data that will be sent
- permissions required
- alternatives
- rollback or cancellation options

Set limits where the platform supports them. Prefer local or free tools for experiments. Use sample data in early prototypes. Require confirmation for consequential external actions.

## 13. Make Buddy better with feedback

After a task, tell Buddy:
- what was useful
- what was wrong or missing
- what should be clearer next time
- whether the result met the acceptance criteria

Good feedback should become a traceable improvement: a corrected lesson, test, routing rule, or documentation change. It should not silently rewrite safety rules or turn one user's preference into a universal fact.

## 14. A first-day walkthrough

1. Choose one small goal.
2. Ask Buddy to explain the plan in plain language.
3. Confirm the tools and permissions.
4. Start with a prototype or sample data.
5. Complete one learning exercise.
6. Ask Buddy to review the result.
7. Run the relevant tests.
8. Save the work and its evidence.
9. Decide the next step.

A first success should be small, real, and understandable.

## 15. Quick prompt library

**Learn:** “Teach me [topic] from beginner level with examples and practice.”

**Practice:** “Give me a challenge. Wait for my attempt before showing a solution.”

**Debug:** “Help me isolate the root cause. Do not guess; ask for the missing logs or files.”

**Plan:** “Break this goal into milestones, dependencies, risks, and acceptance criteria.”

**Build:** “Create a small working prototype with tests and clear setup instructions.”

**Review:** “Review this change for correctness, security, accessibility, maintainability, and test coverage.”

**CI/CD:** “Inspect the failing workflow and identify the first causal error. Propose a fix and regression test.”

**Research:** “Find authoritative resources, link to the originals, explain relevance, and identify licensing limits.”

**Progress:** “Show what is completed, what is verified, what is blocked, and the evidence for each status.”

**Cost:** “Estimate the cost and explain free or lower-cost alternatives before taking action.”

---

## Closing

Buddy should make technology and learning easier to approach. You remain in control of your goals, data, accounts, and approvals. Ask questions, inspect the work, practice the skills, and expect evidence.

The best way to use Buddy is as a partner in learning and building—not as a substitute for understanding what you are creating.
