---
name: Buddy Bot Feature Routes
description: All 16 Buddy API routes, their status, and key dependencies
---

## Routes Added (all in server/routes.ts inside registerRoutes())

| Route | Method | Status | Notes |
|---|---|---|---|
| /api/voice/clone | POST | needs-key | Requires ELEVENLABS_API_KEY; returns 503 + setup guide if absent |
| /api/voice/voices | GET | needs-key | Lists ElevenLabs voices |
| /api/search/web | POST | live | GitHub+OpenAI synthesis fallback; upgrades to Serper if SERPER_API_KEY set |
| /api/github-intel/trending | GET | live | Query param: `topic` (default: artificial-intelligence) |
| /api/github-intel/search | POST | live | Searches repos/code on GitHub |
| /api/council/proposals | GET | live | In-memory store, 3 default proposals seeded at startup |
| /api/council/report | POST | live | Submits a new proposal |
| /api/council/proposals/:id | PATCH | live | Approve/reject a proposal |
| /api/buddy/train | POST | live | Generates coding bootcamp exercises |
| /api/buddy/study-book | POST | live | Extracts insights from any nonfiction book |
| /api/buddy/vibe-code | POST | live | Full project generation as JSON with all files |
| /api/buddy/build-game | POST | live | Browser-playable game (HTML5/Canvas/Phaser) |
| /api/buddy/simulate-course | POST | live | Full college course simulation with syllabus |
| /api/intel/competitive | POST | live | Competitor analysis via GitHub + OpenAI |
| /api/data-packages | GET | live | Catalog of sellable training data packages |
| /api/buddy/features | GET | live | Live status of all 12 Buddy capabilities |

## Key Dependencies
- **ELEVENLABS_API_KEY** — voice cloning and TTS
- **SERPER_API_KEY** — Google web search (free tier: 2,500 queries/month at serper.dev)
- **GITHUB_TOKEN** — higher rate limits for GitHub intel (works unauthenticated at lower rate)

## UI
- `BuddySuperpowersPanel` in ConversationPage.tsx auto-opens when Buddy is active
- Each feature card runs a real API test on click, shows result inline
- "Vibe Code" is the 5th chat mode (cyan, with stack quick-select buttons)

**Why:** Routes must be in routes.ts because Vite's catch-all intercepts anything registered outside registerRoutes().
