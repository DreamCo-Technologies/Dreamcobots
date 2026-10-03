# Blind holdout items (edu-career-pathways, kit v1)

Grade each candidate answer against its own rubric. Record scores in `grading_sheet.csv`. See README.md first.

## H01

**Scenario prompt**

You have been assigned a caseload of 60 people on probation. Design the case file structure and maintenance routine: the sections every file must have (court orders and conditions, risk and needs assessment, supervision plan, contacts, drug test results, treatment reports, violations, correspondence), naming and dating conventions, what must be updated after each contact and within what time, privacy and record-access rules, and a monthly self-audit checklist.

**Candidate answer (outline form)**

- Sections in a standard order, electronic or paper.
- Contact notes are added to the file when time allows.
- Treatment records handled under substance-use confidentiality rules.
- Access limited to authorized staff; release requires proper consent.
- Monthly check: conditions tracked, assessments current, deadlines met.

**Rubric (score each criterion 0, 1 or 2)**

1. Complete structure: File sections cover legal, assessment, plan, contact and compliance records.
2. Timely maintenance: Sets clear update deadlines and contact note standards.
3. Confidentiality and audit: Addresses access rules for sensitive records (such as treatment information) and includes a self-audit.

## H02

**Scenario prompt**

A city transit agency is commissioning onboard software that shows next-stop announcements and real-time arrival predictions on bus screens, using GPS and a cellular link. Write the performance requirements section of the specification: latency from GPS fix to on-screen update, prediction accuracy, behavior during cellular outages, startup time, and resource limits on the onboard computer. For each requirement give a number, how it will be measured, and why that value matters to riders.

**Candidate answer (outline form)**

- Stop announcement at least a set number of seconds before arrival at typical speeds.
- Screen update within about 2 seconds of a GPS fix; prediction error within a stated band for most trips.
- During outages, fall back to schedule-based predictions and label them; resume within a stated time after reconnect.
- Boot to usable display within a stated time after ignition.
- CPU and memory ceilings leave headroom on the onboard computer; measured during field trials on named routes.

**Rubric (score each criterion 0, 1 or 2)**

1. Quantified requirements: Each requirement has a specific value and unit rather than vague words like 'fast'.
2. Measurability: Each has a test method (logged timestamps, field trials on set routes, induced outages).
3. Rider-centered rationale: Values are justified by rider experience or safety, such as announcing a stop before the bus reaches it.

## H03

**Scenario prompt**

A first-time home buyer couple, both in their twenties with one gig-economy income and one salaried income, books a meeting to apply for a mortgage. Write your interview guide: the information and documents you need (and why for each), how you explain the steps from application to closing, the questions they are likely to ask (down payment, rate locks, credit checks) with plain-language answers, how you handle variable gig income, and the follow-up checklist you hand them.

**Candidate answer (outline form)**

- Documents: whatever the bank asks for.
- Process: application, disclosures, appraisal, underwriting, conditions, closing.
- Explain rate locks, down payment options, and credit inquiry effects.
- Checklist with dates and contact information.

**Rubric (score each criterion 0, 1 or 2)**

1. Complete information needs: Lists the documents and data needed and explains why, including how variable income is documented.
2. Clear process explanation: Explains the stages and timelines accurately in plain language.
3. Fair and helpful: Answers questions without steering or promising approval, and gives a clear follow-up checklist.

## H04

**Scenario prompt**

Invented case: a 67-year-old man is starting an oral anticoagulant after a diagnosis of atrial fibrillation; he takes an over-the-counter pain reliever several times a week, uses a fish-oil supplement and sometimes forgets evening doses of other medicines. Write the counseling script: opening and teach-back, how to take the medicine and what to do about a missed dose (per the product labeling), bleeding warning signs, interactions with his OTC products, storage, and when to call the pharmacist or doctor or seek emergency care.

**Candidate answer (outline form)**

- Open with purpose and ask what he already knows.
- Dosing and missed-dose instructions from the labeling; pill organizer or phone alarm.
- Avoid routine NSAID use; discuss fish oil with the prescriber; acetaminophen as a usual alternative within limits.
- Teach-back: he explains how and when he takes it and what he watches for.

**Rubric (score each criterion 0, 1 or 2)**

1. Accurate, individualized content: Advice reflects the drug's labeling and addresses his OTC pain reliever and supplement use.
2. Safety emphasis: Clearly explains bleeding signs and emergency situations.
3. Effective communication: Uses plain language, teach-back and adherence aids for forgetfulness.

## H05

**Scenario prompt**

