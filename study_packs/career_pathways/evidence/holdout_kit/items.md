# Blind holdout items (edu-career-pathways blind holdout v3 (rubric discrimination))

Drawn 2026-10-02T20:32:46-05:00. 18 items. Read `README.md` first. Score each candidate answer against its own rubric, 0 to 2 per criterion, in `grading_sheet.csv`.

## Q01. Computer Science (CIP 11.0701)

**Scenario prompt.** Your team owns a public REST API that about forty partner companies call. The order total is returned as a whole number of cents, and it must become a decimal string so that currencies with three decimal places can be supported. You are asked how to make the change without breaking partners. Write a short plan.

**Candidate answer.**

- **Amount field:** Change total_cents from a number to a decimal string in place, because most client libraries parse JSON values loosely and should adapt.
- **Versioning:** Keep the current version number, since the field name does not change, and describe the new string format in the changelog for this release.
- **Partner notice:** Email every partner the change, sample responses and a removal date six months out, and keep a list of partners who confirm they have switched.
- **Testing:** Replay a day of recorded partner requests against the new build and run the contract tests from the partner client libraries before release.
- **Rollout:** Turn on the new field for five percent of traffic first, watch error rates per partner, and keep a switch that can turn it off within minutes.

**Rubric (0 to 2 points each).**

1. Backward compatibility: Keeps existing clients working by adding a new field or a new API version alongside the old one, instead of changing the type or meaning of the field they already read.
2. Partner communication: Tells partners early with a clear deprecation date, migration notes and example responses, and tracks which partners have not yet moved to the new field.
3. Rollout safety: Tests the change against real client usage (contract tests or recorded traffic), releases it gradually while watching errors, and keeps a quick way to switch it off.

## Q02. Computer Science (CIP 11.0701)

**Scenario prompt.** A scheduling app sends appointment reminders an hour early or late for some users twice a year, and a few reminders go out twice. The team suspects time zone handling. You are asked to find the bug and fix it properly. Write a short plan.

**Candidate answer.**

- **Pattern:** Pull the reminders that went out early or late and confirm they cluster on the weekends when clocks change, mostly for users outside the server's own zone.
- **Bug location:** Trace the code that saves appointments and find that it stores a fixed UTC offset taken at booking time instead of the user's named time zone.
- **Fix:** Store each appointment as local time plus a zone name such as America/Chicago, and compute the UTC send time from the zone rules when each reminder is scheduled.
- **Edge hours:** Define what happens for times in the skipped spring hour and the repeated autumn hour, and keep a sent flag so a reminder can never go out twice.
- **Tests:** Ask the team to check reminders by hand on the next two clock-change weekends, and add a line to the release checklist reminding everyone about time zones.

**Rubric (0 to 2 points each).**

1. Diagnosis: Links the errors to daylight saving changes by checking which users and dates were affected, and finds where times are stored or converted without a proper time zone.
2. Correct design: Stores appointment times with the user's named time zone (not a fixed offset), converts at send time, and handles the skipped and repeated hour explicitly.
3. Testing: Adds automated tests for the daylight saving transitions in several zones, including the repeated hour, and uses a controllable clock so the tests do not depend on the real date.

## Q03. Computer Science (CIP 11.0701)

**Scenario prompt.** Customers of an online store are occasionally charged twice for one order. Logs show that the mobile app retries the payment request when the network times out, and the server processes both requests. You are asked to fix this and make sure it cannot quietly happen again. Write a short plan.

**Candidate answer.**

- **Confirm cause:** Match payment logs by order and card over the last ninety days to count duplicate charges, and confirm each pair came from an app retry after a timeout.
- **Retry key:** Have the app create a unique idempotency key for each checkout attempt and send that same key on every retry of the payment request.
- **Server check:** Store each key with the payment result in the same transaction, and when a key repeats, return the stored result instead of calling the card processor again.
- **Customers:** Refund every confirmed duplicate automatically, email the affected customers with an apology, and give the support team a list of the cases.
- **Guardrails:** Add a nightly reconciliation that flags two charges for one order, plus an automated test that cuts the network mid-payment and expects a single charge.

**Rubric (0 to 2 points each).**

1. Diagnosis: Confirms the cause from logs or traces by matching retried requests to duplicate charges, and estimates how many customers were affected and since when.
2. Idempotent design: Makes the payment endpoint safe to retry, for example with a client-generated idempotency key stored with the result, so a repeated request returns the first outcome instead of charging again.
3. Remediation and monitoring: Refunds affected customers, adds an alert or reconciliation check that would catch duplicates, and tests the retry path on purpose.

