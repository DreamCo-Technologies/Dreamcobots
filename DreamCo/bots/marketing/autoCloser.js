'use strict';

/**
 * DreamCo Auto Closer Bot
 *
 * AI negotiation engine with closing scripts and a 7-stage state machine.
 * Handles objections, advances deals through the pipeline, and tracks
 * closing outcomes.
 *
 * BOT → ACTION → RESULT → REVENUE → VALIDATION → SCALE
 */

/**
 * Pre-written closing scripts keyed by stage.
 */
const WIN_PROBABILITY = 0.65; // simulation only — not used for security or cryptography
const CLOSING_SCRIPTS = {
  initial_contact:
    'Hi [NAME], I came across [COMPANY] and thought there could be a great fit between what we offer and what you need. Do you have 10 minutes this week?',
  discovery:
    "Tell me more about the biggest challenge you're facing with [PAIN_POINT]. What does that cost you in time or revenue each month?",
  proposal:
    "Based on what you've shared, here's exactly how we'd solve [PAIN_POINT] for [COMPANY]. Our solution typically delivers results within 90 days.",
  objection_handling:
    'I completely understand. Many of our clients had the same concern. What happened when they moved forward is [RESULT]. Does that address your worry?',
  closing:
    "It sounds like we're aligned. The next step is simply getting the agreement signed so we can kick off. Shall we do that now?",
  follow_up:
    "I wanted to follow up on our last conversation. Have you had a chance to discuss this internally? I'm here if you have any questions.",
  booked:
    "Fantastic! You're all set. I'll send the onboarding details shortly. Looking forward to delivering results for [COMPANY]!",
};

const STAGES = [
  'initial_contact',
  'discovery',
  'proposal',
  'objection_handling',
  'closing',
  'follow_up',
  'booked',
];

const COMMON_OBJECTIONS = [
  'too expensive',
  'not the right time',
  'need to think about it',
  'already have a solution',
  'need to talk to my team',
];

const OBJECTION_RESPONSES = {
  'too expensive':
    'Our pricing is an investment that typically pays back 3–5x within 90 days. Would an ROI breakdown help make the decision clearer?',
  'not the right time':
    "I understand timing matters. Can I ask — what would need to change for the timing to be right? Let's map that out.",
  'need to think about it':
    'Of course! What specific questions can I answer right now to make that easier for you?',
  'already have a solution':
    "That's great to hear. Many clients who already had a solution found we could complement or improve their results significantly. Would you be open to a quick comparison?",
  'need to talk to my team':
    'Absolutely. I can put together a one-pager for your team and even join a quick call. Would that be helpful?',
};

/**
 * Start a new negotiation session for a lead.
 * @param {Object} lead - Lead object (needs at least id, company, niche)
 * @returns {Object} Negotiation session object
 */
function startNegotiation(lead = {}) {
  const stage = STAGES[0];
  return {
    session_id: `NEG-${Date.now()}-${Math.floor(Math.random() * 9999)}`,
    lead_id: lead.id || `LEAD-${Date.now()}`,
    company: lead.company || 'Unknown Co.',
    stage,
    script: CLOSING_SCRIPTS[stage],
    history: [{ stage, timestamp: new Date().toISOString() }],
    status: 'active',
    created_at: new Date().toISOString(),
  };
}

/**
 * Handle an objection and return the appropriate response script.
 * @param {string} objection - Objection phrase
 * @returns {{ objection: string, response: string }}
 */
function handleObjection(objection = '') {
  const normalized = objection.toLowerCase();
  const matched = COMMON_OBJECTIONS.find((o) => normalized.includes(o)) || COMMON_OBJECTIONS[0];
  return {
    objection: matched,
    response: OBJECTION_RESPONSES[matched],
  };
}

/**
 * Advance a negotiation session to the next stage and determine a deal outcome.
 * @param {Object} session - Active negotiation session
 * @returns {{ session: Object, deal: Object }} Updated session and deal outcome
 */
function closeDeal(session = {}) {
  const currentIndex = STAGES.indexOf(session.stage || STAGES[0]);
  const nextIndex = Math.min(currentIndex + 1, STAGES.length - 1);
  const nextStage = STAGES[nextIndex];
  const won = Math.random() > 1 - WIN_PROBABILITY; // simulation only — not used for security or cryptography
  const dealValue = Math.floor(Math.random() * 5000) + 1000;

  const updatedSession = {
    ...session,
    stage: nextStage,
    status: nextStage === 'booked' ? (won ? 'won' : 'lost') : 'active',
    script: CLOSING_SCRIPTS[nextStage],
    history: [
      ...(session.history || []),
      { stage: nextStage, timestamp: new Date().toISOString() },
    ],
    closed_at: nextStage === 'booked' ? new Date().toISOString() : null,
  };

  return {
    session: updatedSession,
    deal: {
      won,
      value: won ? dealValue : 0,
      stage: nextStage,
      message: won
        ? `🎉 Deal closed with ${session.company || 'client'} — $${dealValue}`
        : `Deal lost at ${nextStage} stage`,
    },
  };
}

/**
 * Main bot entry point — runs an auto-closing cycle.
 * @param {Object} [options]
 * @param {number} [options.prospects] - Number of prospects to run through the closer
 * @returns {Object} Standardised bot output
 */
function run(options = {}) {
  const prospectCount = options.prospects || Math.floor(Math.random() * 10) + 5;
  const sessions = [];
  let totalDealsWon = 0;
  let totalDealValue = 0;

  for (let i = 0; i < prospectCount; i++) {
    const lead = { id: `LEAD-${i}`, company: `Prospect ${i + 1} LLC`, niche: 'general' };
    let session = startNegotiation(lead);
    const { session: closed, deal } = closeDeal(session);
    sessions.push(closed);
    if (deal.won) {
      totalDealsWon++;
      totalDealValue += deal.value;
    }
  }

  const revenue = Math.floor(Math.random() * (6000 - 2500 + 1)) + 2500;
  const leadsGenerated = Math.floor(Math.random() * (60 - 30 + 1)) + 30;
  const conversionRate =
    prospectCount > 0 ? parseFloat((totalDealsWon / prospectCount).toFixed(2)) : 0;

  return {
    bot: 'autoCloser',
    revenue,
    leads_generated: leadsGenerated,
    conversion_rate: conversionRate,
    prospects_run: prospectCount,
    deals_won: totalDealsWon,
    deal_value_closed: totalDealValue,
    action: `Ran ${prospectCount} prospects through 7-stage closer — ${totalDealsWon} deals booked ($${totalDealValue} value)`,
    timestamp: new Date().toISOString(),
  };
}

module.exports = { run, startNegotiation, handleObjection, closeDeal, CLOSING_SCRIPTS };