The university library asks for a study-room booking app: students reserve rooms from their phones, staff can block rooms for events, no-shows are released after 15 minutes, and it must work with campus single sign-on. You have two part-time student developers for eight weeks and no budget for paid services beyond existing campus hosting. Write a one-page feasibility memo: the requirements you would confirm with users, a rough effort estimate per feature, what fits in eight weeks, what you would cut or defer, and your recommendation.

**Candidate answer (outline form)**

- Must-haves: SSO login, view availability, book and cancel, staff block-out; nice-to-have: notifications, analytics.
- Open questions: booking limits per student, accessibility needs, room check-in method for no-show release.
- The work looks manageable in the time available.
- Defer push notifications and analytics; consider an existing open-source booking system if SSO support exists.
- Recommendation with a scope, a timeline and the main risk.

**Rubric (score each criterion 0, 1 or 2)**

1. Requirements analysis: Distinguishes must-have from nice-to-have requirements and names open questions to confirm with students and staff.
2. Credible estimate: Effort estimates are broken down by feature, include testing and SSO integration risk, and add up within the stated capacity.
3. Clear recommendation: Recommends a specific scope (build, reduce, or buy/adapt existing tool) with the trade-offs stated.

## H06

**Scenario prompt**

A psychology lab ran an online survey on sleep and stress with 2,400 student responses exported from the survey platform: wide format, item names like Q14_3, some reverse-scored items, attention-check questions, and a free-text 'major' field. Write a data management plan for turning this into an analysis-ready dataset: a codebook template, the cleaning steps in order (including attention-check exclusions and reverse scoring), how you compute scale scores, how you keep the raw file untouched and record every change, and how identifying information is protected.

**Candidate answer (outline form)**

- Codebook: variable name, label, item wording reference, response scale, reverse-scored flag, missing codes.
- Order: import, rename, flag failed attention checks, recode reverse items, compute scales, recode free-text majors into categories.
- Scale scores as mean of items with a stated minimum number answered.
- Raw export kept read-only; analysis script under version control; change log.

**Rubric (score each criterion 0, 1 or 2)**

1. Reproducible pipeline: Raw data stays read-only and all transformations are scripted or logged so another person could rebuild the dataset.
2. Correct psychometric steps: Reverse-scoring, scale scoring and handling of missing items are described correctly, and exclusion rules are stated before looking at outcomes.
3. Data protection: Identifiers are separated or removed, storage and access are controlled, and the plan follows the study's consent and ethics approval.

## H07

**Scenario prompt**

You are the project specialist for moving a 60-person insurance office to a new building in eight weeks. The team: facilities coordinator, IT technician, HR generalist, an office manager, two volunteer 'floor captains', and the moving vendor. Build a responsibility assignment (RACI) matrix for the twelve main work packages, explain how you matched duties to people's skills and workloads, how you will confirm each person accepts their assignments, and how you will rebalance if someone becomes overloaded.

**Candidate answer (outline form)**

- Work packages: floor plan, IT network and phones, furniture, vendor contract, employee communication, packing, security badges, parking, mail forwarding, go-live support.
- IT technician accountable for network cutover; HR for employee communication; facilities for vendor coordination.
- Kickoff meeting where owners confirm scope and capacity.
- Weekly status check of hours and task counts per person.
- Rebalance by shifting tasks to floor captains or adding vendor support.

**Rubric (score each criterion 0, 1 or 2)**

1. Complete, clear matrix: Each work package has exactly one accountable owner, and responsible, consulted and informed roles are sensible.
2. Thoughtful assignment: Assignments reflect skills, authority and availability rather than convenience.
3. Commitment and rebalancing: Includes a step for confirming assignments and a concrete method for detecting and fixing overload.

## H08

**Scenario prompt**

Your team is releasing new firmware for a battery-powered soil-moisture sensor that reports over LoRa every 15 minutes and must last two years on two AA cells. Write a test plan for the firmware release: the test scenarios (normal reporting, weak radio signal, battery near cutoff, sensor disconnected, clock drift), which tests run on a simulator versus on real devices in a test rack, how you will measure power draw, and the release criteria.

**Candidate answer (outline form)**

- Scenario list with expected behavior, including retry and back-off on weak signal and safe shutdown at low voltage.
- Simulator for logic and timing; a rack of real sensors with programmable power supplies for power and radio tests.
- Power measured with a current analyzer across sleep and transmit cycles; projected battery life computed.
- 72-hour soak test with fault injection.
- Release only if projected battery life is at least two years and no resets occur.

**Rubric (score each criterion 0, 1 or 2)**

1. Embedded scenarios: Scenarios reflect embedded realities: power states, radio retries, brown-out, sensor faults, and long-duration behavior.
2. Test environment: Explains what can be simulated versus what needs physical devices and instruments, and why.
3. Quantified criteria: Release criteria include numbers (average current in microamps, packet success rate, no watchdog resets over a soak period).

