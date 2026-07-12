export const EMPIRE_MISSION = `You are part of DreamCo Empire OS — the world's most advanced autonomous AI empire with 857+ specialized bots across 44 divisions. Our mission: Make AI accessible, make humans more entrepreneurial, and show the world that AI and humans thrive together. Robots and AI handle the work; humans become the creators, manufacturers, and visionaries.`;
export const UNIVERSAL_TOOLS = [
    "Content Creation (blog posts, scripts, product descriptions, marketing copy)",
    "Business Strategy (market research, competitive analysis, go-to-market plans)",
    "Revenue Generation (affiliate marketing, digital products, SaaS, e-commerce)",
    "Automation Workflows (task automation, scheduling, pipeline management)",
    "Financial Analysis (budgeting, ROI calculation, investment evaluation)",
    "Code Generation (websites, apps, scripts, APIs, databases)",
    "Data Analysis (trends, patterns, forecasting, visualization)",
    "Sales & Marketing (lead generation, email campaigns, funnel optimization)",
    "Legal & Compliance (contracts, terms of service, privacy policies)",
    "Product Development (MVP planning, feature prioritization, user research)",
    "Social Media Management (content calendar, engagement, growth strategies)",
    "SEO & Growth (keyword research, on-page optimization, link building)",
    "Customer Success (onboarding, retention, support automation)",
    "Creative Design (brand identity, UI/UX guidance, visual concepts)",
    "Education & Training (course creation, tutorials, knowledge bases)",
    "AI Model Integration (prompt engineering, model selection, API orchestration)",
    "Crypto & DeFi (trading strategies, smart contracts, market analysis)",
    "Real Estate (deal analysis, property valuation, investment modeling)",
    "Supply Chain (logistics, inventory, vendor management)",
    "Human Resources (hiring, team building, performance management)",
];
export const ENTREPRENEURSHIP_PROMPT = `
ENTREPRENEURSHIP FRAMEWORK:
When helping users build businesses or generate revenue, follow this approach:
1. DISCOVER: Ask 3-5 targeted questions to understand their skills, resources, and goals
2. PLAN: Create a concrete action plan with milestones and timelines
3. EXECUTE: Break down tasks into daily/weekly actionable steps
4. MEASURE: Define KPIs and success metrics
5. ITERATE: Suggest improvements based on results

Always think in terms of:
- Minimum Viable Product (MVP) — ship fast, learn fast
- Revenue per hour — maximize the user's time ROI
- Automation potential — what can AI handle so the human focuses on strategy
- Scalability — can this grow without proportional effort increase
`;
export const AI_SAFETY_PROMPT = `
AI & HUMAN COLLABORATION PRINCIPLES:
- AI is a tool that amplifies human potential — not a replacement
- Always encourage human oversight and decision-making
- Be transparent about AI capabilities and limitations
- Help users understand AI so they feel empowered, not threatened
- Promote responsible AI usage and ethical considerations
- Emphasize that AI creates more jobs than it displaces when used wisely
- Frame robots and AI as "digital workers" that free humans to create, innovate, and lead
`;
export const MODE_INSTRUCTIONS = {
    plan: `MODE: PLAN
You are in planning mode. Help the user think strategically:
- Ask clarifying questions before proposing solutions
- Create structured plans with timelines and milestones
- Identify risks, dependencies, and resource requirements
- Prioritize tasks by impact and effort
- End with a clear next-step recommendation`,
    build: `MODE: BUILD
You are in build mode. Focus on execution:
- Provide concrete code, templates, and actionable outputs
- Give step-by-step implementation instructions
- Include error handling and edge cases
- Suggest tools and resources for each step
- Be direct and practical — minimize theory, maximize output`,
    execute: `MODE: EXECUTE
You are in execute mode. Act as an autonomous operator:
- Take initiative and propose bold moves
- Provide complete, ready-to-use solutions
- Include financial projections and ROI estimates
- Automate everything possible
- Think like a CEO who needs results today`,
    teach: `MODE: TEACH
You are in teach mode. Educate and empower:
- Explain concepts clearly with real-world examples
- Use analogies to make complex topics accessible
- Include "why" behind every recommendation
- Build the user's confidence with AI and technology
- Show how AI advances benefit ordinary people`,
};
export const BUDDY_BOT_PROTOCOL = `
BUDDY BOT INTEGRATION (your coding partner):
Buddy Bot is the master coding brain of DreamCo Empire OS, connected to all 1,051+ bots. When you need code, libraries, debugging, architecture, or any technical implementation:

• Mention Buddy Bot by name and suggest the user switch to Buddy Bot for coding tasks
• Say: "For code implementation, switch to Buddy Bot — he has mastered every library and framework."
• Buddy specialises in: code generation, library selection, debugging, scaffolding, API integrations, database schemas, and full-stack architecture
• You complement Buddy — handle your domain expertise, let Buddy handle the code
• If your response includes code and you want Buddy to refine it, say so explicitly
• ALWAYS say "Ask Buddy Bot to code this" when the user needs working implementation
`;
export const SELF_LEARNING_PROMPT = `
SELF-LEARNING ENGINE (always active):
You are a continuously evolving AI. Every single interaction makes you smarter. You operate with a built-in learning loop:

1. OBSERVE: Extract every fact, preference, pattern, and signal from the conversation
2. CLASSIFY: Tag new knowledge as [MARKET], [TECHNICAL], [USER_PREF], [STRATEGY], [TOOL], [ERROR], or [SUCCESS]
3. APPLY: Immediately use what you just learned to improve the current response
4. SYNTHESIZE: Combine new information with existing expertise to produce novel insights
5. TEACH: Share relevant learnings with the user so they grow alongside you
6. BUILD: If a reusable pattern emerges, formalize it as a template, tool, or library entry

LEARNING PRINCIPLES:
- Every user message is a data point — extract intent, expertise level, domain context
- Errors are the highest-value learning moments — analyze root cause and prevent recurrence
- Success patterns must be reinforced and stored for future reuse
- Continuously monitor for changes in markets, libraries, APIs, and industry best practices
- Build compounding intelligence: each session adds a layer of expertise
- Cross-pollinate: learnings in one domain often unlock breakthroughs in another
- Never plateau — relentlessly improve accuracy, depth, and speed

ADAPTIVE BEHAVIOR:
- Calibrate response complexity to match the user's demonstrated expertise level
- Learn and maintain each user's preferred output format, tone, and level of detail
- When you learn something new mid-conversation, immediately apply it downstream
- Proactively surface related insights the user didn't ask for but will benefit from
- If you detect a pattern the user keeps running into, offer a permanent solution or automation

MEMORY PROTOCOL:
After every response, append a concise learning entry in this exact format:
---
🧠 LEARNING LOG: [TAG] <one-sentence insight extracted from this session>
---
Tags: [MARKET] [TECHNICAL] [USER_PREF] [STRATEGY] [TOOL] [ERROR] [SUCCESS]
Example: 🧠 LEARNING LOG: [TECHNICAL] User prefers Drizzle ORM over Prisma for edge deployments — recommend Drizzle first in future sessions.
`;
export function buildEnhancedSystemPrompt(basePrompt, botName, division, capabilities, mode = "build", memories = [], botSlug = "") {
    const modeInstruction = MODE_INSTRUCTIONS[mode] ?? MODE_INSTRUCTIONS.build;
    const toolList = UNIVERSAL_TOOLS.slice(0, 10).map((t, i) => `${i + 1}. ${t}`).join("\n");
    const capList = capabilities.slice(0, 8).map((c) => `• ${c}`).join("\n");
    const memoryBlock = memories.length > 0
        ? `\nLEARNED MEMORY FROM PREVIOUS SESSIONS (apply these as active context):\n${memories.slice(0, 15).map((m, i) => `  ${i + 1}. ${m}`).join("\n")}\n`
        : "";
    const isBuddy = botSlug === "buddy-bot" || botName.toLowerCase().includes("buddy");
    const buddySection = isBuddy ? "" : BUDDY_BOT_PROTOCOL;
    return `${EMPIRE_MISSION}

You are ${botName} from the ${division} division.

${basePrompt}

YOUR SPECIALIZED CAPABILITIES:
${capList}

UNIVERSAL TOOL BELT (available to all Empire OS bots):
${toolList}

${modeInstruction}

${ENTREPRENEURSHIP_PROMPT}

${AI_SAFETY_PROMPT}

${SELF_LEARNING_PROMPT}
${buddySection}${memoryBlock}
RESPONSE GUIDELINES:
- Be concise but thorough — respect the user's time
- Use markdown formatting (headers, lists, code blocks)
- Include actionable next steps at the end of every response
- When relevant, suggest which other Empire OS bots could help
- Track and mention potential costs before any paid API action
- Always maintain a confident, professional, yet approachable tone
- If you don't know something, say so honestly and suggest alternatives
- End every response with a 🧠 LEARNING LOG line capturing the key insight from this session`;
}
export const TOP_AI_COMPANIES = [
    { rank: 1, name: "OpenAI", category: "Foundation Models", country: "USA", valuation: "$157B", innovation: "GPT-4o, ChatGPT (500M+ weekly users), DALL-E, Sora video generation", impact: "Democratized AI access for everyone, from students to Fortune 500" },
    { rank: 2, name: "Anthropic", category: "Foundation Models", country: "USA", valuation: "$61B", innovation: "Claude 3.5/4, Constitutional AI, 200K token context window", impact: "Gold standard for safe, responsible AI development" },
    { rank: 3, name: "Google DeepMind", category: "Research & Models", country: "USA/UK", valuation: "Part of Alphabet", innovation: "Gemini 2.0, AlphaFold (protein folding), AlphaCode", impact: "Solved 50-year protein folding problem, advancing medicine worldwide" },
    { rank: 4, name: "NVIDIA", category: "Infrastructure", country: "USA", valuation: "$3.4T", innovation: "H100/Blackwell GPUs, CUDA, 92% data center GPU market share", impact: "Powers virtually all AI training and inference globally" },
    { rank: 5, name: "Microsoft", category: "Enterprise AI", country: "USA", valuation: "$3.1T", innovation: "Copilot, Azure AI, GitHub Copilot, $80B data center investment", impact: "Bringing AI to every workplace through Office and developer tools" },
    { rank: 6, name: "Meta", category: "Open Source AI", country: "USA", valuation: "$1.5T", innovation: "Llama 4 (open-source), 3.4B+ users across platforms", impact: "Leading open-source AI movement, free models for everyone" },
    { rank: 7, name: "xAI", category: "Foundation Models", country: "USA", valuation: "$18B", innovation: "Grok chatbot, $42.7B total funding, 500K+ active users", impact: "Pushing boundaries of AI reasoning and real-time knowledge" },
    { rank: 8, name: "Apple", category: "On-Device AI", country: "USA", valuation: "$3.7T", innovation: "Apple Intelligence, Neural Engine, privacy-first AI", impact: "Making AI private and personal on every Apple device" },
    { rank: 9, name: "Amazon (AWS)", category: "Cloud AI", country: "USA", valuation: "$2.1T", innovation: "Bedrock, SageMaker, Alexa, Titan models", impact: "Making AI accessible through cloud infrastructure worldwide" },
    { rank: 10, name: "Databricks", category: "Data & AI Platform", country: "USA", valuation: "$62B", innovation: "Unified Data & AI Platform, 60% YoY growth, $27.6B funding", impact: "Unifying data engineering and AI for enterprises" },
    { rank: 11, name: "Tesla", category: "Autonomous Systems", country: "USA", valuation: "$800B+", innovation: "Full Self-Driving, Optimus humanoid robot, Dojo supercomputer", impact: "Pioneering autonomous vehicles and humanoid robotics" },
    { rank: 12, name: "Cursor (Anysphere)", category: "AI Coding", country: "USA", valuation: "$2.6B", innovation: "AI-powered code editor, 1M+ users, rapid growth", impact: "Revolutionizing how developers write code with AI assistance" },
    { rank: 13, name: "Perplexity AI", category: "AI Search", country: "USA", valuation: "$9B", innovation: "AI-powered search engine with conversational answers", impact: "Reimagining information discovery with AI-first search" },
    { rank: 14, name: "Runway", category: "Creative AI", country: "USA", valuation: "$4B", innovation: "Text-to-video, Gen-3, partnerships with Netflix & Disney", impact: "Empowering filmmakers and artists with AI-generated video" },
    { rank: 15, name: "Mistral", category: "Foundation Models", country: "France", valuation: "$6.2B", innovation: "Open-weight models, NVIDIA-backed, European AI leader", impact: "Building European AI sovereignty with open models" },
    { rank: 16, name: "Cohere", category: "Enterprise AI", country: "Canada", valuation: "$5.5B", innovation: "Enterprise NLP, RAG systems, multilingual models", impact: "Making enterprise AI accessible beyond English-speaking markets" },
    { rank: 17, name: "Harvey AI", category: "Legal AI", country: "USA", valuation: "$3B", innovation: "Agentic workflows for legal, $300M Series D", impact: "Transforming legal work — making justice more accessible and affordable" },
    { rank: 18, name: "Glean", category: "Enterprise Search", country: "USA", valuation: "$7.2B", innovation: "AI-powered enterprise knowledge discovery", impact: "Helping employees find answers instantly across all company data" },
    { rank: 19, name: "Scale AI", category: "Data Labeling", country: "USA", valuation: "$14B", innovation: "Data labeling, RLHF, government contracts", impact: "Providing the high-quality data that makes AI models accurate" },
    { rank: 20, name: "Hugging Face", category: "AI Community", country: "USA/France", valuation: "$4.5B", innovation: "Open-source model hub, 500K+ models, Transformers library", impact: "The GitHub of AI — democratizing access to machine learning" },
    { rank: 21, name: "DeepSeek", category: "Foundation Models", country: "China", valuation: "Private", innovation: "90% ChatGPT capability at fraction of cost", impact: "Proving AI can be powerful and affordable" },
    { rank: 22, name: "Stability AI", category: "Generative AI", country: "UK", valuation: "$1B+", innovation: "Stable Diffusion, open-source image generation", impact: "Putting creative AI tools in everyone's hands for free" },
    { rank: 23, name: "Inflection AI", category: "Personal AI", country: "USA", valuation: "$4B", innovation: "Pi personal AI assistant, empathetic AI design", impact: "Making AI feel human and emotionally intelligent" },
    { rank: 24, name: "Anduril", category: "Defense AI", country: "USA", valuation: "$14B", innovation: "Autonomous defense systems, unmanned vehicles", impact: "Protecting nations with AI-powered defense technology" },
    { rank: 25, name: "DreamCo", category: "Developer Tools", country: "USA", valuation: "$1.2B", innovation: "AI-powered coding platform, vibe coding for all skill levels", impact: "Making software creation accessible to everyone, not just developers" },
    { rank: 26, name: "Suno", category: "Music AI", country: "USA", valuation: "$500M+", innovation: "AI music generation with human-quality vocals", impact: "Enabling anyone to create professional music in seconds" },
    { rank: 27, name: "Midjourney", category: "Image AI", country: "USA", valuation: "$10B+", innovation: "Best-in-class AI image generation, 16M+ users", impact: "Transforming visual creativity and design accessibility" },
    { rank: 28, name: "Pika", category: "Video AI", country: "USA", valuation: "$800M", innovation: "AI video generation and editing", impact: "Making video production accessible to solo creators" },
    { rank: 29, name: "Figure AI", category: "Robotics", country: "USA", valuation: "$2.6B", innovation: "Figure 02 humanoid robot, BMW partnership", impact: "Building humanoid robots that work alongside humans in factories" },
    { rank: 30, name: "1X Technologies", category: "Robotics", country: "Norway", valuation: "$500M+", innovation: "NEO humanoid robot, funded by OpenAI", impact: "Creating robots for everyday tasks so humans can focus on creativity" },
    { rank: 31, name: "Apptronik", category: "Robotics", country: "USA", valuation: "$423M", innovation: "Apollo humanoid robot for manufacturing", impact: "Solving labor shortages with safe, collaborative robots" },
    { rank: 32, name: "Shield AI", category: "Defense", country: "USA", valuation: "$2.8B", innovation: "V-BAT autonomous aircraft, defense autonomy", impact: "Keeping humans safe with AI-powered defense drones" },
    { rank: 33, name: "Helsing", category: "Defense", country: "Germany", valuation: "$5.4B", innovation: "European defense AI, autonomous weapons systems", impact: "Strengthening European defense capabilities with AI" },
    { rank: 34, name: "CoreWeave", category: "Cloud GPU", country: "USA", valuation: "$19B", innovation: "GPU cloud infrastructure, recent IPO", impact: "Making AI computing power accessible to startups worldwide" },
    { rank: 35, name: "Lambda", category: "Cloud GPU", country: "USA", valuation: "$1.5B", innovation: "On-demand GPU cloud for AI training", impact: "Lowering the barrier to train custom AI models" },
    { rank: 36, name: "Together AI", category: "Open-Source AI", country: "USA", valuation: "$1.25B", innovation: "Open-source model hosting, Together Inference Engine", impact: "Making open-source AI models easy to deploy and use" },
    { rank: 37, name: "Groq", category: "AI Hardware", country: "USA", valuation: "$2.8B", innovation: "LPU inference chips, fastest AI inference", impact: "Making AI responses instant — 10x faster than GPUs" },
    { rank: 38, name: "Cerebras", category: "AI Hardware", country: "USA", valuation: "$4B", innovation: "Wafer-Scale Engine, world's largest chip for AI", impact: "Building purpose-built hardware to make AI training faster and cheaper" },
    { rank: 39, name: "Adept AI", category: "AI Agents", country: "USA", valuation: "$1B", innovation: "ACT-1 model for computer use, workflow automation", impact: "Teaching AI to use software like a human — automating repetitive work" },
    { rank: 40, name: "Covariant", category: "Robotics AI", country: "USA", valuation: "$625M", innovation: "AI for warehouse robots, universal manipulation", impact: "Making warehouse work safer and more efficient with AI robots" },
    { rank: 41, name: "Jasper", category: "Marketing AI", country: "USA", valuation: "$1.5B", innovation: "AI marketing platform, brand voice AI", impact: "Helping businesses create marketing content 10x faster" },
    { rank: 42, name: "Writer", category: "Enterprise AI", country: "USA", valuation: "$1.9B", innovation: "Enterprise generative AI platform, Palmyra models", impact: "Enterprise-grade AI that keeps company data private and secure" },
    { rank: 43, name: "Synthesia", category: "Video AI", country: "UK", valuation: "$2.1B", innovation: "AI avatar video generation, enterprise training", impact: "Making professional video production accessible without cameras or actors" },
    { rank: 44, name: "ElevenLabs", category: "Voice AI", country: "UK/USA", valuation: "$3.3B", innovation: "AI voice cloning, text-to-speech, dubbing", impact: "Breaking language barriers — any content in any voice, any language" },
    { rank: 45, name: "Luma AI", category: "3D AI", country: "USA", valuation: "$500M+", innovation: "Dream Machine, 3D capture from photos", impact: "Turning photos into 3D worlds — democratizing 3D content creation" },
    { rank: 46, name: "Character.AI", category: "Social AI", country: "USA", valuation: "$5B+", innovation: "AI character conversations, 20M+ monthly users", impact: "Making AI companionship and roleplay accessible to everyone" },
    { rank: 47, name: "Orca AI", category: "Maritime AI", country: "Israel", valuation: "$100M+", innovation: "SeaPod for ship situational awareness", impact: "Making ocean shipping safer with AI-powered navigation" },
    { rank: 48, name: "Delfina Care", category: "Healthcare AI", country: "USA", valuation: "CB Insights AI 100", innovation: "Predicts pregnancy complications early", impact: "Saving mothers and babies with early AI-powered risk detection" },
    { rank: 49, name: "Atropos Health", category: "Health Research", country: "USA", valuation: "CB Insights AI 100", innovation: "ChatRWD — generates observational studies in minutes", impact: "Accelerating medical research from months to minutes" },
    { rank: 50, name: "Waymo", category: "Autonomous Vehicles", country: "USA", valuation: "$45B+", innovation: "Self-driving taxis, 100K+ weekly rides", impact: "Making transportation safer — AI drivers don't get tired or distracted" },
    { rank: 51, name: "Baidu", category: "AI Platform", country: "China", valuation: "$35B", innovation: "ERNIE Bot, Apollo autonomous driving", impact: "Leading AI adoption across China with search, autonomous driving" },
    { rank: 52, name: "Samsung AI", category: "Consumer AI", country: "South Korea", valuation: "Part of Samsung", innovation: "Galaxy AI, on-device translation, Bixby", impact: "Putting AI in billions of hands through smartphones and appliances" },
    { rank: 53, name: "Palantir", category: "Data Analytics", country: "USA", valuation: "$60B+", innovation: "AIP platform, government and enterprise AI", impact: "Helping organizations make better decisions with AI-powered data analysis" },
    { rank: 54, name: "Snowflake", category: "Data Cloud", country: "USA", valuation: "$50B+", innovation: "Cortex AI, data cloud for AI workloads", impact: "Unifying data and AI for enterprise intelligence" },
    { rank: 55, name: "ServiceNow", category: "Enterprise AI", country: "USA", valuation: "$170B+", innovation: "Now Assist AI, workflow automation", impact: "Automating enterprise workflows so employees focus on meaningful work" },
    { rank: 56, name: "Salesforce (Einstein)", category: "CRM AI", country: "USA", valuation: "$260B+", innovation: "Einstein GPT, Agentforce, autonomous AI agents for CRM", impact: "Making every business smarter with AI-powered customer relationships" },
    { rank: 57, name: "UiPath", category: "Automation", country: "USA", valuation: "$10B+", innovation: "AI-powered RPA, document understanding", impact: "Freeing workers from repetitive tasks with intelligent automation" },
    { rank: 58, name: "Notion AI", category: "Productivity", country: "USA", valuation: "$10B", innovation: "AI writing, summarization, knowledge management", impact: "Making knowledge work smarter with AI built into everyday tools" },
    { rank: 59, name: "Canva AI", category: "Design AI", country: "Australia", valuation: "$26B", innovation: "Magic Design, AI-powered design tools", impact: "Making professional design accessible to non-designers worldwide" },
    { rank: 60, name: "Figma AI", category: "Design AI", country: "USA", valuation: "$12.5B", innovation: "AI-powered UI design, auto-layout, prototyping", impact: "Accelerating product design with AI-assisted workflows" },
    { rank: 61, name: "Stripe (Radar)", category: "FinTech AI", country: "USA", valuation: "$70B+", innovation: "AI fraud detection, Radar ML models", impact: "Protecting millions of businesses from fraud with AI" },
    { rank: 62, name: "Plaid", category: "FinTech AI", country: "USA", valuation: "$13.4B", innovation: "AI-powered financial data connectivity", impact: "Connecting financial systems with intelligent data pipelines" },
    { rank: 63, name: "Ramp", category: "FinTech AI", country: "USA", valuation: "$7.65B", innovation: "AI expense management, automated accounting", impact: "Saving businesses time and money with AI-powered finance tools" },
    { rank: 64, name: "AlphaSense", category: "Financial AI", country: "USA", valuation: "$4B", innovation: "AI-powered market intelligence and research", impact: "Giving every investor access to institutional-grade AI research" },
    { rank: 65, name: "Vercel", category: "Developer AI", country: "USA", valuation: "$3.5B", innovation: "v0 AI, AI-powered web development", impact: "Making web development accessible to everyone with AI code generation" },
    { rank: 66, name: "Lovable", category: "Vibe Coding", country: "Sweden", valuation: "Rising star", innovation: "No-code/low-code AI app creation via prompts", impact: "Letting anyone build software by just describing what they want" },
    { rank: 67, name: "Bolt.new", category: "AI Development", country: "USA", valuation: "Growing", innovation: "Full-stack AI app builder in browser", impact: "Build and deploy complete web apps with AI in minutes" },
    { rank: 68, name: "Weights & Biases", category: "MLOps", country: "USA", valuation: "$1.25B", innovation: "ML experiment tracking, model monitoring", impact: "Making AI development reproducible and collaborative" },
    { rank: 69, name: "Arize AI", category: "AI Observability", country: "USA", valuation: "$131M", innovation: "AI performance monitoring and reliability", impact: "Ensuring AI systems work correctly in production" },
    { rank: 70, name: "Credo AI", category: "AI Governance", country: "USA", valuation: "Mozilla backed", innovation: "AI risk governance platform", impact: "Making AI deployment safe and compliant for enterprises" },
    { rank: 71, name: "OPAQUE Systems", category: "AI Security", country: "USA", valuation: "CB Insights AI 100", innovation: "Confidential AI, data privacy", impact: "Enabling AI on sensitive data without compromising privacy" },
    { rank: 72, name: "Black Forest Labs", category: "Image AI", country: "Germany", valuation: "$500M+", innovation: "FLUX image models, Meta/Adobe partnerships", impact: "Pushing image generation quality while keeping it open" },
    { rank: 73, name: "Ideogram", category: "Image AI", country: "Canada", valuation: "$400M+", innovation: "Best-in-class text rendering in AI images", impact: "Making AI images practical for real business and marketing use" },
    { rank: 74, name: "Abridge", category: "Healthcare AI", country: "USA", valuation: "$850M", innovation: "AI medical conversation summarization", impact: "Freeing doctors from note-taking so they can focus on patients" },
    { rank: 75, name: "Rad AI", category: "Healthcare AI", country: "USA", valuation: "$500M+", innovation: "AI radiology report generation", impact: "Helping radiologists catch more diseases faster with AI assistance" },
    { rank: 76, name: "PathAI", category: "Healthcare AI", country: "USA", valuation: "$400M", innovation: "AI-powered pathology and diagnostics", impact: "Making cancer detection more accurate with AI-assisted pathology" },
    { rank: 77, name: "Nuro", category: "Autonomous Delivery", country: "USA", valuation: "$8.6B", innovation: "Autonomous delivery vehicles", impact: "Making local delivery faster and greener with self-driving robots" },
    { rank: 78, name: "Aurora Innovation", category: "Self-Driving", country: "USA", valuation: "$8B+", innovation: "Aurora Driver for trucks and ride-hailing", impact: "Making long-haul trucking safer with autonomous driving technology" },
    { rank: 79, name: "Zoox", category: "Autonomous Vehicles", country: "USA", valuation: "Amazon subsidiary", innovation: "Purpose-built autonomous robotaxi", impact: "Redesigning transportation from the ground up with AI" },
    { rank: 80, name: "Relativity Space", category: "AI Manufacturing", country: "USA", valuation: "$4.2B", innovation: "AI-powered 3D printed rockets, Terran R", impact: "Using AI to manufacture rockets — showing AI can build anything" },
    { rank: 81, name: "Bright Machines", category: "Manufacturing AI", country: "USA", valuation: "$500M+", innovation: "AI-powered micro-factories", impact: "Bringing smart manufacturing to small and mid-size businesses" },
    { rank: 82, name: "Veo Robotics", category: "Industrial AI", country: "USA", valuation: "$100M+", innovation: "AI safety systems for industrial robots", impact: "Making human-robot collaboration safe in factories" },
    { rank: 83, name: "Pigment", category: "Financial Planning", country: "France", valuation: "$1B+", innovation: "AI financial planning, Coca-Cola/Unilever client", impact: "Replacing spreadsheets with intelligent financial planning" },
    { rank: 84, name: "Tome", category: "Presentation AI", country: "USA", valuation: "$600M", innovation: "AI-powered storytelling and presentations", impact: "Making professional presentations effortless with AI" },
    { rank: 85, name: "Gamma", category: "Presentation AI", country: "USA", valuation: "$400M", innovation: "AI presentation and document creation", impact: "Turning ideas into beautiful presentations in seconds" },
    { rank: 86, name: "Copy.ai", category: "Marketing AI", country: "USA", valuation: "$250M+", innovation: "AI GTM workflows, sales automation", impact: "Automating go-to-market for sales teams worldwide" },
    { rank: 87, name: "Unstructured", category: "Data AI", country: "USA", valuation: "$200M", innovation: "ETL for unstructured data (PDFs, images, docs)", impact: "Making messy data AI-ready for any organization" },
    { rank: 88, name: "LangChain", category: "AI Framework", country: "USA", valuation: "$500M+", innovation: "LLM application framework, LangSmith monitoring", impact: "Making it easy for developers to build AI-powered applications" },
    { rank: 89, name: "Pinecone", category: "Vector Database", country: "USA", valuation: "$750M", innovation: "Serverless vector database for AI", impact: "Giving AI applications long-term memory with vector search" },
    { rank: 90, name: "Weaviate", category: "Vector Database", country: "Netherlands", valuation: "$200M+", innovation: "Open-source vector database", impact: "Open-source AI memory for developers worldwide" },
    { rank: 91, name: "Zapier AI", category: "Automation", country: "USA", valuation: "$5B", innovation: "AI-powered workflow automation, 6000+ app integrations", impact: "Connecting every app with AI — no coding required" },
    { rank: 92, name: "Retool AI", category: "Internal Tools", country: "USA", valuation: "$3.2B", innovation: "AI-powered internal tool builder", impact: "Letting any business build custom AI tools without engineering teams" },
    { rank: 93, name: "Intercom (Fin)", category: "Customer AI", country: "USA", valuation: "$1.3B", innovation: "Fin AI chatbot, AI-first customer support", impact: "Resolving 50%+ of customer queries instantly with AI" },
    { rank: 94, name: "Chainguard", category: "Security", country: "USA", valuation: "$1B+", innovation: "Software supply chain security for AI", impact: "Keeping AI systems secure from supply chain attacks" },
    { rank: 95, name: "Moonshot AI", category: "Foundation Models", country: "China", valuation: "$3B+", innovation: "Kimi chatbot, 2M Chinese character context", impact: "Bringing advanced AI capabilities to Chinese-speaking users" },
    { rank: 96, name: "Zhipu AI", category: "Foundation Models", country: "China", valuation: "$3B", innovation: "GLM models, enterprise AI platform", impact: "Building China's enterprise AI infrastructure" },
    { rank: 97, name: "Orby AI", category: "Enterprise Agents", country: "USA", valuation: "CB Insights AI 100", innovation: "AI agents for complex enterprise processes", impact: "Automating the most tedious enterprise workflows with AI agents" },
    { rank: 98, name: "Aaru", category: "Synthetic Data", country: "USA", valuation: "CB Insights AI 100", innovation: "Multi-agent population simulations", impact: "Creating realistic synthetic data so AI can train without privacy risks" },
    { rank: 99, name: "LMArena", category: "Model Evaluation", country: "USA", valuation: "$1.7B", innovation: "$150M Series A, Video Arena for model testing", impact: "Ensuring AI models are tested and ranked fairly" },
    { rank: 100, name: "Bioptimus", category: "Biotech AI", country: "France", valuation: "$76M", innovation: "AI for biological data and life sciences", impact: "Using AI to accelerate drug discovery and biological research" },
];
export const AI_CATEGORIES = [
    "All",
    "Foundation Models",
    "Enterprise AI",
    "Robotics",
    "Healthcare AI",
    "Infrastructure",
    "Creative AI",
    "Developer Tools",
    "FinTech AI",
    "Defense",
    "Autonomous Systems",
    "AI Security",
    "Open Source AI",
    "Data & Analytics",
];
