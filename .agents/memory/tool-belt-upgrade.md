---
name: Tool-belt upgrade pattern
description: shared/tool-belt.ts is injected into every bot's system prompt via buildEnhancedSystemPrompt(); upgrading it simultaneously upgrades all 1,051+ bots.
---
The single highest-leverage file in the empire. Every export added here is injected into ALL bots automatically.

**Why:** buildEnhancedSystemPrompt() in shared/tool-belt.ts is called server-side for every chat request; all new protocols are prepended to the base system prompt of every bot.

**How to apply:** When adding new bot-wide capabilities (new revenue protocol, new safety rule, new skill-building pattern), add an export to tool-belt.ts and call it inside buildEnhancedSystemPrompt(). Never patch individual bot prompts for system-wide changes.

Current major exports:
- AUTONOMOUS_CASH_GENERATION_PROTOCOL (3-tier API rotation, 8 revenue streams)
- SELF_BUILDING_BOT_PROTOCOL (bot blueprint, self-healing, 5-level ladder)
- SKILL_BUILDER_PROTOCOL (skill anatomy, proactive categories)
- SELF_LEARNING_PROMPT (learning loop with REVENUE SIGNAL + BOT NEEDED lines)
- MODE_INSTRUCTIONS (plan/build/execute/teach)
- BUDDY_BOT_PROTOCOL (routing all coding + auth to Buddy)