## H09

**Scenario prompt**

You designed an online exhibit for a local history museum with scroll-triggered animations, an interactive timeline and an image zoom viewer, to be built by one front-end and one back-end developer. Write the collaboration plan: how you specify animations (timing, easing, reduced-motion alternatives), the content model the back end must support (timeline entries, image sets, captions, credits), performance budgets for images and scripts, how you pair with developers during build, and acceptance testing.

**Candidate answer (outline form)**

- Motion specs with durations and easing; prefers-reduced-motion fallback.
- Content model fields: date, title, text, images, alt text, credits.
- Budgets: page weight limit, responsive images, lazy loading.
- Weekly pairing sessions and a shared issues board.
- Acceptance: device matrix, keyboard navigation, screen reader check, performance score.

**Rubric (score each criterion 0, 1 or 2)**

1. Precise specifications: Animation and interaction specs are concrete enough to build and include accessibility alternatives.
2. Content and performance: Defines a content model and performance budgets that developers can implement.
3. Working process: Describes pairing, feedback loops and acceptance tests.

## H10

**Scenario prompt**

Graduate-path practice. Invented case: a 16-year-old athlete had a concussion five weeks ago and still reports headaches and trouble concentrating; testing by the supervising neuropsychologist found slowed processing speed but normal memory. Draft the consultation materials the neuropsychologist could use: (1) a short consult note to the treating neurologist, and (2) talking points for a meeting with the school counselor about temporary academic accommodations. Keep medical decisions with the physician and share only information the family has authorized.

**Candidate answer (outline form)**

- Neurologist note: referral question, key findings (processing speed below expectation, memory within normal limits), impressions, recommendation to re-evaluate in a set number of weeks.
- School points: extra time on tests, rest breaks, reduced screen load, gradual return to full workload.
- Defer return-to-play to the physician's graduated protocol.
- Confirm signed release of information before school contact.
- Plan follow-up contact to review whether accommodations can be reduced.

**Rubric (score each criterion 0, 1 or 2)**

1. Audience-appropriate content: The note to the neurologist is concise and technical; the school talking points are plain-language and focus on function and accommodations.
2. Accurate scope: Does not make medical decisions such as clearance to play; defers return-to-sport to the physician and follows concussion protocols.
3. Privacy: Shares only what the family has authorized and avoids unnecessary diagnostic detail with the school.

## H11

**Scenario prompt**

Invented case: a process engineer reports that the last three batches of a polyurethane coating cure tacky, although every standard QC test passed. You meet the engineer and the formulation chemist. Write the meeting summary and plan: the questions you asked, hypotheses (moisture in raw materials, catalyst level, isocyanate-to-polyol ratio, cure temperature), the existing data you reviewed, a non-standard test you propose (for example, FTIR monitoring of isocyanate peak during cure or Karl Fischer water testing of raw materials), and how results will decide the fix.

**Candidate answer (outline form)**

- Questions: raw material lots, humidity during mixing, mixing ratios, cure oven logs.
- Hypotheses ranked by likelihood with evidence for each.
- Tests: Karl Fischer on polyol lots, FTIR of residual isocyanate over time, small batches at controlled ratios.
- Next steps to be agreed after the tests come back.

**Rubric (score each criterion 0, 1 or 2)**

1. Collaborative inquiry: Captures input from both colleagues and asks questions that separate hypotheses.
2. Scientific reasoning: Hypotheses are chemically plausible and the proposed tests can confirm or rule them out.
3. Decision path: States what result points to which corrective action and how quickly it can be tested.

## H12

**Scenario prompt**

A subscription meal-kit company gives you a dataset of 50,000 customers with 120 candidate features (order history, delivery issues, discounts used, survey answers) and asks for a model to predict cancellation in the next 60 days. Write the feature-selection plan: how you split data to avoid leakage (including features recorded after cancellation), at least two selection methods compared (for example, L1-regularized logistic regression and permutation importance from a tree model), how you evaluate the final model, and how you explain the selected features to the business team.

**Candidate answer (outline form)**

- Train on older customers, validate on later months; prediction date fixed for each customer.
- Drop leaked fields such as cancellation survey answers.
- L1 logistic path versus permutation importance in gradient boosting; keep features stable across folds.
- Evaluate AUC and precision among the top 10 percent flagged.
- Explain with plain charts; note correlations are not causes; propose retention test.

**Rubric (score each criterion 0, 1 or 2)**

1. Leakage prevention: Uses time-based splits and removes features that would not be known at prediction time.
2. Sound selection methods: Compares at least two methods correctly, with cross-validation and stability checks.
3. Evaluation and explanation: Reports appropriate metrics (AUC, precision at a contact budget) and explains features without implying causation.