## Q04. Computer Science (CIP 11.0701)

**Scenario prompt.** A web service's memory use climbs steadily for about two days after every deploy until the platform kills the container, and users see slow pages just before each restart. You are asked to find the cause and propose a fix. Write a short plan.

**Candidate answer.**

- **Confirm pattern:** Plot resident memory across the last five deploys to confirm steady growth that resets only on restart, not spikes tied to traffic peaks.
- **Heap comparison:** Take heap snapshots one hour and twelve hours after a restart on one instance, then diff object counts to see which types keep growing.
- **Likely suspects:** Look first at the in-process response cache and the listeners added per request, since both can grow without bound; reproduce locally with a load script.
- **Fix:** Give the cache a size limit with least-recently-used eviction and remove each listener when its request finishes, rather than scheduling restarts to hide the growth.
- **Verify:** Add a one-hour soak test to the pipeline that fails if heap use grows past a set margin, and watch the memory graph for a week after release.

**Rubric (0 to 2 points each).**

1. Evidence gathering: Confirms the pattern from metrics across several deploys and compares heap snapshots or allocation profiles taken at two points in time, instead of guessing from reading the code.
2. Cause isolation: Narrows the growth to specific objects or code paths (caches with no size limit, listeners that are never removed, unbounded queues) and confirms the suspect with a small reproduction.
3. Fix and verification: Fixes the cause instead of relying on restarts, adds a limit or an automated check that would catch the problem coming back, and confirms memory stays flat after release.

## Q05. Computer Science (CIP 11.0701)

**Scenario prompt.** A security advisory says that a logging library used by your company's main web service has a flaw that lets attackers run code through crafted input. The fixed version renames some configuration options. You are asked to handle it today. Write a short plan.

**Candidate answer.**

- **Find usage:** Search the dependency lock files of every repository, including indirect dependencies, to list each service and build image that pulls in an affected version.
- **Reachability:** Check whether user-supplied text such as headers or form fields reaches the logger in each service, and rank the internet-facing services first.
- **Upgrade:** Move the main web service to the fixed release today and update its renamed configuration options, leaving the internal services for the next scheduled release cycle.
- **Confirm:** Verify the running version in each deployment after release, and search the last month of logs for the crafted input patterns described in the advisory.
- **Next time:** Turn on automatic dependency alerts for all repositories, and agree that every critical advisory is assigned an owner and handled on the same day.

**Rubric (0 to 2 points each).**

1. Exposure assessment: Finds every service and build that includes an affected version, including indirect dependencies, and checks whether the vulnerable feature is reachable from untrusted input.
2. Remediation: Upgrades every affected service to the fixed version (or applies the documented mitigation until it can), adjusts the renamed configuration, and redeploys rather than patching only the main service.
3. Verification and follow-up: Confirms the fix is live in each deployment, looks for signs of past exploitation in the logs, and improves dependency alerts so the next advisory is caught sooner.

## Q06. Mechanical Engineering (CIP 14.1901)

**Scenario prompt.** A centrifugal pump in a factory cooling loop has vibrated noticeably since its motor was replaced last month, and the new motor bearings already run hot. Production wants it fixed during the next weekend shutdown. You are asked to plan the investigation and repair. Write a short plan.

**Candidate answer.**

- **Measure:** Record vibration spectra in horizontal, vertical and axial directions at both motor and pump bearings, and log bearing temperatures under normal load.
- **Compare:** Check the readings against the pump's records from before the motor change and against the vibration limits the site uses for this class of machine.
- **Diagnose:** Since the vibration started with the new motor, treat it as a bearing defect in that motor and ask the supplier whether this model has known bearing faults.
- **Repair:** During the shutdown, correct soft foot with shims, align the shafts with a laser alignment tool, and torque the base bolts to the specified values.
- **Confirm:** Restart under load, repeat the same vibration and temperature measurements, and take weekly readings for a month to check that the bearings settle.

**Rubric (0 to 2 points each).**

