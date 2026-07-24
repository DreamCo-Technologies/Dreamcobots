# Buddy Bot Fleet End-to-End Certification

This report executes every registered bot through the repository-controlled Buddy flow. It verifies profile and route integrity, declared capabilities, runtime tools, a bot-specific sandbox task packet, required sandbox evidence, and the one-action live approval stop.

## Result

| Gate | Result |
|---|---:|
| Profiles tested | 1,051 |
| Sandbox certified | 1,051 |
| Failed | 0 |
| Divisions tested | 45 |
| Declared capabilities tested | 8,408 |
| Capability contracts passed | 8,408 |
| Capability contracts failed | 0 |
| Every declared capability tested | Yes |
| Repository-controlled flow complete | Yes |
| Live external flow complete | No |

## Deployment Boundary

Live external provider calls are not simulated as successful. They require an authenticated deployment, configured adapter, owner approval, and provider sandbox. Fleet totals are recorded in `website/data/bot-fleet-e2e.json`; per-capability evidence is sharded by division under `website/data/bot-capability-tests/`.

## Divisions

| Division | Profiles | Passed | Failed | Capability tests | Capability passed | Capability failed |
|---|---:|---:|---:|---:|---:|---:|
| CommandCore | 13 | 13 | 0 | 104 | 104 | 0 |
| DreamAdmin | 21 | 21 | 0 | 168 | 168 | 0 |
| DreamAgents | 20 | 20 | 0 | 160 | 160 | 0 |
| DreamAgriculture | 20 | 20 | 0 | 160 | 160 | 0 |
| DreamAIInfra | 25 | 25 | 0 | 200 | 200 | 0 |
| DreamArts | 18 | 18 | 0 | 144 | 144 | 0 |
| DreamAutomation | 21 | 21 | 0 | 168 | 168 | 0 |
| DreamBizLaunch | 21 | 21 | 0 | 168 | 168 | 0 |
| DreamCodeLab | 146 | 146 | 0 | 1168 | 1168 | 0 |
| DreamConstruction | 19 | 19 | 0 | 152 | 152 | 0 |
| DreamContent | 16 | 16 | 0 | 128 | 128 | 0 |
| DreamCrypto | 20 | 20 | 0 | 160 | 160 | 0 |
| DreamCustIntel | 25 | 25 | 0 | 200 | 200 | 0 |
| DreamCyber | 25 | 25 | 0 | 200 | 200 | 0 |
| DreamData | 16 | 16 | 0 | 128 | 128 | 0 |
| DreamDecision | 25 | 25 | 0 | 200 | 200 | 0 |
| DreamEducation | 20 | 20 | 0 | 160 | 160 | 0 |
| DreamEmpire | 5 | 5 | 0 | 40 | 40 | 0 |
| DreamEntFinance | 25 | 25 | 0 | 200 | 200 | 0 |
| DreamFinance | 25 | 25 | 0 | 200 | 200 | 0 |
| DreamFlow | 5 | 5 | 0 | 40 | 40 | 0 |
| DreamFood | 20 | 20 | 0 | 160 | 160 | 0 |
| DreamGlobal | 16 | 16 | 0 | 128 | 128 | 0 |
| DreamHealth | 20 | 20 | 0 | 160 | 160 | 0 |
| DreamInfluence | 25 | 25 | 0 | 200 | 200 | 0 |
| DreamLegal | 25 | 25 | 0 | 200 | 200 | 0 |
| DreamLoans | 23 | 23 | 0 | 184 | 184 | 0 |
| DreamMaintenance | 21 | 21 | 0 | 168 | 168 | 0 |
| DreamMarket | 5 | 5 | 0 | 40 | 40 | 0 |
| DreamMilitary | 20 | 20 | 0 | 160 | 160 | 0 |
| DreamOps | 26 | 26 | 0 | 208 | 208 | 0 |
| DreamPayments | 23 | 23 | 0 | 184 | 184 | 0 |
| DreamPersonalCare | 30 | 30 | 0 | 240 | 240 | 0 |
| DreamPlanetary | 25 | 25 | 0 | 200 | 200 | 0 |
| DreamProduction | 20 | 20 | 0 | 160 | 160 | 0 |
| DreamProServices | 25 | 25 | 0 | 200 | 200 | 0 |
| DreamProtection | 20 | 20 | 0 | 160 | 160 | 0 |
| DreamRealEstate | 25 | 25 | 0 | 200 | 200 | 0 |
| DreamRetail | 26 | 26 | 0 | 208 | 208 | 0 |
| DreamSalesPro | 37 | 37 | 0 | 296 | 296 | 0 |
| DreamScience | 20 | 20 | 0 | 160 | 160 | 0 |
| DreamSocial | 33 | 33 | 0 | 264 | 264 | 0 |
| DreamTrade | 12 | 12 | 0 | 96 | 96 | 0 |
| DreamTransport | 19 | 19 | 0 | 152 | 152 | 0 |
| GameTitan | 4 | 4 | 0 | 32 | 32 | 0 |
