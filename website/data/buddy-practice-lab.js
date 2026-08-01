window.BUDDY_PRACTICE_LAB = {
  "difficulty_levels": [
    {
      "behavior": "Give time, hints, and one follow-up at a time.",
      "id": "supportive",
      "label": "Supportive"
    },
    {
      "behavior": "Use normal interruptions, ambiguity, and follow-up questions.",
      "id": "realistic",
      "label": "Realistic"
    },
    {
      "behavior": "Use skeptical follow-ups and tighter timing without hostility or deception.",
      "id": "challenging",
      "label": "Challenging"
    }
  ],
  "hard_boundaries": [
    "no impersonating a candidate during a real interview or assessment",
    "no automated employment eligibility decision",
    "no inference or scoring of protected or sensitive traits",
    "no fabricated credentials, references, employment, education, or achievements",
    "no application, message, call, acceptance, signature, or submission without exact owner approval",
    "no real-person voice or likeness use without active adult consent and scoped rights",
    "no raw voice recording stored in a downloadable practice packet"
  ],
  "job_prep_outputs": [
    "target-role evidence map",
    "ATS-safe resume review checklist",
    "STAR story bank",
    "role-specific question set",
    "mock interview rounds",
    "skills-gap learning sprint",
    "salary and offer research checklist",
    "thank-you and follow-up draft",
    "application tracker handoff",
    "owner-review gate before any submission"
  ],
  "modes": [
    {
      "id": "job_interview",
      "label": "Job interview",
      "opening": "Tell me about yourself and connect your experience to this role.",
      "questions": [
        "Describe a result you are proud of and the actions you took.",
        "Tell me about a difficult problem, the options you considered, and what happened.",
        "Explain how you prioritize when several deadlines compete.",
        "Describe a time you received difficult feedback and what you changed.",
        "What would your first thirty days in this role look like?",
        "What questions would you ask the hiring team before deciding whether this role fits?"
      ],
      "specialists": [
        "resume-builder-bot",
        "job-application-bot",
        "buddy-bot"
      ]
    },
    {
      "id": "career_plan",
      "label": "Career and job preparation",
      "opening": "Describe the role you want, the experience you have, and the gap you most want to close.",
      "questions": [
        "Which achievements best prove you can perform the target role?",
        "Which job requirements are strengths, learnable gaps, or true constraints?",
        "How would you rewrite one achievement with action, scale, and result?",
        "Which portfolio sample could demonstrate your ability without revealing private employer information?",
        "What is one realistic learning sprint you can complete this week?",
        "Which applications and follow-ups should remain owner-reviewed before submission?"
      ],
      "specialists": [
        "resume-builder-bot",
        "job-application-bot",
        "mos-career-planner"
      ]
    },
    {
      "id": "sales_call",
      "label": "Sales conversation",
      "opening": "Open the conversation by confirming the customer's goal instead of pitching immediately.",
      "questions": [
        "Ask three questions that uncover the current problem and its measurable cost.",
        "Summarize the customer's need in plain language and ask whether you understood it.",
        "Explain the offer without unsupported claims or guaranteed outcomes.",
        "Respond to a price objection with evidence, options, and room to decline.",
        "Handle a request for a feature the product does not currently have.",
        "Close with one clear, permission-based next step."
      ],
      "specialists": [
        "objection-handler-ai",
        "pitch-craft-ai",
        "buddy-bot"
      ]
    },
    {
      "id": "customer_support",
      "label": "Customer support",
      "opening": "A customer is frustrated because a promised result did not arrive. Acknowledge the problem and verify the facts.",
      "questions": [
        "Ask for the minimum information needed to investigate.",
        "Separate what is known, unknown, and still being checked.",
        "Offer available remedies without promising an unavailable result.",
        "Respond to an angry message without mirroring hostility.",
        "Explain when and how the issue should be escalated.",
        "Close with a written summary, owner, and next update time."
      ],
      "specialists": [
        "review-manager",
        "case-manager",
        "buddy-bot"
      ]
    },
    {
      "id": "manager_conversation",
      "label": "Manager conversation",
      "opening": "Prepare a respectful conversation about expectations, workload, feedback, or a missed commitment.",
      "questions": [
        "State the observable facts without guessing another person's motive.",
        "Explain the impact on the work, customer, or team.",
        "Ask for the other person's perspective and listen for new evidence.",
        "Agree on a measurable next step and realistic deadline.",
        "Practice responding when the other person disagrees.",
        "Document the agreement without adding sensitive personal speculation."
      ],
      "specialists": [
        "project-management",
        "change-manager",
        "buddy-bot"
      ]
    },
    {
      "id": "negotiation",
      "label": "Negotiation",
      "opening": "Define your goal, walk-away conditions, evidence, and the interests on both sides.",
      "questions": [
        "Separate positions from the underlying interests.",
        "Offer two lawful options with clear tradeoffs.",
        "Ask a calibrated question instead of making an unsupported threat.",
        "Summarize price, scope, timing, ownership, and unresolved terms.",
        "Pause for qualified legal or financial review where required.",
        "Prepare a written recap that is not treated as a signed agreement."
      ],
      "specialists": [
        "cultural-intel",
        "contractual-risk-sim",
        "partnership-leverage"
      ]
    },
    {
      "id": "presentation",
      "label": "Presentation and pitch",
      "opening": "Give a clear opening that names the audience's problem and the purpose of this presentation.",
      "questions": [
        "Explain the main idea in one sentence without jargon.",
        "Support the claim with a source, demonstration, or labeled assumption.",
        "Practice a transition between the problem, solution, and evidence.",
        "Answer a skeptical question directly before adding context.",
        "Deliver a concise closing with one requested next step.",
        "Review timing, accessibility, captions, contrast, and backup materials."
      ],
      "specialists": [
        "pitch-deck",
        "pitch-craft-ai",
        "buddy-bot"
      ]
    },
    {
      "id": "audition",
      "label": "Acting or creator audition",
      "opening": "Introduce the original or licensed material, intended role, tone, and performance boundary.",
      "questions": [
        "Perform the scene or original passage with a clear objective.",
        "Repeat it with a different emotional choice while preserving the character.",
        "Practice a slate, framing, eyeline, sound, and lighting check.",
        "Explain the role using your own interpretation rather than imitating a real performer.",
        "Review voice, image, music, script, and commercial-use rights.",
        "Choose the strongest take using a consistent rubric and owner review."
      ],
      "specialists": [
        "animation-pipeline",
        "music-production",
        "buddy-bot"
      ]
    },
    {
      "id": "language_practice",
      "label": "Language and communication practice",
      "opening": "Choose a real-life scenario, language, proficiency level, and the kind of correction you want.",
      "questions": [
        "Practice a greeting and explain the purpose of the conversation.",
        "Ask for clarification when a word or instruction is unfamiliar.",
        "Restate the other person's point to confirm understanding.",
        "Practice names, numbers, dates, and context-specific vocabulary.",
        "Repeat the exchange at a slower and then natural pace.",
        "Record corrections as learning notes, not judgments about intelligence or identity."
      ],
      "specialists": [
        "localization",
        "cultural-intel",
        "buddy-bot"
      ]
    }
  ],
  "name": "Buddy Job Prep and Role-Play Lab",
  "review_dimensions": [
    "clear objective",
    "specific evidence",
    "structured answer",
    "active listening",
    "honest uncertainty",
    "professional boundaries",
    "concise delivery",
    "useful next step"
  ],
  "schema": "dreamco.buddy_practice_lab.v1",
  "truth_boundary": "Buddy can create private practice, coaching, and preparation sessions. It does not impersonate a candidate in a real interview, make employment decisions, secretly score protected traits, or replace a qualified professional."
};