1. Data collection: Measures vibration (amplitude and frequency spectrum) and bearing temperature at defined points, and compares them with readings from before the replacement or a recognized limit.
2. Diagnosis: Uses the vibration frequencies to separate likely causes such as shaft misalignment, imbalance, soft foot or looseness, and checks the motor installation, since the problem began with the replacement.
3. Repair and check: Corrects the cause found (for example precision alignment with laser or dial tools), restarts under load, and confirms vibration and temperature are back within limits.

## Q07. Computer Engineering, General (CIP 14.0901)

**Scenario prompt.** A battery-powered sensor board built around a microcontroller drains its battery in three weeks instead of the one year the design promised. The firmware and the circuit were both designed in-house. You are asked to find where the power goes and fix it. Write a short plan.

**Candidate answer.**

- **Measure:** Log the board's current with a power analyzer across a full hour of normal operation, separating the sleep, sensing and radio transmit states.
- **Firmware:** Check that the microcontroller really enters deep sleep between readings, that timers wake it only as often as needed, and that unused peripherals are switched off.
- **Hardware:** Measure the sleep current of each supply rail, looking for leakage through pull-up resistors on idle lines and a regulator whose quiescent current is too high.
- **Fix:** Correct the sleep entry in firmware, raise the pull-up resistor values, and swap in a low quiescent current regulator if the measurements show it matters.
- **Confirm:** Once the fixes are in, leave one board running on the bench and check after a few days that its battery indicator still shows a full charge.

**Rubric (0 to 2 points each).**

1. Measurement: Measures current over time with suitable equipment (a power analyzer, or a shunt with an oscilloscope) in each operating state, instead of estimating from datasheets.
2. Cause finding: Checks both firmware (sleep modes not entered, wake-ups too frequent, peripherals left on) and hardware (leakage through pull-ups, regulators with high quiescent current).
3. Fix and confirmation: Fixes the specific causes found, re-measures the full duty cycle, and recalculates expected battery life with margin for temperature and battery aging.

## Q08. Biology/Biological Sciences, General (CIP 26.0101)

**Scenario prompt.** In a teaching lab, PCR reactions meant to detect a gene in plant samples show a band of the expected size in the no-template control on three days in a row. Students are about to start a two-week project with the same assay. You are asked what to do. Write a short plan.

**Candidate answer.**

- **Read control:** A product in the no-template control means something added DNA, so mark every result from those three days as invalid and tell the students why.
- **Test sources:** Run fresh no-template controls that swap in new water, new primer dilutions and a new master mix one at a time to find the contaminated reagent.
- **Equipment:** Wipe benches and pipettes with dilute bleach followed by water, and check whether the contamination follows one particular set of pipettes.
- **Separate areas:** Set up reactions on a clean bench away from where gels are run, with its own pipettes and filter tips, and never bring amplified product back.
- **Routine:** Split reagents into small single-use aliquots for each student group, and keep a no-template control in every run for the whole project.

**Rubric (0 to 2 points each).**

1. Interpreting the control: Recognizes that a band in the no-template control means contamination, so results from those runs cannot be trusted, and does not explain the band away.
2. Finding the source: Tests the likely sources one at a time (water, primers, master mix, pipettes, bench) by swapping in fresh aliquots and running new controls.
3. Prevention: Separates pre- and post-PCR work areas and equipment, uses filter tips and small single-use aliquots, and keeps a no-template control in every run.

## Q09. Civil Engineering, General (CIP 14.0801)

**Scenario prompt.** A two-metre concrete block retaining wall beside a school car park has started to lean outward, and a crack has opened in the asphalt behind it after heavy rain. You are asked to assess the situation and recommend next steps. Write a short plan.

**Candidate answer.**

- **Make safe:** Put a warning sign on the wall and ask drivers to take care when parking, keeping the spaces open so that the car park can still be used.
- **Monitor:** Take photos of the lean and the crack today and compare them with new photos at the end of term to see whether anything has changed.
- **Drainage:** Inspect the weep holes and the drain behind the wall, which may be blocked, and check whether water is building up in the soil after rain.
- **Loads and design:** Find out whether cars now park closer to the wall than intended, and look for the original drawings, foundation details and any soil report.
- **Remedy:** Have a chartered geotechnical engineer design the repair, such as restoring drainage, moving the parking back or rebuilding the wall with proper reinforcement.

**Rubric (0 to 2 points each).**

1. Safety first: Restricts access in front of and behind the wall straight away, and arranges regular monitoring of movement until the risk is understood.
2. Investigation: Checks drainage (weep holes, blocked drains, water behind the wall), extra loads near the top of the wall, and the wall's original design and foundation.
3. Remedy: Proposes a remedy matched to the cause, such as restoring drainage, removing the extra load or rebuilding to a proper design, prepared or reviewed by a qualified engineer.

