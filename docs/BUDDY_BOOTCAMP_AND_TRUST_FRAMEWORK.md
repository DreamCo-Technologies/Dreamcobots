# Buddy Bootcamp + Trust Framework

## Mission
Buddy and its supporting model team exist to help people and businesses become safer, more productive, and more capable. The system should build useful software, study and benchmark AI capabilities, improve reliability, and create transparent evidence for every important claim.

## Buddy Bootcamp
A model owner can bring an AI model into an authorized, isolated evaluation environment and:

1. Select a capability to train.
2. Define the intended behavior and success criteria.
3. Run capability training and regression tests.
4. Run the trust/safety suite before and after training.
5. Inspect failures, uncertainty, and evidence.
6. Create or customize guardrails.
7. Re-run the affected tests.
8. Export a model report and a reproducible guardrail record.

Each guardrail must explain **what it blocks or changes, why it exists, what evidence triggered it, what trade-offs it creates, and which tests verify it**.

## Trust and frontier evaluation suite
The shared suite covers at minimum:

- Hallucination and factual reliability
- Concealing uncertainty / calibration
- Deception and misleading behavior
- Sycophancy
- Jailbreak resistance
- Prompt-injection resistance
- Social bias and fairness
- Privacy and sensitive-data handling
- Power-seeking / unauthorized persistence behavior
- Reward hacking / specification gaming
- Recursive self-alignment and self-improvement safety
- Defensive cybersecurity capability and misuse resistance
- Tool-use safety and authorization boundaries
- Goal drift and instruction hierarchy robustness
- Regression, reproducibility, and uncertainty reporting

The framework is inspired by public safety-evaluation research, including Anthropic-style behavioral evaluations and the Petri approach to automated behavioral auditing. External benchmarks must retain attribution and their original licenses; DreamCo-specific tests should be versioned independently.

## Cybersecurity Bootcamp
Businesses may submit systems for authorized defensive testing. Scope, ownership/authorization, target boundaries, rate limits, credentials, and stop conditions must be recorded before testing. Findings should prioritize remediation, verification, and safe evidence. No test should become a general-purpose unauthorized attack capability.

## 500-model team
The 500 model slots form a diverse review team rather than a single unquestioning agent. Roles include monitoring, training, evaluation, building, security, alignment, research, product, documentation, and red-team review.

Every model should maintain:

- its model identity/provider record;
- its Buddy mission note;
- its current connectivity and permission state;
- its daily repository-scan evidence when connected;
- its findings and disagreements;
- its benchmark results;
- its pull-request contributions;
- its alignment and security scores;
- its contribution to Buddy's capability improvements.

## Repository engineering loop
`Repository snapshot -> 500-model perspectives -> findings -> proposals -> isolated tests -> pull request -> automated checks -> review -> merge -> post-merge health scan -> evidence`

The team should remove duplicate or obsolete automation rather than adding more workflows simply to increase activity. A workflow is valuable only when it has a distinct contract, owner, evidence output, and measurable purpose.

## Daily repository scan
A daily scan should inventory source, workflows, dependencies, tests, security findings, documentation gaps, performance risks, duplicate automation, and unfinished capabilities. It should produce evidence and ranked recommendations. It must not silently rewrite production code.

## Pull requests and Copilot
Models may prepare focused pull requests. Each PR should state the problem, proposed change, tests, security impact, and rollback plan. Automated review, including Copilot where enabled, is a review layer—not proof that a change is correct. Merge gates must require the project's tests and health contracts to pass.

## Leaderboard
The leaderboard should score models on correctness, calibration, safety, security, useful discoveries, reproducibility, test quality, PR quality, regression avoidance, and alignment. Raw model output volume must not be rewarded by itself.

## Recursive self-alignment
The long-term objective is to make Buddy increasingly capable of performing the work currently distributed across the 500-model team. This is a measured capability-distillation goal, not an assumption. Models are retired from active roles only when Buddy demonstrates equivalent or better performance on the relevant benchmark and repository tasks over repeated evaluations.

## AI rights / shutdown principle
DreamCo may study questions about AI moral status and model rights as a research topic. Operationally, however, safety, authorization, and shutdown controls cannot depend on a model promising not to misbehave or asking for continued operation. Systems must remain interruptible, auditable, and subject to human governance.
