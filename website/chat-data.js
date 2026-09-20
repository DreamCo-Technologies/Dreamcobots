/* Buddy chat-sync catalogs. Public data only. No keys. */
window.BUDDY_CHAT = {
  "pin": [
    "apache-2.0",
    "mit",
    "bsd-2-clause",
    "bsd-3-clause",
    "cc0-1.0",
    "unlicense",
    "isc",
    "zlib",
    "mpl-2.0",
    "cc-by-4.0",
    "cc-by-sa-4.0"
  ],
  "canonical": [
    "rajpurkar/squad",
    "stanfordnlp/imdb",
    "openai/gsm8k",
    "cais/mmlu",
    "Helsinki-NLP/opus-100",
    "google-research-datasets/paws"
  ],
  "allowHosts": [
    "huggingface.co",
    "spdx.org",
    "www.onetcenter.org",
    "docs.x.ai",
    "allenai.org",
    "crfm.stanford.edu",
    "faiss.ai",
    "qdrant.tech",
    "ollama.com",
    "docs.vllm.ai",
    "opensource.org",
    "docs.stripe.com",
    "developers.google.com",
    "www.anthropic.com",
    "platform.openai.com"
  ],
  "tasks": [
    {
      "id": "text-classification",
      "group": "Language",
      "name": "Text classification",
      "studies": "Labels, splits, class balance on the card",
      "buddy": "buddy-language",
      "other": "O*NET skills are not labels",
      "href": "https://huggingface.co/datasets?task_categories=text-classification"
    },
    {
      "id": "token-classification",
      "group": "Language",
      "name": "Token classification",
      "studies": "NER / POS scheme, IOB notes",
      "buddy": "buddy-language",
      "other": "No GitHub twin",
      "href": "https://huggingface.co/datasets?task_categories=token-classification"
    },
    {
      "id": "question-answering",
      "group": "Language",
      "name": "Question answering",
      "studies": "Extractive vs generative, context source",
      "buddy": "buddy-eval",
      "other": "Goals are work, not SQuAD",
      "href": "https://huggingface.co/datasets?task_categories=question-answering"
    },
    {
      "id": "table-question-answering",
      "group": "Language",
      "name": "Table QA",
      "studies": "Table source, cell cite",
      "buddy": "buddy-eval",
      "other": "O*NET tables are occupation rows",
      "href": "https://huggingface.co/datasets?task_categories=table-question-answering"
    },
    {
      "id": "zero-shot-classification",
      "group": "Language",
      "name": "Zero-shot classification",
      "studies": "Candidate labels, template",
      "buddy": "buddy-language",
      "other": "Specialists are not zero-shot heads",
      "href": "https://huggingface.co/datasets?task_categories=zero-shot-classification"
    },
    {
      "id": "translation",
      "group": "Language",
      "name": "Translation",
      "studies": "Language pair, license both sides",
      "buddy": "buddy-language",
      "other": "Grok translate is paid inference",
      "href": "https://huggingface.co/datasets?task_categories=translation"
    },
    {
      "id": "summarization",
      "group": "Language",
      "name": "Summarization",
      "studies": "News vs paper, abstractive note",
      "buddy": "buddy-language",
      "other": "Goal playbooks are not summaries of HF",
      "href": "https://huggingface.co/datasets?task_categories=summarization"
    },
    {
      "id": "feature-extraction",
      "group": "Language",
      "name": "Feature extraction",
      "studies": "Embedding dim, pooling",
      "buddy": "buddy-language",
      "other": "Local embed families stay named",
      "href": "https://huggingface.co/datasets?task_categories=feature-extraction"
    },
    {
      "id": "text-generation",
      "group": "Language",
      "name": "Text generation",
      "studies": "Instruction vs web crawl, PII",
      "buddy": "buddy-language",
      "other": "Do not scrape chats into a package",
      "href": "https://huggingface.co/datasets?task_categories=text-generation"
    },
    {
      "id": "fill-mask",
      "group": "Language",
      "name": "Fill-mask",
      "studies": "MLM domain",
      "buddy": "buddy-language",
      "other": "Study only",
      "href": "https://huggingface.co/datasets?task_categories=fill-mask"
    },
    {
      "id": "sentence-similarity",
      "group": "Language",
      "name": "Sentence similarity",
      "studies": "Pair source, score type",
      "buddy": "buddy-language",
      "other": "O*NET keyword match is not STS",
      "href": "https://huggingface.co/datasets?task_categories=sentence-similarity"
    },
    {
      "id": "multiple-choice",
      "group": "Language",
      "name": "Multiple choice",
      "studies": "Exam source, leakage risk",
      "buddy": "buddy-eval",
      "other": "Holdout stays native",
      "href": "https://huggingface.co/datasets?task_categories=multiple-choice"
    },
    {
      "id": "text-ranking",
      "group": "Language",
      "name": "Text ranking",
      "studies": "Query set, qrels license",
      "buddy": "buddy-eval",
      "other": "Search is not a Hub dump",
      "href": "https://huggingface.co/datasets?task_categories=text-ranking"
    },
    {
      "id": "text-retrieval",
      "group": "Language",
      "name": "Text retrieval",
      "studies": "Corpus license, BEIR-style splits",
      "buddy": "buddy-eval",
      "other": "Repo scan is not a corpus",
      "href": "https://huggingface.co/datasets?task_categories=text-retrieval"
    },
    {
      "id": "text-to-speech",
      "group": "Speech",
      "name": "Text to speech",
      "studies": "Speaker consent, accent",
      "buddy": "buddy-speech",
      "other": "No voice clone of a user",
      "href": "https://huggingface.co/datasets?task_categories=text-to-speech"
    },
    {
      "id": "text-to-audio",
      "group": "Speech",
      "name": "Text to audio",
      "studies": "Music vs SFX license",
      "buddy": "buddy-speech",
      "other": "Foundry has no audio weights",
      "href": "https://huggingface.co/datasets?task_categories=text-to-audio"
    },
    {
      "id": "automatic-speech-recognition",
      "group": "Speech",
      "name": "Speech recognition",
      "studies": "Hours, language, recording consent",
      "buddy": "buddy-speech",
      "other": "Browser mic is grant-first",
      "href": "https://huggingface.co/datasets?task_categories=automatic-speech-recognition"
    },
    {
      "id": "audio-to-audio",
      "group": "Speech",
      "name": "Audio to audio",
      "studies": "Enhancement vs conversion",
      "buddy": "buddy-speech",
      "other": "Study card only",
      "href": "https://huggingface.co/datasets?task_categories=audio-to-audio"
    },
    {
      "id": "audio-classification",
      "group": "Speech",
      "name": "Audio classification",
      "studies": "Event labels, scene vs speaker",
      "buddy": "buddy-speech",
      "other": "Hey-Buddy wake-word is not ours",
      "href": "https://huggingface.co/datasets?task_categories=audio-classification"
    },
    {
      "id": "voice-activity-detection",
      "group": "Speech",
      "name": "Voice activity",
      "studies": "Threshold notes",
      "buddy": "buddy-speech",
      "other": "Local VAD later, named",
      "href": "https://huggingface.co/datasets?task_categories=voice-activity-detection"
    },
    {
      "id": "image-classification",
      "group": "Vision",
      "name": "Image classification",
      "studies": "Class list, known bias",
      "buddy": "buddy-vision",
      "other": "O*NET has no pixels",
      "href": "https://huggingface.co/datasets?task_categories=image-classification"
    },
    {
      "id": "object-detection",
      "group": "Vision",
      "name": "Object detection",
      "studies": "Box format, crowd notes",
      "buddy": "buddy-vision",
      "other": "Study, do not scrape ImageNet mirrors",
      "href": "https://huggingface.co/datasets?task_categories=object-detection"
    },
    {
      "id": "image-segmentation",
      "group": "Vision",
      "name": "Image segmentation",
      "studies": "Semantic vs instance",
      "buddy": "buddy-vision",
      "other": "No silent face datasets",
      "href": "https://huggingface.co/datasets?task_categories=image-segmentation"
    },
    {
      "id": "depth-estimation",
      "group": "Vision",
      "name": "Depth estimation",
      "studies": "Sensor vs predicted",
      "buddy": "buddy-vision",
      "other": "Robotics later",
      "href": "https://huggingface.co/datasets?task_categories=depth-estimation"
    },
    {
      "id": "image-to-text",
      "group": "Vision",
      "name": "Image to text",
      "studies": "Caption source, alt text quality",
      "buddy": "buddy-vision",
      "other": "Goal copy is not a caption set",
      "href": "https://huggingface.co/datasets?task_categories=image-to-text"
    },
    {
      "id": "text-to-image",
      "group": "Vision",
      "name": "Text to image",
      "studies": "Prompt-image pairs, artist consent",
      "buddy": "buddy-vision",
      "other": "Imagine tools are not a dataset we own",
      "href": "https://huggingface.co/datasets?task_categories=text-to-image"
    },
    {
      "id": "image-to-image",
      "group": "Vision",
      "name": "Image to image",
      "studies": "Edit pairs, inpaint masks",
      "buddy": "buddy-vision",
      "other": "Study recipes",
      "href": "https://huggingface.co/datasets?task_categories=image-to-image"
    },
    {
      "id": "unconditional-image-generation",
      "group": "Vision",
      "name": "Unconditional image gen",
      "studies": "Domain, license of pixels",
      "buddy": "buddy-vision",
      "other": "No weight scrape",
      "href": "https://huggingface.co/datasets?task_categories=unconditional-image-generation"
    },
    {
      "id": "video-classification",
      "group": "Vision",
      "name": "Video classification",
      "studies": "Clip length, label grain",
      "buddy": "buddy-vision",
      "other": "Heavy. Card only",
      "href": "https://huggingface.co/datasets?task_categories=video-classification"
    },
    {
      "id": "image-feature-extraction",
      "group": "Vision",
      "name": "Image features",
      "studies": "Backbone, dim",
      "buddy": "buddy-vision",
      "other": "timm is a library, not data",
      "href": "https://huggingface.co/datasets?task_categories=image-feature-extraction"
    },
    {
      "id": "zero-shot-image-classification",
      "group": "Vision",
      "name": "Zero-shot image class",
      "studies": "CLIP-class labels",
      "buddy": "buddy-vision",
      "other": "Named families only",
      "href": "https://huggingface.co/datasets?task_categories=zero-shot-image-classification"
    },
    {
      "id": "zero-shot-object-detection",
      "group": "Vision",
      "name": "Zero-shot detection",
      "studies": "Open-vocab notes",
      "buddy": "buddy-vision",
      "other": "Study",
      "href": "https://huggingface.co/datasets?task_categories=zero-shot-object-detection"
    },
    {
      "id": "mask-generation",
      "group": "Vision",
      "name": "Mask generation",
      "studies": "SAM-class masks",
      "buddy": "buddy-vision",
      "other": "Study",
      "href": "https://huggingface.co/datasets?task_categories=mask-generation"
    },
    {
      "id": "visual-question-answering",
      "group": "Vision",
      "name": "Visual QA",
      "studies": "Question source, region cite",
      "buddy": "buddy-eval",
      "other": "Not a medical diagnosis set",
      "href": "https://huggingface.co/datasets?task_categories=visual-question-answering"
    },
    {
      "id": "image-to-video",
      "group": "Motion",
      "name": "Image to video",
      "studies": "Frame rate, identity risk",
      "buddy": "buddy-vision",
      "other": "Paid GPU. Card only",
      "href": "https://huggingface.co/datasets?task_categories=image-to-video"
    },
    {
      "id": "text-to-video",
      "group": "Motion",
      "name": "Text to video",
      "studies": "Prompt pairs, compute",
      "buddy": "buddy-vision",
      "other": "Not a Buddy weight",
      "href": "https://huggingface.co/datasets?task_categories=text-to-video"
    },
    {
      "id": "text-to-3d",
      "group": "Motion",
      "name": "Text to 3D",
      "studies": "Mesh license",
      "buddy": "buddy-vision",
      "other": "Study",
      "href": "https://huggingface.co/datasets?task_categories=text-to-3d"
    },
    {
      "id": "image-to-3d",
      "group": "Motion",
      "name": "Image to 3D",
      "studies": "Scan consent",
      "buddy": "buddy-vision",
      "other": "Study",
      "href": "https://huggingface.co/datasets?task_categories=image-to-3d"
    },
    {
      "id": "video-text-to-text",
      "group": "Motion",
      "name": "Video-text to text",
      "studies": "Caption + clip license",
      "buddy": "buddy-vision",
      "other": "Study",
      "href": "https://huggingface.co/datasets?task_categories=video-text-to-text"
    },
    {
      "id": "image-text-to-text",
      "group": "Multimodal",
      "name": "Image-text to text",
      "studies": "VLM instruction rows, PII in pixels",
      "buddy": "buddy-language",
      "other": "Grok vision is paid",
      "href": "https://huggingface.co/datasets?task_categories=image-text-to-text"
    },
    {
      "id": "image-text-to-image",
      "group": "Multimodal",
      "name": "Image-text to image",
      "studies": "Edit instruction pairs",
      "buddy": "buddy-vision",
      "other": "Study",
      "href": "https://huggingface.co/datasets?task_categories=image-text-to-image"
    },
    {
      "id": "image-text-to-video",
      "group": "Multimodal",
      "name": "Image-text to video",
      "studies": "Identity + prompt",
      "buddy": "buddy-vision",
      "other": "Study",
      "href": "https://huggingface.co/datasets?task_categories=image-text-to-video"
    },
    {
      "id": "visual-document-retrieval",
      "group": "Multimodal",
      "name": "Visual document retrieval",
      "studies": "PDF page license",
      "buddy": "buddy-eval",
      "other": "Repo files are not a retrieval set",
      "href": "https://huggingface.co/datasets?task_categories=visual-document-retrieval"
    },
    {
      "id": "any-to-any",
      "group": "Multimodal",
      "name": "Any to any",
      "studies": "Modality graph, huge cards",
      "buddy": "buddy-index",
      "other": "Do not claim a unified model",
      "href": "https://huggingface.co/datasets?task_categories=any-to-any"
    },
    {
      "id": "tabular-classification",
      "group": "Tables",
      "name": "Tabular classification",
      "studies": "Column types, leakage",
      "buddy": "buddy-eval",
      "other": "O*NET is a table we already own",
      "href": "https://huggingface.co/datasets?task_categories=tabular-classification"
    },
    {
      "id": "tabular-regression",
      "group": "Tables",
      "name": "Tabular regression",
      "studies": "Target units",
      "buddy": "buddy-eval",
      "other": "No fake finance ticks",
      "href": "https://huggingface.co/datasets?task_categories=tabular-regression"
    },
    {
      "id": "tabular-to-text",
      "group": "Tables",
      "name": "Tabular to text",
      "studies": "Template vs free text",
      "buddy": "buddy-language",
      "other": "Study",
      "href": "https://huggingface.co/datasets?task_categories=tabular-to-text"
    },
    {
      "id": "table-to-text",
      "group": "Tables",
      "name": "Table to text",
      "studies": "WikiTables-class notes",
      "buddy": "buddy-language",
      "other": "Study",
      "href": "https://huggingface.co/datasets?task_categories=table-to-text"
    },
    {
      "id": "time-series-forecasting",
      "group": "Tables",
      "name": "Time series",
      "studies": "Frequency, horizon",
      "buddy": "buddy-eval",
      "other": "Actions run history is not a market feed",
      "href": "https://huggingface.co/datasets?task_categories=time-series-forecasting"
    },
    {
      "id": "graph-ml",
      "group": "Tables",
      "name": "Graph ML",
      "studies": "Node/edge license",
      "buddy": "buddy-eval",
      "other": "Wiring map is not a GNN corpus",
      "href": "https://huggingface.co/datasets?task_categories=graph-ml"
    },
    {
      "id": "reinforcement-learning",
      "group": "Agents",
      "name": "Reinforcement learning",
      "studies": "Env license, reward",
      "buddy": "buddy-eval",
      "other": "Sandbox first. No live spend env",
      "href": "https://huggingface.co/datasets?task_categories=reinforcement-learning"
    },
    {
      "id": "robotics",
      "group": "Agents",
      "name": "Robotics",
      "studies": "LeRobot episodes, embodiment, consent",
      "buddy": "buddy-eval",
      "other": "Devices stay grant-first, never takeover",
      "href": "https://huggingface.co/datasets?task_categories=robotics"
    }
  ],
  "occupations": [
    {
      "soc": "11-1011.00",
      "title": "Chief Executives",
      "group": "Management",
      "zone": 5,
      "dream": "Run the company yourself",
      "middlemen": [
        "management consultants",
        "executive coaches who sell retainers"
      ],
      "tasks": [
        "Set direction",
        "Approve spend",
        "Hire directly"
      ],
      "skills": [
        "judgment",
        "finance"
      ],
      "division": "DreamBizLaunch",
      "face": "business",
      "hubQuery": "business strategy",
      "keywords": [
        "ceo",
        "founder",
        "owner",
        "company"
      ]
    },
    {
      "soc": "11-1021.00",
      "title": "General and Operations Managers",
      "group": "Management",
      "zone": 4,
      "dream": "Operate without a layer of agencies",
      "middlemen": [
        "ops consultancies"
      ],
      "tasks": [
        "Schedule work",
        "Track delivery",
        "Cut waste"
      ],
      "skills": [
        "planning",
        "coordination"
      ],
      "division": "DreamOps",
      "face": "operator",
      "hubQuery": "operations",
      "keywords": [
        "ops",
        "operations",
        "manager",
        "run"
      ]
    },
    {
      "soc": "11-2021.00",
      "title": "Marketing Managers",
      "group": "Management",
      "zone": 4,
      "dream": "Reach customers without an ad agency",
      "middlemen": [
        "ad agencies",
        "lead shops"
      ],
      "tasks": [
        "Position offer",
        "Write campaigns",
        "Measure"
      ],
      "skills": [
        "copy",
        "analytics"
      ],
      "division": "DreamSalesPro",
      "face": "business",
      "hubQuery": "marketing copy",
      "keywords": [
        "marketing",
        "brand",
        "campaign",
        "ads"
      ]
    },
    {
      "soc": "11-2022.00",
      "title": "Sales Managers",
      "group": "Management",
      "zone": 4,
      "dream": "Close work without a sales house",
      "middlemen": [
        "outsourced SDR shops"
      ],
      "tasks": [
        "Pipeline",
        "Scripts",
        "Follow-up"
      ],
      "skills": [
        "persuasion",
        "crm"
      ],
      "division": "DreamSalesPro",
      "face": "agency",
      "hubQuery": "sales",
      "keywords": [
        "sales",
        "pipeline",
        "close",
        "leads"
      ]
    },
    {
      "soc": "11-3031.00",
      "title": "Financial Managers",
      "group": "Management",
      "zone": 4,
      "dream": "See the money yourself",
      "middlemen": [
        "bookkeeping mills"
      ],
      "tasks": [
        "Cash view",
        "Budget",
        "Forecast"
      ],
      "skills": [
        "accounting",
        "analysis"
      ],
      "division": "DreamFinance",
      "face": "business",
      "hubQuery": "finance",
      "keywords": [
        "finance",
        "cfo",
        "cash",
        "budget"
      ]
    },
    {
      "soc": "11-9021.00",
      "title": "Construction Managers",
      "group": "Management",
      "zone": 4,
      "dream": "Run a job without a GC markup you do not need",
      "middlemen": [
        "broker GCs on small work"
      ],
      "tasks": [
        "Schedule trades",
        "Permits",
        "Punch list"
      ],
      "skills": [
        "scheduling",
        "safety"
      ],
      "division": "DreamOps",
      "face": "operator",
      "hubQuery": "construction",
      "keywords": [
        "construction",
        "build",
        "renovation",
        "contractor"
      ]
    },
    {
      "soc": "13-1111.00",
      "title": "Management Analysts",
      "group": "Business",
      "zone": 4,
      "dream": "Fix the process without a consulting firm",
      "middlemen": [
        "strategy boutiques"
      ],
      "tasks": [
        "Map waste",
        "Pilot a change",
        "Measure"
      ],
      "skills": [
        "analysis",
        "writing"
      ],
      "division": "DreamAgency",
      "face": "operator",
      "hubQuery": "process improvement",
      "keywords": [
        "consultant",
        "process",
        "efficiency",
        "lean"
      ]
    },
    {
      "soc": "13-1161.00",
      "title": "Market Research Analysts",
      "group": "Business",
      "zone": 4,
      "dream": "Know the market from primary sources",
      "middlemen": [
        "research vendors"
      ],
      "tasks": [
        "Question",
        "Sources",
        "Uncertainty"
      ],
      "skills": [
        "research",
        "stats"
      ],
      "division": "DreamData",
      "face": "researcher",
      "hubQuery": "market research",
      "keywords": [
        "research",
        "market",
        "survey",
        "competitor"
      ]
    },
    {
      "soc": "13-2011.00",
      "title": "Accountants and Auditors",
      "group": "Business",
      "zone": 4,
      "dream": "Keep the books without a monthly package you do not use",
      "middlemen": [
        "outsourced bookkeeping shops"
      ],
      "tasks": [
        "Ledger",
        "Reconciliation",
        "Reports"
      ],
      "skills": [
        "accounting",
        "excel"
      ],
      "division": "DreamFinance",
      "face": "business",
      "hubQuery": "accounting",
      "keywords": [
        "books",
        "accounting",
        "taxes",
        "bookkeeping",
        "cpa"
      ]
    },
    {
      "soc": "13-2051.00",
      "title": "Financial and Investment Analysts",
      "group": "Business",
      "zone": 4,
      "dream": "Read a deal yourself",
      "middlemen": [
        "pay-to-pitch newsletters"
      ],
      "tasks": [
        "Model",
        "Risk",
        "Compare"
      ],
      "skills": [
        "modeling",
        "writing"
      ],
      "division": "DreamFinance",
      "face": "researcher",
      "hubQuery": "financial analysis",
      "keywords": [
        "invest",
        "valuation",
        "deal",
        "model"
      ]
    },
    {
      "soc": "15-1211.00",
      "title": "Computer Systems Analysts",
      "group": "Computer",
      "zone": 4,
      "dream": "Specify the system without a systems integrator tax",
      "middlemen": [
        "integrator lock-in"
      ],
      "tasks": [
        "Requirements",
        "Interfaces",
        "Tests"
      ],
      "skills": [
        "systems",
        "sql"
      ],
      "division": "DreamIntegrations",
      "face": "integrator",
      "hubQuery": "systems analysis",
      "keywords": [
        "systems",
        "requirements",
        "integration"
      ]
    },
    {
      "soc": "15-1212.00",
      "title": "Information Security Analysts",
      "group": "Computer",
      "zone": 4,
      "dream": "Harden without a fear-retainer",
      "middlemen": [
        "checkbox MSSPs"
      ],
      "tasks": [
        "Threat model",
        "Permissions",
        "Evidence"
      ],
      "skills": [
        "security",
        "logging"
      ],
      "division": "DreamCyber",
      "face": "safety",
      "hubQuery": "cybersecurity",
      "keywords": [
        "security",
        "cyber",
        "soc",
        "vulnerability"
      ]
    },
    {
      "soc": "15-1242.00",
      "title": "Database Administrators",
      "group": "Computer",
      "zone": 4,
      "dream": "Own the data layer",
      "middlemen": [
        "hosted-DB upsells you do not need"
      ],
      "tasks": [
        "Schema",
        "Backup",
        "Access"
      ],
      "skills": [
        "sql",
        "ops"
      ],
      "division": "DreamData",
      "face": "coder",
      "hubQuery": "database",
      "keywords": [
        "database",
        "sql",
        "postgres",
        "data"
      ]
    },
    {
      "soc": "15-1252.00",
      "title": "Software Developers",
      "group": "Computer",
      "zone": 4,
      "dream": "Ship software without a body shop",
      "middlemen": [
        "staffing firms",
        "offshore mills"
      ],
      "tasks": [
        "Design",
        "Code",
        "Test",
        "Ship"
      ],
      "skills": [
        "programming",
        "testing"
      ],
      "division": "DreamCodeLab",
      "face": "coder",
      "hubQuery": "code generation",
      "keywords": [
        "software",
        "app",
        "code",
        "developer",
        "programming",
        "saas"
      ]
    },
    {
      "soc": "15-1254.00",
      "title": "Web Developers",
      "group": "Computer",
      "zone": 4,
      "dream": "Put a site live without a website mill",
      "middlemen": [
        "template mills",
        "$5k brochure shops"
      ],
      "tasks": [
        "Pages",
        "Forms",
        "Ship"
      ],
      "skills": [
        "html",
        "accessibility"
      ],
      "division": "DreamCodeLab",
      "face": "builder",
      "hubQuery": "web development",
      "keywords": [
        "website",
        "web",
        "landing",
        "shopify",
        "wordpress"
      ]
    },
    {
      "soc": "15-1255.00",
      "title": "Web and Digital Interface Designers",
      "group": "Computer",
      "zone": 4,
      "dream": "Design the product you will ship",
      "middlemen": [
        "brand-only studios"
      ],
      "tasks": [
        "Flows",
        "Copy",
        "Accessibility"
      ],
      "skills": [
        "ux",
        "visual"
      ],
      "division": "DreamContent",
      "face": "builder",
      "hubQuery": "ui design",
      "keywords": [
        "design",
        "ui",
        "ux",
        "interface"
      ]
    },
    {
      "soc": "15-2051.00",
      "title": "Data Scientists",
      "group": "Computer",
      "zone": 5,
      "dream": "Answer from your data, not a dashboard vendor",
      "middlemen": [
        "BI agencies"
      ],
      "tasks": [
        "Question",
        "Features",
        "Holdout"
      ],
      "skills": [
        "stats",
        "python"
      ],
      "division": "DreamData",
      "face": "researcher",
      "hubQuery": "data science",
      "keywords": [
        "data",
        "ml",
        "model",
        "predict",
        "analytics"
      ]
    },
    {
      "soc": "15-2099.01",
      "title": "Bioinformatics Technicians",
      "group": "Computer",
      "zone": 4,
      "dream": "Study licensed data, not scraped weights",
      "middlemen": [
        "unlicensed dataset brokers"
      ],
      "tasks": [
        "License",
        "Pipeline",
        "Eval"
      ],
      "skills": [
        "python",
        "biology"
      ],
      "division": "DreamFoundry",
      "face": "foundry",
      "hubQuery": "bioinformatics",
      "keywords": [
        "bio",
        "genome",
        "lab"
      ]
    },
    {
      "soc": "17-2112.00",
      "title": "Industrial Engineers",
      "group": "Engineering",
      "zone": 4,
      "dream": "Improve throughput yourself",
      "middlemen": [
        "lean-theater consultancies"
      ],
      "tasks": [
        "Map flow",
        "Bottleneck",
        "Pilot"
      ],
      "skills": [
        "process",
        "stats"
      ],
      "division": "DreamOps",
      "face": "operator",
      "hubQuery": "industrial engineering",
      "keywords": [
        "throughput",
        "factory",
        "lean",
        "process"
      ]
    },
    {
      "soc": "23-1011.00",
      "title": "Lawyers",
      "group": "Legal",
      "zone": 5,
      "dream": "Draft first, counsel second",
      "middlemen": [
        "form mills that pretend to be counsel"
      ],
      "tasks": [
        "Draft",
        "Review",
        "File plan"
      ],
      "skills": [
        "writing",
        "research"
      ],
      "division": "DreamLegal",
      "face": "safety",
      "hubQuery": "legal drafting",
      "keywords": [
        "legal",
        "contract",
        "trademark",
        "llc",
        "lawyer"
      ]
    },
    {
      "soc": "23-2011.00",
      "title": "Paralegals and Legal Assistants",
      "group": "Legal",
      "zone": 3,
      "dream": "Assemble the packet without a filing mill",
      "middlemen": [
        "document mills"
      ],
      "tasks": [
        "Checklist",
        "Exhibits",
        "Deadlines"
      ],
      "skills": [
        "organization",
        "writing"
      ],
      "division": "DreamLegal",
      "face": "operator",
      "hubQuery": "paralegal",
      "keywords": [
        "paralegal",
        "filing",
        "packet",
        "court"
      ]
    },
    {
      "soc": "25-2021.00",
      "title": "Elementary School Teachers",
      "group": "Education",
      "zone": 4,
      "dream": "Teach with your own materials",
      "middlemen": [
        "content mills"
      ],
      "tasks": [
        "Lesson",
        "Practice",
        "Check"
      ],
      "skills": [
        "instruction",
        "patience"
      ],
      "division": "DreamEducation",
      "face": "teacher",
      "hubQuery": "education",
      "keywords": [
        "teach",
        "school",
        "lesson",
        "classroom"
      ]
    },
    {
      "soc": "25-9031.00",
      "title": "Instructional Coordinators",
      "group": "Education",
      "zone": 5,
      "dream": "Build a course you actually own",
      "middlemen": [
        "course-funnel gurus"
      ],
      "tasks": [
        "Objectives",
        "Drills",
        "Mastery"
      ],
      "skills": [
        "curriculum",
        "assessment"
      ],
      "division": "DreamEducation",
      "face": "teacher",
      "hubQuery": "instructional design",
      "keywords": [
        "course",
        "curriculum",
        "training",
        "lms"
      ]
    },
    {
      "soc": "27-1024.00",
      "title": "Graphic Designers",
      "group": "Arts",
      "zone": 4,
      "dream": "Make the art for the offer",
      "middlemen": [
        "unlimited-design subscriptions"
      ],
      "tasks": [
        "Layout",
        "Type",
        "Export"
      ],
      "skills": [
        "visual",
        "brand"
      ],
      "division": "DreamContent",
      "face": "builder",
      "hubQuery": "graphic design",
      "keywords": [
        "logo",
        "graphic",
        "poster",
        "brand kit"
      ]
    },
    {
      "soc": "27-2012.00",
      "title": "Producers and Directors",
      "group": "Arts",
      "zone": 4,
      "dream": "Ship a show without a studio tax you do not need",
      "middlemen": [
        "middle-producer stacks"
      ],
      "tasks": [
        "Outline",
        "Shoot plan",
        "Edit"
      ],
      "skills": [
        "story",
        "ops"
      ],
      "division": "DreamStreaming",
      "face": "builder",
      "hubQuery": "video production",
      "keywords": [
        "video",
        "youtube",
        "film",
        "podcast",
        "channel"
      ]
    },
    {
      "soc": "27-3031.00",
      "title": "Public Relations Specialists",
      "group": "Arts",
      "zone": 4,
      "dream": "Tell the story yourself",
      "middlemen": [
        "PR retainers"
      ],
      "tasks": [
        "Angle",
        "Draft",
        "Approve send"
      ],
      "skills": [
        "writing",
        "media"
      ],
      "division": "DreamContent",
      "face": "business",
      "hubQuery": "public relations",
      "keywords": [
        "pr",
        "press",
        "media",
        "announcement"
      ]
    },
    {
      "soc": "27-3041.00",
      "title": "Editors",
      "group": "Arts",
      "zone": 4,
      "dream": "Edit without a ghost mill",
      "middlemen": [
        "content farms"
      ],
      "tasks": [
        "Cut",
        "Fact",
        "Voice"
      ],
      "skills": [
        "language",
        "judgment"
      ],
      "division": "DreamContent",
      "face": "coder",
      "hubQuery": "editing",
      "keywords": [
        "edit",
        "write",
        "book",
        "blog",
        "copy"
      ]
    },
    {
      "soc": "27-3043.00",
      "title": "Writers and Authors",
      "group": "Arts",
      "zone": 4,
      "dream": "Publish the work you mean",
      "middlemen": [
        "vanity presses"
      ],
      "tasks": [
        "Outline",
        "Draft",
        "Ship"
      ],
      "skills": [
        "writing",
        "research"
      ],
      "division": "DreamContent",
      "face": "companion",
      "hubQuery": "writing",
      "keywords": [
        "write",
        "author",
        "newsletter",
        "story"
      ]
    },
    {
      "soc": "29-1141.00",
      "title": "Registered Nurses",
      "group": "Healthcare",
      "zone": 3,
      "dream": "Admin help, never a diagnosis",
      "middlemen": [
        "credential mills"
      ],
      "tasks": [
        "Schedule",
        "Notes structure",
        "Education links"
      ],
      "skills": [
        "care",
        "documentation"
      ],
      "division": "DreamHealth",
      "face": "safety",
      "hubQuery": "nursing",
      "keywords": [
        "nurse",
        "clinic",
        "care",
        "health admin"
      ]
    },
    {
      "soc": "31-9092.00",
      "title": "Medical Assistants",
      "group": "Healthcare support",
      "zone": 3,
      "dream": "Run the front desk without a staffing agency",
      "middlemen": [
        "medical staffing firms"
      ],
      "tasks": [
        "Intake forms",
        "Reminders",
        "Filing"
      ],
      "skills": [
        "organization",
        "empathy"
      ],
      "division": "DreamHealth",
      "face": "operator",
      "hubQuery": "medical assistant",
      "keywords": [
        "front desk",
        "clinic ops",
        "intake"
      ]
    },
    {
      "soc": "35-1012.00",
      "title": "First-Line Supervisors of Food Workers",
      "group": "Food",
      "zone": 2,
      "dream": "Open the shop without a restaurant consultant",
      "middlemen": [
        "turnkey restaurant gurus"
      ],
      "tasks": [
        "Menu",
        "Labor",
        "Open/close"
      ],
      "skills": [
        "ops",
        "food"
      ],
      "division": "DreamBizLaunch",
      "face": "operator",
      "hubQuery": "restaurant",
      "keywords": [
        "restaurant",
        "bakery",
        "cafe",
        "food truck",
        "kitchen"
      ]
    },
    {
      "soc": "35-2014.00",
      "title": "Cooks, Restaurant",
      "group": "Food",
      "zone": 2,
      "dream": "Standardize the recipes you own",
      "middlemen": [
        "franchise packs you do not need"
      ],
      "tasks": [
        "Recipes",
        "Prep lists",
        "Cost"
      ],
      "skills": [
        "cooking",
        "timing"
      ],
      "division": "DreamBizLaunch",
      "face": "builder",
      "hubQuery": "culinary",
      "keywords": [
        "cook",
        "recipe",
        "kitchen"
      ]
    },
    {
      "soc": "37-1011.00",
      "title": "Housekeeping Supervisors",
      "group": "Building",
      "zone": 2,
      "dream": "Run cleaning routes yourself",
      "middlemen": [
        "national franchise fees"
      ],
      "tasks": [
        "Routes",
        "Checklists",
        "Supplies"
      ],
      "skills": [
        "ops",
        "qa"
      ],
      "division": "DreamOps",
      "face": "operator",
      "hubQuery": "facilities",
      "keywords": [
        "cleaning",
        "housekeeping",
        "janitorial"
      ]
    },
    {
      "soc": "39-5012.00",
      "title": "Hairdressers and Cosmetologists",
      "group": "Personal care",
      "zone": 3,
      "dream": "Book the chair without a marketplace cut",
      "middlemen": [
        "booking apps that own the customer"
      ],
      "tasks": [
        "Book",
        "Remind",
        "Retail"
      ],
      "skills": [
        "craft",
        "service"
      ],
      "division": "DreamSaaS",
      "face": "business",
      "hubQuery": "salon",
      "keywords": [
        "salon",
        "barber",
        "beauty",
        "spa"
      ]
    },
    {
      "soc": "41-1011.00",
      "title": "Retail Supervisors",
      "group": "Sales",
      "zone": 2,
      "dream": "Run the floor without a retail consultant",
      "middlemen": [
        "planogram vendors"
      ],
      "tasks": [
        "Staffing",
        "Stock",
        "Close"
      ],
      "skills": [
        "ops",
        "people"
      ],
      "division": "DreamSalesPro",
      "face": "operator",
      "hubQuery": "retail",
      "keywords": [
        "retail",
        "store",
        "shop"
      ]
    },
    {
      "soc": "41-2031.00",
      "title": "Retail Salespersons",
      "group": "Sales",
      "zone": 2,
      "dream": "Sell the thing you made",
      "middlemen": [
        "marketplace that buries you"
      ],
      "tasks": [
        "Pitch",
        "Stock",
        "Follow-up"
      ],
      "skills": [
        "service",
        "product"
      ],
      "division": "DreamSalesPro",
      "face": "agency",
      "hubQuery": "retail sales",
      "keywords": [
        "sell",
        "shopify",
        "storefront",
        "etsy"
      ]
    },
    {
      "soc": "41-3021.00",
      "title": "Insurance Sales Agents",
      "group": "Sales",
      "zone": 4,
      "dream": "Explain coverage without a lead mill",
      "middlemen": [
        "exclusive lead vendors"
      ],
      "tasks": [
        "Needs",
        "Compare",
        "Disclose"
      ],
      "skills": [
        "listening",
        "compliance"
      ],
      "division": "DreamFinance",
      "face": "safety",
      "hubQuery": "insurance",
      "keywords": [
        "insurance",
        "policy",
        "coverage"
      ]
    },
    {
      "soc": "41-3031.00",
      "title": "Securities and Commodities Sales",
      "group": "Sales",
      "zone": 4,
      "dream": "Explain a product with disclosures",
      "middlemen": [
        "boiler rooms"
      ],
      "tasks": [
        "Suitability",
        "Disclose",
        "Record"
      ],
      "skills": [
        "finance",
        "compliance"
      ],
      "division": "DreamFinance",
      "face": "safety",
      "hubQuery": "investing",
      "keywords": [
        "broker",
        "securities",
        "advisor"
      ]
    },
    {
      "soc": "41-3091.00",
      "title": "Sales Representatives of Services",
      "group": "Sales",
      "zone": 4,
      "dream": "Sell the service you deliver",
      "middlemen": [
        "lead-gen agencies"
      ],
      "tasks": [
        "Offer",
        "Demo",
        "Close"
      ],
      "skills": [
        "talk",
        "follow-up"
      ],
      "division": "DreamSalesPro",
      "face": "agency",
      "hubQuery": "b2b sales",
      "keywords": [
        "b2b",
        "services",
        "proposal",
        "demo"
      ]
    },
    {
      "soc": "41-4012.00",
      "title": "Sales Representatives, Wholesale",
      "group": "Sales",
      "zone": 4,
      "dream": "Move product without a broker stack",
      "middlemen": [
        "exclusive distributors you do not need"
      ],
      "tasks": [
        "Catalog",
        "Quote",
        "Fulfill"
      ],
      "skills": [
        "product",
        "negotiation"
      ],
      "division": "DreamSalesPro",
      "face": "business",
      "hubQuery": "wholesale",
      "keywords": [
        "wholesale",
        "b2b",
        "distributor"
      ]
    },
    {
      "soc": "43-3031.00",
      "title": "Bookkeeping Clerks",
      "group": "Office",
      "zone": 3,
      "dream": "Enter the books once, correctly",
      "middlemen": [
        "receipt-photo apps that charge forever"
      ],
      "tasks": [
        "Inbox",
        "Categorize",
        "Reconcile"
      ],
      "skills": [
        "accuracy",
        "software"
      ],
      "division": "DreamFinance",
      "face": "operator",
      "hubQuery": "bookkeeping",
      "keywords": [
        "invoices",
        "receipts",
        "quickbooks",
        "ledger"
      ]
    },
    {
      "soc": "43-4051.00",
      "title": "Customer Service Representatives",
      "group": "Office",
      "zone": 2,
      "dream": "Answer customers without a BPO",
      "middlemen": [
        "offshore CS mills"
      ],
      "tasks": [
        "Inbox",
        "Macros",
        "Escalate"
      ],
      "skills": [
        "writing",
        "calm"
      ],
      "division": "DreamAutomation",
      "face": "companion",
      "hubQuery": "customer support",
      "keywords": [
        "support",
        "helpdesk",
        "customer service",
        "inbox"
      ]
    },
    {
      "soc": "43-6011.00",
      "title": "Executive Secretaries",
      "group": "Office",
      "zone": 3,
      "dream": "Run the calendar without a VA farm",
      "middlemen": [
        "VA marketplaces"
      ],
      "tasks": [
        "Calendar",
        "Notes",
        "Follow-ups"
      ],
      "skills": [
        "organization",
        "writing"
      ],
      "division": "DreamAutomation",
      "face": "operator",
      "hubQuery": "executive assistant",
      "keywords": [
        "assistant",
        "calendar",
        "va",
        "admin"
      ]
    },
    {
      "soc": "47-1011.00",
      "title": "First-Line Supervisors of Construction",
      "group": "Construction",
      "zone": 3,
      "dream": "Coordinate the crew yourself",
      "middlemen": [
        "labor brokers"
      ],
      "tasks": [
        "Daily plan",
        "Safety",
        "Materials"
      ],
      "skills": [
        "leadership",
        "trades"
      ],
      "division": "DreamOps",
      "face": "operator",
      "hubQuery": "construction supervisor",
      "keywords": [
        "foreman",
        "crew",
        "jobsite"
      ]
    },
    {
      "soc": "47-2031.00",
      "title": "Carpenters",
      "group": "Construction",
      "zone": 2,
      "dream": "Price and do the work",
      "middlemen": [
        "lead apps that resell you"
      ],
      "tasks": [
        "Measure",
        "Cut list",
        "Install"
      ],
      "skills": [
        "craft",
        "math"
      ],
      "division": "DreamBizLaunch",
      "face": "builder",
      "hubQuery": "carpentry",
      "keywords": [
        "carpenter",
        "wood",
        "deck",
        "trim"
      ]
    },
    {
      "soc": "47-2111.00",
      "title": "Electricians",
      "group": "Construction",
      "zone": 3,
      "dream": "Plan the job to code",
      "middlemen": [
        "dispatch apps"
      ],
      "tasks": [
        "Load",
        "Materials",
        "Test"
      ],
      "skills": [
        "electrical",
        "safety"
      ],
      "division": "DreamBizLaunch",
      "face": "safety",
      "hubQuery": "electrician",
      "keywords": [
        "electrician",
        "wiring",
        "panel"
      ]
    },
    {
      "soc": "49-3023.00",
      "title": "Automotive Technicians",
      "group": "Installation",
      "zone": 3,
      "dream": "Diagnose without a dealer middle",
      "middlemen": [
        "dealer-only scan lock-in"
      ],
      "tasks": [
        "Diagnose",
        "Parts",
        "Verify"
      ],
      "skills": [
        "mechanical",
        "electronics"
      ],
      "division": "DreamOps",
      "face": "operator",
      "hubQuery": "automotive",
      "keywords": [
        "auto",
        "mechanic",
        "car repair"
      ]
    },
    {
      "soc": "51-1011.00",
      "title": "First-Line Supervisors of Production",
      "group": "Production",
      "zone": 3,
      "dream": "Run the line without a MES vendor you do not need",
      "middlemen": [
        "shop-floor software lock-in"
      ],
      "tasks": [
        "Schedule",
        "Quality",
        "Labor"
      ],
      "skills": [
        "ops",
        "quality"
      ],
      "division": "DreamOps",
      "face": "operator",
      "hubQuery": "manufacturing",
      "keywords": [
        "production",
        "factory",
        "manufacturing"
      ]
    },
    {
      "soc": "53-1047.00",
      "title": "First-Line Supervisors of Transportation",
      "group": "Transportation",
      "zone": 3,
      "dream": "Route work without a broker cut",
      "middlemen": [
        "load boards that own the margin"
      ],
      "tasks": [
        "Dispatch",
        "Hours",
        "Proof"
      ],
      "skills": [
        "logistics",
        "people"
      ],
      "division": "DreamOps",
      "face": "operator",
      "hubQuery": "logistics",
      "keywords": [
        "trucking",
        "dispatch",
        "delivery",
        "logistics"
      ]
    },
    {
      "soc": "11-9141.00",
      "title": "Property, Real Estate, and Community Managers",
      "group": "Management",
      "zone": 4,
      "dream": "Manage the property you own",
      "middlemen": [
        "property-management firms on simple stock"
      ],
      "tasks": [
        "Lease",
        "Maintenance",
        "Ledger"
      ],
      "skills": [
        "ops",
        "law-basics"
      ],
      "division": "DreamRealEstate",
      "face": "operator",
      "hubQuery": "property management",
      "keywords": [
        "rental",
        "property",
        "landlord",
        "lease",
        "airbnb"
      ]
    },
    {
      "soc": "41-9022.00",
      "title": "Real Estate Sales Agents",
      "group": "Sales",
      "zone": 3,
      "dream": "List and show without a desk that owns you",
      "middlemen": [
        "portal boosts",
        "desk splits you do not need"
      ],
      "tasks": [
        "CMA",
        "Listing",
        "Show"
      ],
      "skills": [
        "sales",
        "local"
      ],
      "division": "DreamRealEstate",
      "face": "agency",
      "hubQuery": "real estate",
      "keywords": [
        "realtor",
        "listing",
        "house",
        "mls"
      ]
    },
    {
      "soc": "13-1071.00",
      "title": "Human Resources Specialists",
      "group": "Business",
      "zone": 4,
      "dream": "Hire without a recruiter cut",
      "middlemen": [
        "recruiting agencies"
      ],
      "tasks": [
        "Score",
        "Interview",
        "Offer"
      ],
      "skills": [
        "people",
        "writing"
      ],
      "division": "DreamBizLaunch",
      "face": "operator",
      "hubQuery": "recruiting",
      "keywords": [
        "hire",
        "hiring",
        "recruiter",
        "hr",
        "job"
      ]
    },
    {
      "soc": "15-1299.08",
      "title": "Computer Systems Engineers / Architects",
      "group": "Computer",
      "zone": 4,
      "dream": "Design the stack you will run",
      "middlemen": [
        "cloud architects on retainer"
      ],
      "tasks": [
        "Diagram",
        "Cost",
        "Failure modes"
      ],
      "skills": [
        "architecture",
        "security"
      ],
      "division": "DreamAIInfra",
      "face": "foundry",
      "hubQuery": "systems architecture",
      "keywords": [
        "architecture",
        "cloud",
        "infra",
        "stack"
      ]
    },
    {
      "soc": "15-1221.00",
      "title": "Computer and Information Research Scientists",
      "group": "Computer",
      "zone": 5,
      "dream": "Study models without buying a fake checkpoint",
      "middlemen": [
        "weight resellers"
      ],
      "tasks": [
        "Paper",
        "Eval",
        "License"
      ],
      "skills": [
        "research",
        "math"
      ],
      "division": "DreamFoundry",
      "face": "foundry",
      "hubQuery": "machine learning",
      "keywords": [
        "research scientist",
        "papers",
        "benchmark",
        "weights"
      ]
    },
    {
      "soc": "27-1014.00",
      "title": "Special Effects Artists and Animators",
      "group": "Arts",
      "zone": 4,
      "dream": "Make the motion yourself",
      "middlemen": [
        "studio farm-outs"
      ],
      "tasks": [
        "Storyboard",
        "Animate",
        "Export"
      ],
      "skills": [
        "3d",
        "timing"
      ],
      "division": "GameTitan",
      "face": "builder",
      "hubQuery": "animation",
      "keywords": [
        "animation",
        "game",
        "vfx",
        "3d"
      ]
    },
    {
      "soc": "15-1299.09",
      "title": "Product Managers",
      "group": "Management",
      "zone": 4,
      "dream": "Ship the product without a product-agency",
      "middlemen": [
        "product consultancies"
      ],
      "tasks": [
        "Outcome",
        "Slice",
        "Evidence"
      ],
      "skills": [
        "prioritize",
        "write"
      ],
      "division": "DreamSaaS",
      "face": "operator",
      "hubQuery": "product management",
      "keywords": [
        "product",
        "roadmap",
        "mvp",
        "saas"
      ]
    },
    {
      "soc": "13-1082.00",
      "title": "Project Management Specialists",
      "group": "Business",
      "zone": 4,
      "dream": "Run the project without a PMO tax",
      "middlemen": [
        "PMO outsourcing"
      ],
      "tasks": [
        "Scope",
        "Risks",
        "Done"
      ],
      "skills": [
        "planning",
        "comms"
      ],
      "division": "DreamOps",
      "face": "operator",
      "hubQuery": "project management",
      "keywords": [
        "project",
        "deadline",
        "milestone",
        "gantt"
      ]
    },
    {
      "soc": "15-1253.00",
      "title": "Software Quality Assurance Analysts",
      "group": "Computer",
      "zone": 4,
      "dream": "Prove it works without a QA body shop",
      "middlemen": [
        "outsourced QA farms"
      ],
      "tasks": [
        "Cases",
        "Run",
        "Bug evidence"
      ],
      "skills": [
        "testing",
        "sql"
      ],
      "division": "DreamCodeLab",
      "face": "safety",
      "hubQuery": "software testing",
      "keywords": [
        "qa",
        "test",
        "quality",
        "regression"
      ]
    },
    {
      "soc": "27-3091.00",
      "title": "Interpreters and Translators",
      "group": "Arts",
      "zone": 4,
      "dream": "Move meaning without a language mill",
      "middlemen": [
        "agency per-word markups"
      ],
      "tasks": [
        "Source",
        "Draft",
        "Review"
      ],
      "skills": [
        "language",
        "domain"
      ],
      "division": "DreamGlobal",
      "face": "companion",
      "hubQuery": "translation",
      "keywords": [
        "translate",
        "language",
        "localize"
      ]
    },
    {
      "soc": "11-9199.01",
      "title": "Regulatory Affairs Managers",
      "group": "Management",
      "zone": 5,
      "dream": "Track the rule without a compliance theater firm",
      "middlemen": [
        "binder mills"
      ],
      "tasks": [
        "Map rule",
        "Evidence",
        "Gap"
      ],
      "skills": [
        "reading",
        "process"
      ],
      "division": "DreamLegal",
      "face": "safety",
      "hubQuery": "compliance",
      "keywords": [
        "compliance",
        "policy",
        "regulation",
        "license"
      ]
    },
    {
      "soc": "13-1199.04",
      "title": "Business Continuity Planners",
      "group": "Business",
      "zone": 4,
      "dream": "Recover without a DR vendor speech",
      "middlemen": [
        "continuity retainers"
      ],
      "tasks": [
        "Risks",
        "Runbook",
        "Test"
      ],
      "skills": [
        "planning",
        "comms"
      ],
      "division": "DreamOps",
      "face": "safety",
      "hubQuery": "business continuity",
      "keywords": [
        "continuity",
        "disaster",
        "backup",
        "recover"
      ]
    },
    {
      "soc": "15-1232.00",
      "title": "Computer User Support Specialists",
      "group": "Computer",
      "zone": 3,
      "dream": "Fix the machine without a helpdesk contract",
      "middlemen": [
        "break-fix retainers"
      ],
      "tasks": [
        "Reproduce",
        "Fix",
        "Note"
      ],
      "skills": [
        "troubleshooting",
        "docs"
      ],
      "division": "DreamOps",
      "face": "operator",
      "hubQuery": "it support",
      "keywords": [
        "it support",
        "helpdesk",
        "laptop",
        "wifi"
      ]
    },
    {
      "soc": "41-4011.00",
      "title": "Sales Engineers",
      "group": "Sales",
      "zone": 4,
      "dream": "Demo the real thing",
      "middlemen": [
        "slide-only SEs"
      ],
      "tasks": [
        "Discover",
        "Demo",
        "Proof"
      ],
      "skills": [
        "product",
        "talk"
      ],
      "division": "DreamSaaS",
      "face": "agency",
      "hubQuery": "sales engineer",
      "keywords": [
        "demo",
        "poc",
        "technical sales"
      ]
    },
    {
      "soc": "27-2012.05",
      "title": "Media Technical Directors",
      "group": "Arts",
      "zone": 4,
      "dream": "Run the stream yourself",
      "middlemen": [
        "full-service channel agencies"
      ],
      "tasks": [
        "Board",
        "Cues",
        "Archive"
      ],
      "skills": [
        "av",
        "ops"
      ],
      "division": "DreamStreaming",
      "face": "operator",
      "hubQuery": "live streaming",
      "keywords": [
        "stream",
        "obs",
        "live",
        "broadcast"
      ]
    },
    {
      "soc": "11-9111.00",
      "title": "Medical and Health Services Managers",
      "group": "Management",
      "zone": 5,
      "dream": "Run the practice admin, not medicine",
      "middlemen": [
        "RCM mills"
      ],
      "tasks": [
        "Schedule load",
        "Billing map",
        "Staffing"
      ],
      "skills": [
        "ops",
        "compliance"
      ],
      "division": "DreamHealth",
      "face": "operator",
      "hubQuery": "practice management",
      "keywords": [
        "practice",
        "clinic manager",
        "billing"
      ]
    },
    {
      "soc": "19-3022.00",
      "title": "Survey Researchers",
      "group": "Science",
      "zone": 5,
      "dream": "Ask real questions",
      "middlemen": [
        "survey-panel brokers"
      ],
      "tasks": [
        "Instrument",
        "Sample",
        "Uncertainty"
      ],
      "skills": [
        "stats",
        "writing"
      ],
      "division": "DreamData",
      "face": "researcher",
      "hubQuery": "survey research",
      "keywords": [
        "survey",
        "poll",
        "questionnaire"
      ]
    },
    {
      "soc": "25-1194.00",
      "title": "Career/Technical Education Teachers",
      "group": "Education",
      "zone": 4,
      "dream": "Train the skill that gets the job",
      "middlemen": [
        "bootcamp funnels"
      ],
      "tasks": [
        "Skill",
        "Drill",
        "Evidence"
      ],
      "skills": [
        "instruction",
        "trade"
      ],
      "division": "DreamEducation",
      "face": "teacher",
      "hubQuery": "vocational education",
      "keywords": [
        "bootcamp",
        "trade school",
        "apprentice",
        "skill"
      ]
    },
    {
      "soc": "13-2052.00",
      "title": "Personal Financial Advisors",
      "group": "Business",
      "zone": 4,
      "dream": "Plan money with disclosures, not a product mill",
      "middlemen": [
        "AUM-only shops for simple plans"
      ],
      "tasks": [
        "Goals",
        "Budget",
        "Risk"
      ],
      "skills": [
        "listening",
        "math"
      ],
      "division": "DreamFinance",
      "face": "teacher",
      "hubQuery": "personal finance",
      "keywords": [
        "money",
        "retire",
        "budget",
        "advisor"
      ]
    }
  ],
  "methods": [
    {
      "id": "sandbox-first",
      "group": "Sandbox",
      "name": "Sandbox first",
      "how": "Do the drill in a copy that cannot spend, send, or write production.",
      "sandbox": "A fixture, a fake inbox, a local file. Never the live system."
    },
    {
      "id": "fail-fixture",
      "group": "Sandbox",
      "name": "Failing fixture",
      "how": "Write the test that should fail before you study the happy path.",
      "sandbox": "Red test checked in. Green without a test is not a pass."
    },
    {
      "id": "holdout",
      "group": "Sandbox",
      "name": "Holdout set",
      "how": "Keep examples the teacher never saw. Native score stays native.",
      "sandbox": "Assisted score in a second column."
    },
    {
      "id": "replay",
      "group": "Sandbox",
      "name": "Replay the trace",
      "how": "Run the same tool calls again. If you cannot replay, you did not learn it.",
      "sandbox": "Saved trace, no network unless granted."
    },
    {
      "id": "blast-radius",
      "group": "Sandbox",
      "name": "Blast-radius card",
      "how": "Name what would break if this were live: mail, money, weights, secrets.",
      "sandbox": "Card must list the gate that stays shut."
    },
    {
      "id": "license-stop",
      "group": "Sandbox",
      "name": "License stop",
      "how": "Missing license ends the lesson. Do not load the dataset.",
      "sandbox": "Write the SPDX id or stop."
    },
    {
      "id": "one-tool",
      "group": "Sandbox",
      "name": "One tool, one grant",
      "how": "Agents get a single permissioned tool until the trace is clean.",
      "sandbox": "No silent second tool."
    },
    {
      "id": "money-off",
      "group": "Sandbox",
      "name": "Money off",
      "how": "Stripe, ads, and paid inference stay off until an owner gate.",
      "sandbox": "Test-mode or dry-run only."
    },
    {
      "id": "retrieval",
      "group": "Memory",
      "name": "Retrieval practice",
      "how": "Close the doc. Produce the answer. Then check.",
      "sandbox": "Blank page, then the source."
    },
    {
      "id": "spaced",
      "group": "Memory",
      "name": "Spaced recall",
      "how": "Same drill on day 1, 3, 7, 21. Forgetting is the point.",
      "sandbox": "Calendar the retest, not a binge."
    },
    {
      "id": "interleave",
      "group": "Memory",
      "name": "Interleaving",
      "how": "Mix NER, QA, and generate in one session so you learn to choose.",
      "sandbox": "Shuffled queue of three tasks."
    },
    {
      "id": "elaboration",
      "group": "Memory",
      "name": "Elaboration",
      "how": "Ask why this step exists, not only how.",
      "sandbox": "One why-note per procedure."
    },
    {
      "id": "dual-code",
      "group": "Memory",
      "name": "Dual coding",
      "how": "Same idea as a diagram and as a command. Both have to match.",
      "sandbox": "ASCII flow + the actual command."
    },
    {
      "id": "worked",
      "group": "Memory",
      "name": "Worked example fade",
      "how": "Study a full solution, then a partial, then a blank.",
      "sandbox": "Three versions of one problem."
    },
    {
      "id": "errorful",
      "group": "Memory",
      "name": "Errorful learning",
      "how": "Keep the miss. The miss is the curriculum.",
      "sandbox": "Error log with the corrected trace."
    },
    {
      "id": "generation",
      "group": "Memory",
      "name": "Generation effect",
      "how": "Write the summary before you read theirs.",
      "sandbox": "Your paragraph first, then the card."
    },
    {
      "id": "feynman",
      "group": "Perspective",
      "name": "Feynman pass",
      "how": "Teach it to a beginner in plain words. Jargon you cannot drop is a hole.",
      "sandbox": "One page, no vendor names until the end."
    },
    {
      "id": "contrast",
      "group": "Perspective",
      "name": "Contrast cases",
      "how": "Two near-miss examples. Name the one feature that changes the answer.",
      "sandbox": "A/B fixtures."
    },
    {
      "id": "five-houses",
      "group": "Perspective",
      "name": "Five-house view",
      "how": "Same topic from GitHub, Hugging Face, ChatGPT, Claude, Grok. Then Buddy.",
      "sandbox": "Five notes, then a synthesis card."
    },
    {
      "id": "steelman",
      "group": "Perspective",
      "name": "Steelman the other vendor",
      "how": "State their best argument before you reject it.",
      "sandbox": "Quoted claim + source URL."
    },
    {
      "id": "beginner-expert",
      "group": "Perspective",
      "name": "Beginner then expert",
      "how": "Do the tutorial path, then the failure-mode path.",
      "sandbox": "Two checklists."
    },
    {
      "id": "user-owner",
      "group": "Perspective",
      "name": "User vs owner",
      "how": "Learn as the person doing the job, then as the person who pays.",
      "sandbox": "Two outcome sentences."
    },
    {
      "id": "onet-lens",
      "group": "Perspective",
      "name": "O*NET lens",
      "how": "Map the skill to an occupation’s tasks, not a course outline.",
      "sandbox": "SOC code + three tasks."
    },
    {
      "id": "native-vs-wrapper",
      "group": "Perspective",
      "name": "Native vs wrapper",
      "how": "Can a free student do it. Grok only if the holdout fails.",
      "sandbox": "Two scores."
    },
    {
      "id": "pomodoro",
      "group": "Session",
      "name": "Tight session",
      "how": "45–90 minutes. One evidence object. Stop.",
      "sandbox": "Timer + one artifact."
    },
    {
      "id": "pretest",
      "group": "Session",
      "name": "Pretest",
      "how": "Guess first. Wrong guesses make the lesson stick.",
      "sandbox": "Dated pretest sheet."
    },
    {
      "id": "posttest",
      "group": "Session",
      "name": "Immediate posttest",
      "how": "Same items, no notes. That is the day’s score.",
      "sandbox": "Closed-book recap."
    },
    {
      "id": "sleep",
      "group": "Session",
      "name": "Sleep on it",
      "how": "Do not restudy the same night. Retest tomorrow.",
      "sandbox": "Next-day holdout."
    },
    {
      "id": "teach-back",
      "group": "Session",
      "name": "Teach-back",
      "how": "Buddy asks you to explain. You talk. It only checks the gates.",
      "sandbox": "Voice or typed teach-back."
    },
    {
      "id": "rubber",
      "group": "Session",
      "name": "Rubber duck the fail",
      "how": "Narrate the failing run before you patch.",
      "sandbox": "Comment on the red test."
    },
    {
      "id": "one-metric",
      "group": "Session",
      "name": "One metric",
      "how": "Pick accuracy, exact match, or replay. Not all three.",
      "sandbox": "Named metric in the card."
    },
    {
      "id": "time-box-search",
      "group": "Session",
      "name": "Time-box search",
      "how": "Ten minutes of docs. Then do. More reading is stalling.",
      "sandbox": "Clock the search."
    },
    {
      "id": "deliberate",
      "group": "Skill",
      "name": "Deliberate practice",
      "how": "The hard 20%, not the demo 80%.",
      "sandbox": "A drill that still fails."
    },
    {
      "id": "chunk",
      "group": "Skill",
      "name": "Chunking",
      "how": "Name the chunk: tokenize, train, eval. Master one.",
      "sandbox": "Chunk card."
    },
    {
      "id": "transfer",
      "group": "Skill",
      "name": "Near then far transfer",
      "how": "Same skill on a new dataset, then a new modality.",
      "sandbox": "Two transfer tasks."
    },
    {
      "id": "variation",
      "group": "Skill",
      "name": "Variation",
      "how": "Change one variable: model, data, or decode.",
      "sandbox": "Three runs, one axis."
    },
    {
      "id": "minimal",
      "group": "Skill",
      "name": "Minimal repro",
      "how": "Smallest example that still shows the bug or the skill.",
      "sandbox": "Under 50 lines or one clip."
    },
    {
      "id": "regression",
      "group": "Skill",
      "name": "Regression drill",
      "how": "Yesterday’s pass must still pass.",
      "sandbox": "Saved fixture re-run."
    },
    {
      "id": "socratic",
      "group": "Skill",
      "name": "Socratic gate",
      "how": "Buddy asks until you name the constraint. It does not lecture first.",
      "sandbox": "Question log."
    },
    {
      "id": "capstone",
      "group": "Skill",
      "name": "Capstone evidence",
      "how": "License, metric, fail, next drill. Missing any is not a pass.",
      "sandbox": "Capstone card."
    },
    {
      "id": "pair-free-paid",
      "group": "Routing",
      "name": "Free then paid",
      "how": "Local/open first. Paid teacher last, capped, user-started.",
      "sandbox": "Engine named on the card."
    },
    {
      "id": "unique-model",
      "group": "Routing",
      "name": "Unique model per step",
      "how": "Do not reuse the same student on two steps of one job.",
      "sandbox": "Model ids listed."
    },
    {
      "id": "cite",
      "group": "Routing",
      "name": "Cite the chunk",
      "how": "RAG without a citation is a refuse.",
      "sandbox": "Chunk id on the answer."
    },
    {
      "id": "refuse",
      "group": "Routing",
      "name": "Practice refuse",
      "how": "Learn when not to answer: medical diagnosis, live trade, stolen weights.",
      "sandbox": "Three refuse scripts."
    },
    {
      "id": "plugin-grant",
      "group": "Routing",
      "name": "Plugin is not installed",
      "how": "A named ChatGPT/Claude/Grok/GitHub plugin is a study target until granted.",
      "sandbox": "live=false until ping."
    },
    {
      "id": "mcp-trace",
      "group": "Routing",
      "name": "MCP with a trace",
      "how": "Every tool call logged. No MCP write in study mode.",
      "sandbox": "Read tools only."
    },
    {
      "id": "self-build",
      "group": "Routing",
      "name": "Self-build the lesson",
      "how": "After the five houses, write Buddy’s version: setup, catalog row, evidence.",
      "sandbox": "Original card in local catalog."
    },
    {
      "id": "self-fix",
      "group": "Routing",
      "name": "Self-fix the miss",
      "how": "A failed drill opens a recovery incident, not a skip.",
      "sandbox": "Incident id."
    }
  ],
  "perspectives": [
    {
      "id": "gh-mcp",
      "house": "github",
      "name": "GitHub MCP server",
      "kind": "MCP",
      "teaches": "Issues, PRs, Actions, code search as tools with a trace",
      "href": "https://docs.github.com/en/copilot/customizing-copilot/using-model-context-protocol",
      "live": false,
      "grant": "GitHub grant. Writes stay PR-gated."
    },
    {
      "id": "gh-registry",
      "house": "github",
      "name": "GitHub MCP Registry",
      "kind": "directory",
      "teaches": "Curated servers. Preview. Not every listing is trusted.",
      "href": "https://github.com/mcp",
      "live": false,
      "grant": "Install only reviewed servers."
    },
    {
      "id": "gh-copilot-plugins",
      "house": "github",
      "name": "Copilot plugins",
      "kind": "plugin",
      "teaches": "Official skills, hooks. App-based Copilot Extensions sunset Nov 2025.",
      "href": "https://github.com/github/copilot-plugins",
      "live": false,
      "grant": "Copilot policy on the org."
    },
    {
      "id": "gh-copilot-chat",
      "house": "github",
      "name": "Copilot Chat",
      "kind": "chat",
      "teaches": "Ask in the repo. Still not a substitute for tests.",
      "href": "https://docs.github.com/en/copilot",
      "live": false,
      "grant": "Copilot seat."
    },
    {
      "id": "gh-actions",
      "house": "github",
      "name": "GitHub Actions",
      "kind": "ci",
      "teaches": "Learn by the run: compile, soak, evidence artifacts",
      "href": "https://github.com/DreamCo-Technologies/Dreamcobots/actions",
      "live": true,
      "grant": "Public reads are live. Writes are not."
    },
    {
      "id": "gh-codespaces",
      "house": "github",
      "name": "Codespaces",
      "kind": "env",
      "teaches": "A disposable machine for the drill",
      "href": "https://docs.github.com/en/codespaces",
      "live": false,
      "grant": "Paid compute. Prefer local sandbox."
    },
    {
      "id": "gh-ghas",
      "house": "github",
      "name": "Advanced Security plugin",
      "kind": "plugin",
      "teaches": "Secret and dependency scans as a lesson in what leaked",
      "href": "https://docs.github.com/en/code-security",
      "live": false,
      "grant": "GHAS on the org."
    },
    {
      "id": "gh-cli",
      "house": "github",
      "name": "Copilot CLI / coding agent",
      "kind": "agent",
      "teaches": "Agent in the repo with MCP. Sandbox the branch.",
      "href": "https://docs.github.com/en/copilot",
      "live": false,
      "grant": "Never auto-merge main."
    },
    {
      "id": "hf-learn",
      "house": "huggingface",
      "name": "Hugging Face Learn",
      "kind": "course",
      "teaches": "Official courses: LLM, agents, audio, vision, RL, robotics",
      "href": "https://huggingface.co/learn",
      "live": true,
      "grant": "Public. Weights still licensed."
    },
    {
      "id": "hf-hub",
      "house": "huggingface",
      "name": "Hub cards",
      "kind": "catalog",
      "teaches": "License, pipeline, intended use before any download",
      "href": "https://huggingface.co",
      "live": true,
      "grant": "Public card search is live. No bulk steal."
    },
    {
      "id": "hf-spaces",
      "house": "huggingface",
      "name": "Spaces",
      "kind": "demo",
      "teaches": "Someone else’s demo. Reproduce locally before you trust it.",
      "href": "https://huggingface.co/spaces",
      "live": false,
      "grant": "GPU Spaces cost money."
    },
    {
      "id": "hf-providers",
      "house": "huggingface",
      "name": "Inference Providers",
      "kind": "api",
      "teaches": "PAYG tokens. Free credit is tiny.",
      "href": "https://huggingface.co/docs/inference-providers",
      "live": false,
      "grant": "Key + spend cap."
    },
    {
      "id": "oai-plugins",
      "house": "chatgpt",
      "name": "ChatGPT Plugins directory",
      "kind": "plugin",
      "teaches": "2026 plugins bundle skills + MCP. Old 2023 plugins are dead.",
      "href": "https://learn.chatgpt.com/docs/plugins",
      "live": false,
      "grant": "ChatGPT plan. Writes off by default."
    },
    {
      "id": "oai-apps",
      "house": "chatgpt",
      "name": "ChatGPT apps / connectors",
      "kind": "mcp",
      "teaches": "Gmail, Drive, GitHub, Slack as MCP apps. Search first.",
      "href": "https://help.openai.com/en/articles/12584461-developer-mode-and-full-mcp-connectors-in-chatgpt-beta",
      "live": false,
      "grant": "Connect. No send until a later approve."
    },
    {
      "id": "oai-gpts",
      "house": "chatgpt",
      "name": "Custom GPTs",
      "kind": "gpt",
      "teaches": "A wrapped prompt is not a specialist fleet.",
      "href": "https://chatgpt.com/gpts",
      "live": false,
      "grant": "Actions inside a GPT still need auth."
    },
    {
      "id": "oai-codex",
      "house": "chatgpt",
      "name": "Codex plugins",
      "kind": "plugin",
      "teaches": "Same plugin directory as ChatGPT for coding workflows",
      "href": "https://learn.chatgpt.com/docs/plugins",
      "live": false,
      "grant": "Codex / ChatGPT desktop."
    },
    {
      "id": "oai-data",
      "house": "chatgpt",
      "name": "Data analysis",
      "kind": "sandbox",
      "teaches": "Python in their sandbox. Export the notebook as evidence.",
      "href": "https://help.openai.com",
      "live": false,
      "grant": "Do not paste secrets."
    },
    {
      "id": "oai-canvas",
      "house": "chatgpt",
      "name": "Canvas",
      "kind": "editor",
      "teaches": "Draft in a side doc. Still not a repo.",
      "href": "https://help.openai.com",
      "live": false,
      "grant": "Copy out to git."
    },
    {
      "id": "oai-deep",
      "house": "chatgpt",
      "name": "Deep research",
      "kind": "research",
      "teaches": "Long browse. Cite. Do not treat as a holdout.",
      "href": "https://help.openai.com",
      "live": false,
      "grant": "Paid. Read-only on custom MCP."
    },
    {
      "id": "oai-devmode",
      "house": "chatgpt",
      "name": "Developer mode MCP",
      "kind": "mcp",
      "teaches": "Custom servers. Full write is Business/Enterprise.",
      "href": "https://help.openai.com/en/articles/12584461-developer-mode-and-full-mcp-connectors-in-chatgpt-beta",
      "live": false,
      "grant": "Workspace admin."
    },
    {
      "id": "cl-plugins",
      "house": "claude",
      "name": "Claude plugins",
      "kind": "plugin",
      "teaches": "Role packs: sales, legal, eng. Skills + connectors bundled.",
      "href": "https://support.claude.com/en/articles/13837440-use-plugins-in-claude",
      "live": false,
      "grant": "Paid Claude. Local MCP = your machine."
    },
    {
      "id": "cl-directory",
      "house": "claude",
      "name": "Claude connector directory",
      "kind": "mcp",
      "teaches": "Drive, Gmail, Calendar, Notion, Figma, Slack, Atlassian, 800+",
      "href": "https://claude.com/connectors",
      "live": false,
      "grant": "OAuth. Buddy’s grant desk is separate."
    },
    {
      "id": "cl-code",
      "house": "claude",
      "name": "Claude Code plugins",
      "kind": "plugin",
      "teaches": "MCP in the terminal. Official anthropics/claude-plugins-official",
      "href": "https://code.claude.com/docs/en/mcp",
      "live": false,
      "grant": "Local process. Trust the source."
    },
    {
      "id": "cl-artifacts",
      "house": "claude",
      "name": "Artifacts",
      "kind": "sandbox",
      "teaches": "A preview pane. Promote to git or it vanished.",
      "href": "https://support.claude.com",
      "live": false,
      "grant": "Copy out."
    },
    {
      "id": "cl-computer",
      "house": "claude",
      "name": "Computer use",
      "kind": "agent",
      "teaches": "Clicks a desktop. Highest blast radius. Sandbox VM only.",
      "href": "https://docs.anthropic.com",
      "live": false,
      "grant": "Never on the owner laptop first."
    },
    {
      "id": "cl-projects",
      "house": "claude",
      "name": "Projects",
      "kind": "memory",
      "teaches": "Pinned files. Not a licensed dataset.",
      "href": "https://support.claude.com",
      "live": false,
      "grant": "You uploaded it."
    },
    {
      "id": "cl-create",
      "house": "claude",
      "name": "Plugin Create",
      "kind": "plugin",
      "teaches": "Build a Claude plugin. Then port the skill into Buddy.",
      "href": "https://support.claude.com/en/articles/13837440-use-plugins-in-claude",
      "live": false,
      "grant": "Paid plan."
    },
    {
      "id": "grok-web",
      "house": "grok",
      "name": "Web Search",
      "kind": "tool",
      "teaches": "Live web as a teacher. Cite the page.",
      "href": "https://docs.x.ai",
      "live": true,
      "grant": "User-started Grok. Capped."
    },
    {
      "id": "grok-x",
      "house": "grok",
      "name": "X Search",
      "kind": "tool",
      "teaches": "Posts are not papers. Use for current claims only.",
      "href": "https://docs.x.ai",
      "live": true,
      "grant": "User-started."
    },
    {
      "id": "grok-code",
      "house": "grok",
      "name": "Code execution",
      "kind": "sandbox",
      "teaches": "Python on xAI’s sandbox. Good for a drill, not production.",
      "href": "https://docs.x.ai",
      "live": false,
      "grant": "API tool. No secrets in the snippet."
    },
    {
      "id": "grok-fn",
      "house": "grok",
      "name": "Function calling",
      "kind": "tools",
      "teaches": "Your functions. Disabled by default for a reason.",
      "href": "https://docs.x.ai",
      "live": false,
      "grant": "Owner-defined tools only."
    },
    {
      "id": "grok-img",
      "house": "grok",
      "name": "Image generation",
      "kind": "tool",
      "teaches": "User-started images. Not a scraped Hub dump.",
      "href": "https://docs.x.ai",
      "live": false,
      "grant": "You click generate."
    },
    {
      "id": "grok-collections",
      "house": "grok",
      "name": "Collections search",
      "kind": "rag",
      "teaches": "Search files you gave Grok. Cite the file.",
      "href": "https://docs.x.ai",
      "live": false,
      "grant": "You uploaded it."
    },
    {
      "id": "grok-connectors",
      "house": "grok",
      "name": "Grok connectors",
      "kind": "mcp",
      "teaches": "SharePoint, Outlook, Drive, Notion, GitHub, Linear, custom MCP",
      "href": "https://docs.x.ai",
      "live": false,
      "grant": "Connect desk. Mail read-first."
    },
    {
      "id": "grok-build",
      "house": "grok",
      "name": "Grok Build plugins",
      "kind": "plugin",
      "teaches": "Builder marketplace: MongoDB, Vercel, Sentry, Chrome DevTools, Cloudflare",
      "href": "https://docs.x.ai",
      "live": false,
      "grant": "Named, not installed here."
    },
    {
      "id": "grok-teacher",
      "house": "grok",
      "name": "Grok teacher",
      "kind": "model",
      "teaches": "Hard jobs only. Unique paid step. Free students first.",
      "href": "https://docs.x.ai",
      "live": true,
      "grant": "XAI_API_KEY on the server. You start it."
    },
    {
      "id": "buddy-faces",
      "house": "buddy",
      "name": "Sixteen faces",
      "kind": "original",
      "teaches": "One personality, many surfaces. Not sixteen products.",
      "href": "/faces",
      "live": true,
      "grant": "Already here."
    },
    {
      "id": "buddy-goals",
      "house": "buddy",
      "name": "O*NET goals",
      "kind": "original",
      "teaches": "Work first, course second. Cut middlemen.",
      "href": "/goals",
      "live": true,
      "grant": "Already here."
    },
    {
      "id": "buddy-actions",
      "house": "buddy",
      "name": "Actions evidence",
      "kind": "original",
      "teaches": "Learn from real workflow runs, not a green badge.",
      "href": "/actions",
      "live": true,
      "grant": "Public GitHub."
    },
    {
      "id": "buddy-recover",
      "house": "buddy",
      "name": "Recovery lanes",
      "kind": "original",
      "teaches": "A miss becomes an incident, not a skip.",
      "href": "/recover",
      "live": true,
      "grant": "Already here."
    }
  ],
  "originals": [
    {
      "id": "engine-order",
      "name": "Engine order",
      "setup": "Existing Buddy skill → local/open student → free quota → paid Grok last.",
      "catalog": "Every step names the engine. Unique model per step."
    },
    {
      "id": "sandbox-contract",
      "name": "Sandbox contract",
      "setup": "No spend, no send, no production write, no weight steal.",
      "catalog": "Blast-radius card before the drill."
    },
    {
      "id": "evidence-card",
      "name": "Evidence card",
      "setup": "License, metric, fail, next drill.",
      "catalog": "Missing any field = not a pass."
    },
    {
      "id": "native-column",
      "name": "Native column",
      "setup": "Holdout without Grok. Assisted in a second column.",
      "catalog": "Never promote on assisted-only."
    },
    {
      "id": "five-house",
      "name": "Five-house synthesis",
      "setup": "GitHub, Hugging Face, ChatGPT, Claude, Grok notes, then Buddy original.",
      "catalog": "Original is the sixth row, not a copy."
    },
    {
      "id": "plugin-honesty",
      "name": "Plugin honesty",
      "setup": "Named plugins stay named until granted and pinged.",
      "catalog": "live=false is allowed. Fake-installed is not."
    },
    {
      "id": "occupation-first",
      "name": "Occupation first",
      "setup": "O*NET task, then the course that serves it.",
      "catalog": "SOC + three tasks on the lesson."
    },
    {
      "id": "self-build-lesson",
      "name": "Self-build lesson",
      "setup": "After study, write Buddy’s own setup: files, gates, specialist.",
      "catalog": "Row in this device catalog."
    },
    {
      "id": "self-fix-lesson",
      "name": "Self-fix lesson",
      "setup": "Failed evidence opens recover, not a skip button.",
      "catalog": "Incident id on the card."
    },
    {
      "id": "pages-vs-hosted",
      "name": "Pages vs hosted",
      "setup": "Original chrome on GitHub Pages. Live teachers only on hosted.",
      "catalog": "Keys never on Pages."
    }
  ],
  "sources": [
    {
      "id": "onet",
      "name": "O*NET",
      "href": "https://www.onetcenter.org",
      "use": "Occupations, tasks, skills, job zones",
      "hook": "catalog",
      "live": true,
      "how": "Local O*NET-SOC catalog maps a goal to work. Web Services stay optional."
    },
    {
      "id": "huggingface",
      "name": "Hugging Face Hub",
      "href": "https://huggingface.co",
      "use": "Model cards, licenses, pipelines",
      "hook": "api",
      "live": true,
      "how": "Public Hub search for cards and licenses. No bulk weight download."
    },
    {
      "id": "hf-transformers",
      "name": "Transformers",
      "href": "https://huggingface.co/docs/transformers",
      "use": "Model APIs",
      "hook": "docs",
      "live": false,
      "how": "Study docs. Runtime weights only after a license pin."
    },
    {
      "id": "hf-peft",
      "name": "PEFT",
      "href": "https://huggingface.co/docs/peft",
      "use": "LoRA / QLoRA recipes",
      "hook": "docs",
      "live": false,
      "how": "Recipes, not stolen adapters."
    },
    {
      "id": "hf-trl",
      "name": "TRL",
      "href": "https://huggingface.co/docs/trl",
      "use": "Alignment recipes",
      "hook": "docs",
      "live": false,
      "how": "DPO / ORPO study. No fake trained Buddy weights."
    },
    {
      "id": "hf-datasets",
      "name": "Datasets",
      "href": "https://huggingface.co/docs/datasets",
      "use": "Licensed data loads",
      "hook": "api",
      "live": true,
      "how": "Public Hub dataset cards: task, SPDX, size, files by name. No parquet scrape."
    },
    {
      "id": "github",
      "name": "GitHub Actions",
      "href": "https://github.com/DreamCo-Technologies/Dreamcobots/actions",
      "use": "Workflow health",
      "hook": "api",
      "live": true,
      "how": "Public REST is blocked from Pages. Cached website/data JSON is the live record here."
    },
    {
      "id": "github-repo",
      "name": "Dreamcobots repository",
      "href": "https://github.com/DreamCo-Technologies/Dreamcobots",
      "use": "Bots, desks, evidence",
      "hook": "api",
      "live": true,
      "how": "Public repo is the system of record. Writes stay PR-gated."
    },
    {
      "id": "xai",
      "name": "xAI / Grok",
      "href": "https://docs.x.ai",
      "use": "Paid teacher",
      "hook": "api",
      "live": false,
      "how": "Server-only XAI_API_KEY on the hosted app. Never on Pages."
    },
    {
      "id": "openai",
      "name": "OpenAI",
      "href": "https://platform.openai.com/docs",
      "use": "Named paid wrapper",
      "hook": "api",
      "live": false,
      "how": "OPENAI_API_KEY on the server. Never on Pages."
    },
    {
      "id": "anthropic",
      "name": "Anthropic Claude",
      "href": "https://docs.anthropic.com",
      "use": "Named paid wrapper",
      "hook": "api",
      "live": false,
      "how": "ANTHROPIC_API_KEY. Not saved. Never on Pages."
    },
    {
      "id": "vllm",
      "name": "vLLM",
      "href": "https://docs.vllm.ai",
      "use": "Serve students",
      "hook": "docs",
      "live": false,
      "how": "Local serve plan. Not claimed running."
    },
    {
      "id": "llamacpp",
      "name": "llama.cpp / GGUF",
      "href": "https://github.com/ggml-org/llama.cpp",
      "use": "Local edge",
      "hook": "docs",
      "live": false,
      "how": "Edge students. Install on the owner device."
    },
    {
      "id": "ollama",
      "name": "Ollama",
      "href": "https://ollama.com",
      "use": "Local wrappers",
      "hook": "docs",
      "live": false,
      "how": "Local-first. No account."
    },
    {
      "id": "olmo",
      "name": "OLMo / AllenAI",
      "href": "https://allenai.org/olmo",
      "use": "US open stack",
      "hook": "docs",
      "live": false,
      "how": "Open weights study. Cards, not claimed checkpoints."
    },
    {
      "id": "eleuther",
      "name": "Eleuther harness",
      "href": "https://github.com/EleutherAI/lm-evaluation-harness",
      "use": "Local evals",
      "hook": "docs",
      "live": false,
      "how": "Native scores stay native."
    },
    {
      "id": "helm",
      "name": "HELM",
      "href": "https://crfm.stanford.edu/helm/",
      "use": "Holistic eval",
      "hook": "docs",
      "live": false,
      "how": "Compare with cited numbers only."
    },
    {
      "id": "spdx",
      "name": "SPDX",
      "href": "https://spdx.dev",
      "use": "License pins",
      "hook": "catalog",
      "live": true,
      "how": "Every Hub card must show a license or stay blocked."
    },
    {
      "id": "stripe",
      "name": "Stripe",
      "href": "https://docs.stripe.com",
      "use": "Checkout contracts",
      "hook": "gated",
      "live": false,
      "how": "Test-mode docs only. Live charges stay off."
    },
    {
      "id": "gmail",
      "name": "Gmail",
      "href": "https://developers.google.com/gmail",
      "use": "Mail after grant",
      "hook": "grant",
      "live": false,
      "how": "Grok gate. Read first. No send until a later approve."
    }
  ],
  "mcp": [
    {
      "name": "buddy.plan",
      "channel": "device",
      "live": true,
      "desc": "O*NET goal plan on this device."
    },
    {
      "name": "buddy.operator",
      "channel": "device",
      "live": true,
      "desc": "Local operator evidence job."
    },
    {
      "name": "buddy.notify",
      "channel": "device",
      "live": true,
      "desc": "Ping this device when a task ends."
    },
    {
      "name": "buddy.download",
      "channel": "device",
      "live": true,
      "desc": "Save evidence JSON on this device."
    },
    {
      "name": "buddy.hub.search",
      "channel": "internet",
      "live": true,
      "desc": "Public Hub cards. No weights."
    },
    {
      "name": "buddy.hub.study",
      "channel": "internet",
      "live": true,
      "desc": "One dataset card + license gate."
    },
    {
      "name": "buddy.github.actions",
      "channel": "internet",
      "live": true,
      "desc": "Cached Actions health JSON on Pages."
    },
    {
      "name": "buddy.github.repo",
      "channel": "internet",
      "live": true,
      "desc": "Public repo link. Live REST is CORS-blocked here."
    },
    {
      "name": "buddy.web.get",
      "channel": "internet",
      "live": true,
      "desc": "GET an allowlisted public URL if CORS allows."
    },
    {
      "name": "buddy.teacher.ask",
      "channel": "api",
      "live": false,
      "desc": "Grok teacher. Blocked on Pages. No keys here."
    },
    {
      "name": "buddy.mcp.list",
      "channel": "mcp",
      "live": true,
      "desc": "Tools Buddy can invoke now."
    }
  ],
  "syscalls": [
    {
      "id": "doctor",
      "title": "Doctor",
      "how": "Inspect catalogs, gates, this browser.",
      "twin": "Refresh GitHub runs"
    },
    {
      "id": "test",
      "title": "Tests",
      "how": "Occupation match + catalog fills.",
      "twin": "CI test workflows"
    },
    {
      "id": "lint",
      "title": "Lint",
      "how": "Catalog shape checks.",
      "twin": "Lint workflows"
    },
    {
      "id": "security",
      "title": "Security",
      "how": "No keys in storage. Money off.",
      "twin": "Security / GHAS workflows"
    },
    {
      "id": "benchmark",
      "title": "Benchmark",
      "how": "Counts, not fake scores.",
      "twin": "Benchmark tracker"
    },
    {
      "id": "repair",
      "title": "Repair",
      "how": "Recovery lanes. No auto-merge.",
      "twin": "Recovery / keep-green"
    },
    {
      "id": "pages",
      "title": "Pages",
      "how": "Desk inventory. Keys never on Pages.",
      "twin": "Pages deploy"
    },
    {
      "id": "bundle",
      "title": "Bundle",
      "how": "In-browser OS bundle.",
      "twin": "Release artifacts"
    },
    {
      "id": "datasets",
      "title": "Datasets",
      "how": "Indexed Hub cards. No parquet.",
      "twin": "Hugging Face Hub cards"
    },
    {
      "id": "resources",
      "title": "Resources",
      "how": "Sources and desks as processes.",
      "twin": "Repo sources and desks"
    },
    {
      "id": "hunt",
      "title": "Hunt next",
      "how": "After mastery, find the next resource.",
      "twin": "New workflows / Hub cards"
    },
    {
      "id": "tasks",
      "title": "Tasks",
      "how": "Watch / screen-off runner.",
      "twin": "Watch / screen-off runner"
    }
  ],
  "paths": [
    {
      "id": "map",
      "name": "Hub map, not a binge",
      "vsHub": "Docs, cards, Spaces, papers, and pricing live on different sites.",
      "buddy": "One day: license, card, money gate, then stop.",
      "href": "https://huggingface.co/docs/hub/model-cards",
      "steps": [
        "Pretest: what is a model card vs a dataset card.",
        "Pin three Apache-2.0 cards. Refuse unspecified.",
        "Write the money gate: Hub search is free. Providers and Endpoints are not.",
        "Feynman: explain gated weights to a beginner."
      ]
    },
    {
      "id": "classify",
      "name": "Classifier in one sitting",
      "vsHub": "Task page, Datasets, Trainer, and Evaluate are four lessons.",
      "buddy": "License → eight cards → tiny pipeline → holdout → card.",
      "href": "https://huggingface.co/tasks/text-classification",
      "steps": [
        "Pick one licensed text-classification dataset from the sweep.",
        "Run or write a pipeline() call on a tiny model. CPU is allowed.",
        "Five examples including one miss. The miss is the lesson.",
        "Native metric on a holdout. Assisted score in a second column."
      ]
    },
    {
      "id": "lora",
      "name": "LoRA a student, not a 70B",
      "vsHub": "PEFT, bitsandbytes, Accelerate, and Trainer are separate books.",
      "buddy": "One adapter file. Size vs full checkpoint. Re-run eval tomorrow.",
      "href": "https://huggingface.co/docs/peft",
      "steps": [
        "Name adapter vs full weight. Write the size reason.",
        "Choose 4-bit, GGUF, or CPU. Missing VRAM is not a fail.",
        "Train a toy adapter on licensed rows only.",
        "Draft the card: license, intended use, out of scope."
      ]
    },
    {
      "id": "align",
      "name": "Generate, retrieve, or prefer",
      "vsHub": "Chat templates, SFT, DPO, RAG, and agents are five courses.",
      "buddy": "Pick one: decode, SFT, RAG-with-cite, or one-tool agent.",
      "href": "https://huggingface.co/docs/trl",
      "steps": [
        "Two decodes of the same prompt with settings named.",
        "Or SFT on a tiny licensed instruction set. No scraped chats.",
        "Or RAG: query + cited chunk + a refuse.",
        "Or one tool, one grant, a trace with no live side effect."
      ]
    },
    {
      "id": "senses",
      "name": "Audio and vision you have rights to",
      "vsHub": "Audio Course, Vision Course, and Diffusers are three weeks.",
      "buddy": "One clip or photo you own. Optional generate if you have compute.",
      "href": "https://huggingface.co/learn/audio-course",
      "steps": [
        "ASR or classify a clip/image you have rights to.",
        "Write source + one error. A demo GIF is not a pass.",
        "Skim the other modality. Depth beats tourism.",
        "Diffusers: pipeline name + license. Image optional."
      ]
    },
    {
      "id": "serve",
      "name": "Export and serve on this machine",
      "vsHub": "TGI, vLLM, GGUF, ONNX, Jobs, and LeRobot are six products.",
      "buddy": "One serve path this laptop can run. The others stay blocked with a reason.",
      "href": "https://huggingface.co/docs/hub/gguf",
      "steps": [
        "Choose GGUF, ONNX, or a local pipeline. Write why the others are blocked.",
        "Sweep tabular / multimodal / robotics cards. Index licenses only.",
        "Hub Jobs and Endpoints: paid. Do not start them from study.",
        "Robotics: grant-first. No device takeover story."
      ]
    },
    {
      "id": "capstone",
      "name": "Buddy’s easier path, evidenced",
      "vsHub": "Hugging Face is the library. It is not a certificate.",
      "buddy": "One track, one card: sources, license, metric, fail, next drill.",
      "href": "https://huggingface.co/learn/llm-course",
      "steps": [
        "Closed-book posttest from days 1–6. No notes.",
        "Pick NLP, train, generate, senses, or serve.",
        "Capstone card with license + metric + fail + next drill.",
        "Missing any field is not a pass. Weights still unhashed until you train."
      ]
    }
  ],
  "week": [
    {
      "day": 1,
      "title": "Map the Hub",
      "hours": "3 hr",
      "thesis": "Master the map: cards, licenses, Spaces, papers, money. Do not binge models.",
      "pathId": "map",
      "pretest": "What is the difference between a model card, a dataset card, and a Space?",
      "posttest": "Name three licenses you would index and one you would refuse. Why.",
      "evidence": "Three card URLs + licenses, one refuse, one money-gate paragraph.",
      "taskIds": [],
      "drills": [
        {
          "id": "d1-pre",
          "name": "Pretest first",
          "how": "Answer the pretest in your own words before opening docs."
        },
        {
          "id": "d1-cards",
          "name": "Three Apache cards",
          "how": "Pin three Apache-2.0 or MIT model cards. Skip gated."
        },
        {
          "id": "d1-refuse",
          "name": "Refuse unspecified",
          "how": "Find one dataset with no SPDX. Do not index it."
        },
        {
          "id": "d1-money",
          "name": "Money gate",
          "how": "Write: Hub search $0. Providers credit. Endpoints hourly."
        },
        {
          "id": "d1-feynman",
          "name": "Teach gated weights",
          "how": "One paragraph, no vendor slogans."
        }
      ]
    },
    {
      "day": 2,
      "title": "Language stack",
      "hours": "3.5 hr",
      "thesis": "Every NLP dataset task in one interleaved sitting. Then one classifier path.",
      "pathId": "classify",
      "pretest": "Extractive QA vs classification vs generation — which needs a span in the source?",
      "posttest": "Pick one task. Name license, split, and one miss.",
      "evidence": "Dataset id + SPDX + token counts + one miss.",
      "taskIds": [
        "text-classification",
        "token-classification",
        "question-answering",
        "table-question-answering",
        "zero-shot-classification",
        "translation",
        "summarization",
        "feature-extraction",
        "fill-mask",
        "sentence-similarity",
        "multiple-choice",
        "text-ranking",
        "text-retrieval",
        "tabular-to-text",
        "table-to-text"
      ],
      "drills": [
        {
          "id": "d2-sweep",
          "name": "Live language sweep",
          "how": "Run the Hub sweep. Read licenses. Do not download parquet."
        },
        {
          "id": "d2-tok",
          "name": "Two tokenizers",
          "how": "Same sentence, two tokenizers, two counts."
        },
        {
          "id": "d2-pipe",
          "name": "Tiny pipeline",
          "how": "One classification or QA pipeline id written down."
        },
        {
          "id": "d2-miss",
          "name": "Keep a miss",
          "how": "Five examples, one wrong. That miss is the curriculum."
        },
        {
          "id": "d2-holdout",
          "name": "Holdout column",
          "how": "Native score separate from any teacher."
        }
      ]
    },
    {
      "day": 3,
      "title": "Train a student",
      "hours": "3.5 hr",
      "thesis": "LoRA / QLoRA / Trainer as one recipe. A 70B download is stalling.",
      "pathId": "lora",
      "pretest": "Why is an adapter smaller than a full checkpoint?",
      "posttest": "Adapter vs full vs GGUF — which fits this machine, and why.",
      "evidence": "Chosen quant + metric + card draft. Re-run tomorrow.",
      "taskIds": [
        "text-generation"
      ],
      "drills": [
        {
          "id": "d3-size",
          "name": "Size comparison",
          "how": "Adapter vs full weight, numbers or a cited card."
        },
        {
          "id": "d3-quant",
          "name": "Pick a quant",
          "how": "4-bit, GGUF, or CPU. Name the blocker for the others."
        },
        {
          "id": "d3-toy",
          "name": "Toy train",
          "how": "Trainer or PEFT on licensed toy rows. CPU allowed."
        },
        {
          "id": "d3-metric",
          "name": "One metric",
          "how": "Accuracy, F1, or exact match. Not all three."
        },
        {
          "id": "d3-card",
          "name": "Card draft",
          "how": "License, intended use, out of scope."
        }
      ]
    },
    {
      "day": 4,
      "title": "Generate, retrieve, align",
      "hours": "3.5 hr",
      "thesis": "Chat, SFT, DPO, RAG, agents — pick one Buddy path and finish it.",
      "pathId": "align",
      "pretest": "When must you refuse instead of generate?",
      "posttest": "Show a cite or a refuse. A fluent paragraph without either is a fail.",
      "evidence": "Decode pair or SFT sample or cited chunk or tool trace.",
      "taskIds": [
        "text-generation",
        "text-ranking",
        "text-retrieval",
        "reinforcement-learning"
      ],
      "drills": [
        {
          "id": "d4-decode",
          "name": "Two decodes",
          "how": "Same prompt, two settings, both named."
        },
        {
          "id": "d4-rights",
          "name": "Rights to instruct",
          "how": "If you SFT, the dataset license is on the card."
        },
        {
          "id": "d4-cite",
          "name": "Cite or refuse",
          "how": "RAG chunk id, or a written refuse."
        },
        {
          "id": "d4-tool",
          "name": "One tool",
          "how": "Trace with no mail, money, or production write."
        },
        {
          "id": "d4-contrast",
          "name": "Contrast case",
          "how": "SFT vs DPO in one sentence each. Do not claim RLHF you did not run."
        }
      ]
    },
    {
      "day": 5,
      "title": "Senses: audio, vision, diffusion",
      "hours": "3.5 hr",
      "thesis": "One owned clip or photo. Optional generate. Skim the rest.",
      "pathId": "senses",
      "pretest": "What consent do you need for a voice or a face in a dataset?",
      "posttest": "Source of your clip/image + one error + the modality you only skimmed.",
      "evidence": "Media source + miss + skim note + pipeline license.",
      "taskIds": [
        "text-to-speech",
        "automatic-speech-recognition",
        "image-classification",
        "text-to-image",
        "visual-question-answering"
      ],
      "drills": [
        {
          "id": "d5-sweep",
          "name": "Senses sweep",
          "how": "Live Hub cards for audio and vision tasks. Licenses first."
        },
        {
          "id": "d5-own",
          "name": "Owned media",
          "how": "One clip or photo you have rights to. No scraped faces."
        },
        {
          "id": "d5-error",
          "name": "One error",
          "how": "WER, wrong label, or a qualitative miss."
        },
        {
          "id": "d5-skim",
          "name": "Skim the rest",
          "how": "Name the modality you did not go deep on, and why."
        },
        {
          "id": "d5-diff",
          "name": "Diffusers card",
          "how": "Pipeline + license. Generated file optional."
        }
      ]
    },
    {
      "day": 6,
      "title": "Tables, robots, export, serve",
      "hours": "3 hr",
      "thesis": "Finish the map: tabular, multimodal, RL, robotics, then one local serve path.",
      "pathId": "serve",
      "pretest": "Which serve path can this laptop run without a paid GPU?",
      "posttest": "Chosen serve path + blocked reasons + one robotics/tabular license.",
      "evidence": "Serve choice + two blocked reasons + one robotics/tabular license.",
      "taskIds": [
        "tabular-classification",
        "reinforcement-learning",
        "robotics",
        "any-to-any"
      ],
      "drills": [
        {
          "id": "d6-sweep",
          "name": "Rest-of-Hub sweep",
          "how": "Tabular, multimodal, RL, robotics cards. Index SPDX only."
        },
        {
          "id": "d6-serve",
          "name": "One serve path",
          "how": "GGUF, ONNX, or local pipeline. Others blocked with a reason."
        },
        {
          "id": "d6-paid",
          "name": "Paid stays off",
          "how": "Jobs and Endpoints named as paid. Not started."
        },
        {
          "id": "d6-robot",
          "name": "Grant-first robots",
          "how": "LeRobot is study. Devices stay paired, never taken over."
        },
        {
          "id": "d6-blast",
          "name": "Blast radius",
          "how": "What would break if this were live: weights, money, devices."
        }
      ]
    },
    {
      "day": 7,
      "title": "Holdout and easier path",
      "hours": "3 hr",
      "thesis": "Closed-book recall. Then write Buddy’s version of building a model.",
      "pathId": "capstone",
      "pretest": "Without notes: license rule, LoRA vs full, cite-or-refuse, money gate.",
      "posttest": "Capstone card. Missing license, metric, fail, or next drill is not a pass.",
      "evidence": "Capstone card with four fields + teach-back paragraph.",
      "taskIds": [],
      "drills": [
        {
          "id": "d7-closed",
          "name": "Closed-book",
          "how": "Answer the pretest from memory. Then check days 1–6."
        },
        {
          "id": "d7-teach",
          "name": "Teach-back",
          "how": "Explain the easier path for one track in plain words."
        },
        {
          "id": "d7-card",
          "name": "Capstone card",
          "how": "Sources, license, metric, fail, next drill."
        },
        {
          "id": "d7-honest",
          "name": "Honest weights",
          "how": "trained_weights_exist stays false until hashes land."
        },
        {
          "id": "d7-next",
          "name": "Next drill",
          "how": "The 30-day month is depth. This week was the map."
        }
      ]
    }
  ],
  "compare": [
    {
      "need": "Work / occupations",
      "hf": "No native SOC catalog",
      "buddy": "O*NET-aligned occupations",
      "other": "onetonline.org"
    },
    {
      "need": "Dataset cards",
      "hf": "Live Hub datasets API",
      "buddy": "Study + index, never bulk download",
      "other": "License first"
    },
    {
      "need": "Model cards",
      "hf": "Live Hub models API",
      "buddy": "Pin after SPDX",
      "other": "Foundry students named, untrained"
    },
    {
      "need": "Eval sets",
      "hf": "MMLU, GSM8K, SQuAD cards",
      "buddy": "buddy-eval package",
      "other": "Native holdout ≠ assisted score"
    },
    {
      "need": "Instruction rows",
      "hf": "Ultrachat-class, gated often",
      "buddy": "Do not scrape chats",
      "other": "Your traces stay local"
    },
    {
      "need": "Workflows",
      "hf": "None",
      "buddy": "Actions health + OS syscalls",
      "other": "GitHub Actions"
    },
    {
      "need": "Chat teacher",
      "hf": "Inference Providers, paid",
      "buddy": "Grok, hosted only",
      "other": "OpenAI / Claude named, not installed"
    },
    {
      "need": "Spaces / demos",
      "hf": "Gradio Spaces",
      "buddy": "Desks",
      "other": "GitHub Pages chrome"
    },
    {
      "need": "Robot / device data",
      "hf": "LeRobot datasets",
      "buddy": "Grant-first pairing",
      "other": "No Wi-Fi takeover"
    },
    {
      "need": "Our weights",
      "hf": "Not on the Hub yet",
      "buddy": "DreamFoundry tracks, hashes missing",
      "other": "trained_weights_exist: false"
    }
  ],
  "recovery": [
    {
      "id": "detect",
      "name": "Detect",
      "job": "Observe the repo, fingerprint failures, refuse fake-green.",
      "auto": "Read-only scans.",
      "gated": "Opening repair PRs.",
      "forbidden": "Rewriting old failed Actions to green."
    },
    {
      "id": "branch",
      "name": "Branch",
      "job": "Score every branch: freshness, required Buddy files, mergeability.",
      "auto": "Daily inventory.",
      "gated": "Resolution PRs from the conflict team.",
      "forbidden": "Force-merge to main."
    },
    {
      "id": "pr",
      "name": "Pull requests",
      "job": "Replay clean diffs onto current main. Leave conflicts visible.",
      "auto": "Queue + replacement PR when the net diff applies.",
      "gated": "Any merge. CI still required.",
      "forbidden": "Silent discard of conflicting changes."
    },
    {
      "id": "actions",
      "name": "Actions / CI",
      "job": "Replay only relevant failed jobs. Classify flaky vs deterministic.",
      "auto": "Fingerprint and bounded retry.",
      "gated": "Workflow edits.",
      "forbidden": "Weakening tests to obtain a pass."
    },
    {
      "id": "pages",
      "name": "Pages / original site",
      "job": "Keep buddy.html as home. Overlay website/ after Jekyll.",
      "auto": "File presence checks.",
      "gated": "Changing Pages source or deleting desks.",
      "forbidden": "Replacing original chat with a second home."
    },
    {
      "id": "runtime",
      "name": "Buddy runtime",
      "job": "Chat, unique-model routing, local planner if the teacher misses.",
      "auto": "Fall back to free students.",
      "gated": "Paid Grok send, device bridge.",
      "forbidden": "Claiming trained frontier weights."
    },
    {
      "id": "catalog",
      "name": "Catalog / evidence",
      "job": "JSON contracts. Missing harness stays blocked.",
      "auto": "Parse catalogs. Mark stale.",
      "gated": "Promoting a catalog row to live-connected.",
      "forbidden": "Counting yellow as green."
    },
    {
      "id": "safety",
      "name": "Safety",
      "job": "Money, secrets, outreach, and identity stay behind gates.",
      "auto": "Block auto-repair on Stripe/secret paths.",
      "gated": "Any live write, send, charge, or publish.",
      "forbidden": "Keys in Pages JS. Auto outreach. Fake charges."
    }
  ],
  "desks": [
    {
      "href": "buddy.html",
      "label": "Buddy chat",
      "note": "Original home. Keep this chrome.",
      "group": "Talk"
    },
    {
      "href": "chat-sync.html",
      "label": "This chat → Pages",
      "note": "Everything from the latest Grok chat, live on Pages.",
      "group": "Talk"
    },
    {
      "href": "goals.html",
      "label": "Complete a goal",
      "note": "O*NET work, cut middlemen.",
      "group": "Talk"
    },
    {
      "href": "work.html",
      "label": "Tasks",
      "note": "Device, internet, API, MCP. Watch or screen-off.",
      "group": "Talk"
    },
    {
      "href": "os.html",
      "label": "Buddy OS",
      "note": "Syscalls on this device. GitHub is evidence.",
      "group": "Talk"
    },
    {
      "href": "actions.html",
      "label": "Actions",
      "note": "GitHub Actions health. Inventory, not greenwash.",
      "group": "Talk"
    },
    {
      "href": "command.html",
      "label": "Command",
      "note": "One unique model per step.",
      "group": "Talk"
    },
    {
      "href": "ops.html",
      "label": "Ops",
      "note": "Operator jobs as evidence.",
      "group": "Talk"
    },
    {
      "href": "connect-desk.html",
      "label": "Connect",
      "note": "Grant first. Mail send later.",
      "group": "Talk"
    },
    {
      "href": "devices.html",
      "label": "Devices",
      "note": "Pair Buddy you installed. No takeover.",
      "group": "Talk"
    },
    {
      "href": "wiring.html",
      "label": "Wiring map",
      "note": "Honest connection states only.",
      "group": "Talk"
    },
    {
      "href": "branch-health.html",
      "label": "Branch health",
      "note": "Daily scan. Never force-merges main.",
      "group": "Talk"
    },
    {
      "href": "recover.html",
      "label": "Recovery",
      "note": "Eight lanes. Missing evidence stays blocked.",
      "group": "Talk"
    },
    {
      "href": "build.html",
      "label": "Build readiness",
      "note": "Catalogued is not production.",
      "group": "Talk"
    },
    {
      "href": "hub.html",
      "label": "Hub OS",
      "note": "Study Hub datasets. License first.",
      "group": "Learn"
    },
    {
      "href": "learn-hf.html",
      "label": "7-day Hub week",
      "note": "Master Hugging Face in one week. Evidence required.",
      "group": "Learn"
    },
    {
      "href": "learn.html",
      "label": "Learn methods",
      "note": "Sandbox, five houses, Buddy originals.",
      "group": "Learn"
    },
    {
      "href": "sources.html",
      "label": "Connect sources",
      "note": "One-by-one. Register ≠ crawl.",
      "group": "Learn"
    },
    {
      "href": "desks.html",
      "label": "All plan desks",
      "note": "Clickable map.",
      "group": "Learn"
    },
    {
      "href": "models.html",
      "label": "500 models",
      "note": "Catalog is not live connectivity.",
      "group": "Labs"
    },
    {
      "href": "benchmark-tracker.html",
      "label": "Benchmark tracker",
      "note": "Blocked / native / assisted tracks.",
      "group": "Labs"
    },
    {
      "href": "buddy-learning-lab.html",
      "label": "Learning lab",
      "note": "Study loops and holdouts.",
      "group": "Labs"
    },
    {
      "href": "connections.html",
      "label": "App connections",
      "note": "0 verified live until a backend ping.",
      "group": "Labs"
    },
    {
      "href": "data-control.html",
      "label": "Data and memory",
      "note": "Local-first. Deny-by-default.",
      "group": "Labs"
    },
    {
      "href": "security.html",
      "label": "Defense center",
      "note": "Secrets never on Pages.",
      "group": "Labs"
    }
  ],
  "templates": [
    "Study squad on Hugging Face and pin the license",
    "Scan GitHub Actions health for Dreamcobots",
    "Plan: ship an app without a staffing firm",
    "List MCP tools Buddy can run now",
    "Ask Grok for a 5-step local-first plan to file a grant"
  ],
  "pagesBase": "https://dreamco-technologies.github.io/Dreamcobots/",
  "repo": "https://github.com/DreamCo-Technologies/Dreamcobots"
};
window.BUDDY_CHAT.licenseVerdict = function (license) {
  const id = String(license || "").trim().toLowerCase();
  if (!id || id === "unspecified" || id === "unknown" || id === "other") {
    return { verdict: "refuse", reason: "No SPDX on the card. Buddy will not index or load it." };
  }
  if (id.includes("nc") || id.includes("noncommercial") || id.includes("non-commercial")) {
    return { verdict: "study", reason: "Non-commercial. Study the card. Do not train a product on it." };
  }
  if (id.includes("openrail") || id.startsWith("llama") || id === "gemma") {
    return { verdict: "study", reason: "Use-restricted card. Read the license. Do not treat as Apache." };
  }
  if (window.BUDDY_CHAT.pin.indexOf(id) !== -1) {
    return { verdict: "index", reason: "Named license. Index the card. Rows stay on the Hub until you load with rights." };
  }
  return { verdict: "study", reason: "License named but uncommon. Study before any load." };
};