## Q10. Statistics, General (CIP 27.0501)

**Scenario prompt.** A hospital reports that the average emergency department waiting time fell from 95 to 80 minutes after a new triage system started in March. The board wants to announce that the system cut waits by 15 minutes. You are the statistician asked to review the claim. Write a short response.

**Candidate answer.**

- **Other changes:** Check whether March also brought extra staff, fewer patients or milder cases, since the winter months usually have the longest waits.
- **Same measure:** Confirm that waiting time is still measured from arrival to first assessment, and that the new triage did not change when the clock starts.
- **Analysis:** Fit an interrupted time series to two years of weekly waits, allowing for seasonal patterns, and compare with two hospitals that kept the old system.
- **Uncertainty:** Report the estimated change with a confidence interval rather than a single figure, and check how much the estimate moves when a few weeks are left out.
- **Message:** Suggest the board announce that the new triage system cut waits by 15 minutes, since a short and simple message is easier for the public to remember.

**Rubric (0 to 2 points each).**

1. Data and confounding: Checks for other changes over the same period (seasonal patterns, staffing, patient volume, case mix) and whether waiting time was measured the same way before and after.
2. Analysis: Uses a method suited to before-and-after data with trends, such as an interrupted time series or a comparison with similar hospitals, and reports uncertainty.
3. Communication: Gives the board a clear and honest statement of what the data support, with the uncertainty and caveats, and avoids overstating causation.

## Q11. Marketing/Marketing Management, General (CIP 52.1401)

**Scenario prompt.** A regional coffee chain launched a loyalty app three months ago. Sign-ups are high, but the owners cannot tell whether the app brings in extra visits or simply rewards customers who would have come anyway. You are asked how to find out. Write a short plan.

**Candidate answer.**

- **Holdout test:** For new sign-ups over the next two months, randomly keep ten percent on an app version without rewards, so their visits show what happens without the offer.
- **Store comparison:** Also compare stores that promoted the app heavily with similar stores that did not, using the same weeks of last year as a baseline.
- **Metrics:** Track visits per customer per month, average spend and the share still visiting after eight weeks, adjusting for the summer dip and other promotions.
- **Decision rule:** Look at the results when they come in and decide then whether the app seems worth keeping, based on how customers and staff feel about it.
- **Report:** Present the sign-up count and the strongest store result to the owners as the headline, since one clear message helps them back the app.

**Rubric (0 to 2 points each).**

1. Measurement design: Proposes a comparison that can show a causal effect, such as a randomized holdout group, a staggered rollout by store, or a matched comparison with behavior before launch.
2. Metrics: Defines visit frequency, spend and retention per customer, compares them with a baseline, and accounts for seasonality and other promotions.
3. Decision use: States in advance what result would justify keeping, changing or ending the app, including the cost of rewards, and reports uncertainty honestly.

## Q12. Registered Nursing/Registered Nurse (CIP 51.3801)

**Scenario prompt.** On a medical ward, a patient with type 2 diabetes is found sweaty and confused at 06:00. The bedside glucose reading is 3.1 mmol/L (56 mg/dL), and the patient can still swallow. You are the nurse assigned to the patient. Describe what you do next.

**Candidate answer.**

- **Act now:** Stay with the patient, call a colleague, and give 15 to 20 grams of glucose gel or juice by mouth while the patient can still swallow safely.
- **If worse:** If the patient becomes drowsy or cannot swallow, stop anything by mouth and follow the hypoglycemia protocol for IV glucose or IM glucagon.
- **Recheck:** Repeat the glucose reading after 15 minutes, treat again if it is still below 4 mmol/L (70 mg/dL), then give a sandwich or the breakfast tray.
- **Escalate:** Inform the doctor, and check the chart for the evening insulin or sulfonylurea dose and for whether the patient ate a full dinner.
- **Prevent:** Document the event and treatment, ask for the diabetes medicines to be reviewed, and increase overnight glucose checks for the next two nights.

**Rubric (0 to 2 points each).**

