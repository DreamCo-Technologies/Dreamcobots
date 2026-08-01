window.BUDDY_CONNECTED_LIFE = {
  "access_levels": [
    {
      "allowed": [
        "organize metadata"
      ],
      "id": "catalog_only",
      "label": "Catalog only"
    },
    {
      "allowed": [
        "read owner-selected resources",
        "summarize",
        "compare"
      ],
      "id": "read_selected",
      "label": "Read selected data"
    },
    {
      "allowed": [
        "prepare drafts",
        "preview changes",
        "request approval"
      ],
      "id": "draft_only",
      "label": "Draft work"
    },
    {
      "allowed": [
        "perform one exact approved write at a time"
      ],
      "id": "approved_actions",
      "label": "Approved actions"
    }
  ],
  "app_categories": [
    {
      "id": "social",
      "label": "Social and community"
    },
    {
      "id": "communication",
      "label": "Email, chat, calls, and calendar"
    },
    {
      "id": "creative",
      "label": "Photo, video, music, and design"
    },
    {
      "id": "business",
      "label": "Business operations and CRM"
    },
    {
      "id": "finance",
      "label": "Bills, banking, payments, and accounting"
    },
    {
      "id": "commerce",
      "label": "Shopping, selling, and subscriptions"
    },
    {
      "id": "developer",
      "label": "Code, repositories, and deployment"
    },
    {
      "id": "education",
      "label": "Learning, school, and research"
    },
    {
      "id": "health",
      "label": "Health and wellness"
    },
    {
      "id": "home",
      "label": "Home, utilities, and connected devices"
    },
    {
      "id": "travel",
      "label": "Travel, transportation, and maps"
    },
    {
      "id": "government",
      "label": "Government and public services"
    },
    {
      "id": "files",
      "label": "Files, storage, and documents"
    },
    {
      "id": "custom",
      "label": "Custom app or documented API"
    }
  ],
  "data_controls": [
    "purpose-specific permission",
    "read-only first",
    "minimum necessary fields",
    "bounded retention",
    "view, correct, export, revoke, and delete controls",
    "separate private-training opt-in",
    "separate rights-cleared licensing opt-in",
    "no sale of sensitive, minor, credential, or third-party personal data"
  ],
  "financial_capabilities": [
    "bill and renewal calendar",
    "subscription inventory",
    "monthly and annual cost normalization",
    "possible duplicate detection",
    "unused-service review prompts",
    "cancellation and refund handoff",
    "budget scenarios",
    "payment approval packet",
    "receipt and notification tracking"
  ],
  "group_workflows": [
    "search and compare across selected apps",
    "prepare one dashboard from authorized read-only data",
    "draft coordinated updates for several apps",
    "track subscriptions, renewals, and duplicate services",
    "prepare privacy access, export, correction, deletion, and opt-out requests",
    "create a portable owner archive with provenance and retention rules"
  ],
  "high_impact_actions": [
    "publish content",
    "send a message",
    "go live",
    "change an account",
    "cancel a subscription",
    "submit a privacy request",
    "make a payment",
    "transfer funds",
    "sell or license data"
  ],
  "name": "Buddy Connected Life",
  "schema": "dreamco.buddy_connected_life.v1",
  "social_modes": [
    {
      "approval": "none until publish is requested",
      "id": "draft",
      "label": "Draft only"
    },
    {
      "approval": "exact account, content, media, and time",
      "id": "schedule",
      "label": "Schedule after review"
    },
    {
      "approval": "single-use fingerprinted approval",
      "id": "publish_once",
      "label": "Publish one approved item"
    },
    {
      "approval": "authenticated local production adapter",
      "id": "live_rehearsal",
      "label": "Private live rehearsal"
    },
    {
      "approval": "fresh owner go-live approval plus moderation and emergency stop",
      "id": "live_show",
      "label": "Go live"
    }
  ],
  "truth_boundary": "Buddy can organize and plan work only for apps, accounts, and data the owner connects or imports. Outside companies control their own systems and must honor privacy requests through their official processes."
};
