# DreamCo Beginner-First Product Experience

## Goal

A person who has never built an AI, used GitHub, written code, or configured an API should be able to create a useful Personal AI with Buddy without learning developer terminology first.

The product should teach only when teaching is necessary.

## The five-screen beginner journey

### Screen 1 — Tell Buddy what you want

Use plain language:

> "I want an AI that helps me run my small business."

Buddy translates the goal into capabilities. Do not expose models, embeddings, APIs, vector databases, agents, RAG, LoRA, or deployment settings on the first screen.

### Screen 2 — Choose what your AI should know

Large buttons:

- 📄 Documents
- 📚 Books I am allowed to use
- 📸 Photos
- 🎥 Videos I am allowed to use
- 🎙️ Voice/audio
- 💬 Conversations
- 🌐 Approved websites
- 💼 Business information

Every source gets a simple permission explanation before ingestion.

### Screen 3 — Teach your AI how to act

Starter skills:

- Talk like me
- Explain things simply
- Help me learn
- Help me sell
- Help me research
- Help me organize
- Help me write
- Help me code
- Build my own skill

The user can say what they want in ordinary language. Buddy creates the structured skill package behind the scenes.

### Screen 4 — Try it

Buddy generates 3–5 safe benchmark tasks based on the user's goal.

Show:

- what Buddy knows
- what it does not know
- what it can do
- what needs improvement
- estimated resource/cost usage

Use understandable labels such as **Learning**, **Ready to try**, **Needs more examples**, and **Needs your approval**.

### Screen 5 — Make it yours

Offer controls for:

- personality
- memory
- learning permission
- preferred response style
- connected tools
- model preference
- privacy
- export
- delete/reset

Advanced controls remain available behind **Advanced settings**.

## Beginner language rules

Prefer:

- "Teach your AI" instead of "fine-tune"
- "What should it remember?" instead of "memory policy"
- "What files can it use?" instead of "retrieval corpus"
- "Try a task" instead of "benchmark inference"
- "How good is it?" instead of "evaluation score"
- "AI engine" instead of "foundation model"
- "Connected tool" instead of "API adapter"
- "Private knowledge" instead of "vector store"

Advanced users can switch to technical terminology and raw configuration.

## Magic onboarding

The default path should be:

1. Name your AI.
2. Tell Buddy the job.
3. Add one source.
4. Choose one personality.
5. Teach one skill.
6. Run one test.
7. See the first useful result.
8. Offer upgrade options only after the user experiences value.

The first successful outcome should happen before the product asks the user to understand the architecture.

## Progressive disclosure

### Beginner mode

Only show the decision needed right now.

### Guided mode

Show short explanations and recommended choices.

### Builder mode

Expose skills, tools, memory rules, model routing, tests, and deployment settings.

### Developer mode

Expose repository files, schemas, GitHub Actions, logs, adapters, model IDs, environment configuration, and code.

Users can move between modes without rebuilding their AI.

## GitHub-first developer experience

DreamCo remains source-controlled in GitHub while beginners do not need to interact with Git directly.

The system should support:

- one documented setup path
- safe environment templates
- one-command local startup where practical
- GitHub Actions validation
- versioned Personal AI configuration
- exportable skill packages
- reproducible tests
- rollback to a previous Personal AI version
- clear logs and error messages
- no secrets committed to source control

The existing repository already uses GitHub as a central source of code, configuration, workflows, and Buddy tooling. The flagship should build on that instead of creating a second source of truth.

## Beginner error recovery

Never show a raw stack trace as the first explanation.

Use:

**What happened** → **What it means** → **What Buddy can do** → **What you need to approve**

Example:

> "Your video could not be processed. The file is readable, but this deployment does not have the video-processing tool enabled. I can prepare the connection steps, or you can choose another format."

Then provide an Advanced details option.

## Trust mechanics

Before learning from a source, show:

- source
- purpose
- what will be remembered
- how long it will be retained
- whether it can be deleted/exported
- whether it can be used for model training

Default to the least surprising permission.

## Value ladder

The product should create visible progress:

**New AI → Knows me → Understands my work → Learned a skill → Passed a test → Saves me time → Works across tools → Becomes my personal operating layer**

The interface should celebrate verified progress rather than fake intelligence scores.