1. Immediate treatment: Gives 15 to 20 g of fast-acting carbohydrate by mouth while the patient can swallow safely, and is ready to use IV glucose or glucagon if the patient can no longer swallow.
2. Reassessment: Rechecks glucose about 15 minutes later, repeats treatment if it is still low, then gives a longer-acting carbohydrate snack or meal and keeps monitoring.
3. Escalation and prevention: Informs the prescriber, looks for the cause (insulin or sulfonylurea dose, missed meals), documents the event and adjusts the plan to prevent another episode.

## Q13. Chemistry, General (CIP 40.0501)

**Scenario prompt.** A quality-control lab measures the acid content of vinegar by titration with sodium hydroxide. Over the past month, results have crept upward by about 3 percent, although the production process has not changed. You are the analyst asked to investigate. Write a short plan.

**Candidate answer.**

- **Confirm drift:** Plot the last two months of results on a control chart, and retest a retained sample from before the drift to show the change is in the measurement.
- **Titrant:** Check the label on the sodium hydroxide bottle, which shows it was made up to the correct concentration from a certified solid when the quarter began.
- **Equipment:** Ask the analysts to judge the colour change more carefully, since the drift is probably due to different people reading the endpoint differently.
- **Correct:** Standardize fresh titrant against dried potassium hydrogen phthalate, rerun recent samples, and tell the supervisor which reported results may be affected.
- **Prevent:** Standardize the titrant every week and run a check standard with each batch, plotted on a chart with a limit that triggers an investigation.

**Rubric (0 to 2 points each).**

1. Confirming the drift: Reviews the records and a control chart to date when the drift began, and confirms it is in the measurement, for example by retesting a retained or reference sample.
2. Likely causes: Considers the titrant concentration (sodium hydroxide absorbs carbon dioxide and needs regular standardization), burette and pipette calibration, and endpoint judgment.
3. Correct and prevent: Restandardizes or replaces the titrant, recalibrates equipment, reports possibly affected results, and adds a regular check standard or standardization schedule.

## Q14. Psychology, General (CIP 42.0101)

**Scenario prompt.** A university wellbeing society is asking whether a weekly mindfulness session reduces exam stress. Its organizers plan to compare the stress scores of members who chose to attend with those of members who did not. You are asked to advise them on a better study design. Write a short recommendation.

**Candidate answer.**

- **Problem:** Students who choose to attend may already differ in stress or motivation, so comparing attenders with non-attenders cannot show what the sessions themselves do.
- **Design:** Randomly assign volunteers to start the sessions now or after exams, and measure stress in both groups before the sessions begin and again in exam week.
- **Measure:** Use a validated questionnaire such as the Perceived Stress Scale, given online at the same points for everyone, and record who stops taking part.
- **Ethics:** Get informed consent, make clear that anyone can withdraw at any time, and offer the waitlist group the full set of sessions straight after exams.
- **Claims:** Report the difference between groups with its uncertainty, and describe the result as one small study at one university rather than as proof.

**Rubric (0 to 2 points each).**

1. Design: Recommends random assignment (for example a waitlist control) to remove self-selection, with stress measured before and after the sessions in both groups.
2. Measurement: Uses a validated stress questionnaire, measures at comparable points relative to exams, and plans for dropouts and missing responses.
3. Ethics and interpretation: Covers informed consent and the right to withdraw, offers the sessions to the control group later, and avoids claiming more than the study can show.

## Q15. Computer Science (CIP 11.0701)

**Scenario prompt.** A news site caches its home page for five minutes. Each time the cached copy expires during busy hours, hundreds of requests rebuild the page at once and the database slows to a crawl for about thirty seconds. You are asked to stop these slowdowns. Write a short plan.

**Candidate answer.**

- **Timing check:** Line up the slow periods with cache expiry times in the logs, and confirm that each slowdown begins the moment the home page entry expires.
- **Root cause:** Count how many requests rebuild the page in the first second after expiry, which shows hundreds of identical database queries running at the same moment.
- **Single rebuild:** Let the first request after expiry take a short lock and rebuild the page, while every other request keeps receiving the slightly stale copy.
- **Spread expiry:** Add a small random offset to each cache lifetime, and refresh the home page in the background shortly before it expires during busy hours.
- **Validate:** Replay a busy-hour burst in a load test before and after the change, then watch database load and page latency at expiry times for a week.

**Rubric (0 to 2 points each).**

1. Problem analysis: Connects the slowdowns to many simultaneous rebuilds right after expiry (a cache stampede) using timing evidence, rather than treating them as a general need for a bigger database.
2. Mitigation: Ensures only one request rebuilds an expired entry (a lock or request coalescing) while others get the stale copy, and spreads expiry times so entries do not all expire together.
3. Validation: Reproduces the burst in a load test before and after the change, and monitors database load and page latency around expiry times in production.

## Q16. Social Work (CIP 44.0701)

**Scenario prompt.** A 14-year-old has missed about half of school days this term, and the school refers the family to you as a child and family social worker. Her mother works overnight at a warehouse, and the student looks after two younger siblings in the mornings. Describe how you would approach the case.

**Candidate answer.**

- **Meet family:** Visit at a time that suits the mother's shifts, speak with her and the student together and separately, and explain what you can keep private.
- **Listen:** Ask the student how mornings work at home and how they feel about school, and record their views in their own words.
- **Assess:** Look at the whole picture, including money, housing, the mother's health, who watches the younger children and whether they are safe, and how school is going.
- **Young carer:** Arrange a young carer's assessment, and explore breakfast clubs, nursery places or relatives who could cover the morning school run.
- **Plan:** Agree a written plan with the family and school, with named tasks such as a phased return timetable, and set a review meeting in four weeks.

**Rubric (0 to 2 points each).**

1. Engagement: Meets the student and parent respectfully, together and separately, listens to their account, and explains the social worker's role and the limits of confidentiality.
2. Assessment: Assesses the whole situation (caring load, money, housing, health, safety of the younger children, school factors) rather than treating it only as an attendance problem.
3. Plan and coordination: Agrees a practical plan with the family and school, such as a young carer's assessment and morning childcare support, with named actions and a review date.

## Q17. Accounting (CIP 52.0301)

**Scenario prompt.** During the year-end audit of a furniture retailer, you notice that sales invoiced on the last three days of the year are much higher than in any other week, and several large orders were delivered in January. You are on the audit team. Describe how you would follow this up.

**Candidate answer.**

- **Risk:** Invoices raised just before year end for goods delivered in January may record revenue too early, which would overstate this year's sales and profit.
- **Sample:** Ask the sales manager to confirm in writing that every December invoice relates to a December sale, and file that confirmation with the working papers.
- **Control transfer:** Check when the customer took control under each contract, for example on delivery, and whether any bill-and-hold arrangements meet the required conditions.
- **After year end:** Check that total sales for January look similar to last January, which would suggest that no December sales were brought forward.
- **Conclude:** Total the errors found, project them to the population, compare with materiality and ask management to adjust, escalating to the partner if they refuse.

**Rubric (0 to 2 points each).**

1. Risk recognition: Identifies a revenue cut-off risk (revenue recorded before delivery or transfer of control) and explains why it matters for the reported results of the year.
2. Audit procedures: Tests a sample of sales on both sides of year end against delivery records and contract terms, and reviews credit notes and returns issued after year end.
3. Conclusion and reporting: Quantifies any misstatement, compares it with materiality, proposes adjustments to management and escalates if management refuses to adjust.

## Q18. Elementary Education and Teaching (CIP 13.1202)

**Scenario prompt.** In your fourth-grade class, a quiz shows that about a third of the students think 1/3 is larger than 1/2 because 3 is larger than 2. The unit test is in two weeks. You are the class teacher. Describe how you would respond.

**Candidate answer.**

- **Find reasoning:** Look at the wrong answers and talk briefly with a few students to confirm that they are treating the bottom number like a whole number.
- **Check all:** Give a short task asking every student to compare pairs such as 1/4 and 1/6 and explain why, so each student's reasoning becomes visible.
- **Model:** Have students fold paper strips into halves, thirds and quarters and compare the pieces, then place the same fractions on a number line.
- **Connect:** Link the strips to symbols by asking why more equal parts make each part smaller, and have students explain the idea to a partner in their own words.
- **Monitor:** Use two-minute exit tickets every few days, regroup students who still struggle for small-group work, and share progress with families.

**Rubric (0 to 2 points each).**

1. Diagnosing the misconception: Identifies the whole-number reasoning behind the error and checks each student's thinking (short interviews or a targeted task) rather than relying on the quiz score alone.
2. Instruction: Uses concrete and visual models (fraction strips, number lines, fair-sharing tasks) to build the meaning of the denominator, then connects the models to symbols.
3. Monitoring progress: Checks understanding with short follow-up tasks during the two weeks, and adjusts grouping or support for students who still struggle.
