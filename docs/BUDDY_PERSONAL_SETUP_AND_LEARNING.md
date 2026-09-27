# Personal Buddy setup, evidence and remaining delivery

The guided setup page is `website/buddy-setup-guide.html`. It saves fixed choices in the browser, links to existing tools and exports a plan. It does not create a private user account or mark a plugin connected.

The learning evidence page is `website/buddy-learning-evidence.html`. Users can add up to20 authorized plain-text sources, search cited passages, freeze a baseline and measure the same retrieval question before and after adding material. Text stays in tab memory. An evidence download contains the tested question and matching passages; the user controls that local export. No source is uploaded or model weights updated by that page.

## What has been verified

- The existing small character trainer actually updates16,302parameters on600template-derived note strings. The reproducible verification tool checks parameter deltas, a fixed sample of training windows, checkpoint reload equality and preservation of tracked weights and histories. Loss on those training data is not a held-out benchmark or proof of improved Buddy chat.
- `tools/prove_buddy_learning.py` is a synthetic bookkeeping test: one injected failure plus three injected passes. Its own history remains separate from real learning history.
- The browser model lab runs pinned Hugging Face weights. Its unscored output record proves execution only; users still need task-quality evaluation.
- The full fleet is1,051canonical profiles and50supplemental profiles. Unified inventory, scheduling plans, system-map objects and sandbox evidence retain both groups. Supplemental outcome readiness remains unverified.
- Every indexed file has an exportable metadata prospectus in the command center and dashboard. Folder-derived purpose and candidate relations are explicitly provisional; reading/testing each file is still needed for an implementation-level specification.
- The Actions page has a dedicated prospectus library and an export for each workflow, with static findings and last loaded run evidence.

## Learning routes and their actual next step

| Route | Available now | Required before claiming learning or production use |
| --- | --- | --- |
| Public web and documentation | Resource discovery, citations, local text retrieval | Authorized extraction, source freshness and independent answer checks |
| GitHub | Source inventory, revision links, signed-in editing and workflow evidence | Scoped backend authorization for private access and automated writes |
| Hugging Face | Model/dataset discovery and a small browser model test | License review, pinned revisions, licensed datasets, hardware and held-out evaluations |
| Courses | Study-resource links and original notes | Exercises and a separately graded assessment; no automatic course completion |
| YouTube or other video | Authorized transcript/text import and video-pipeline design | Authorized media adapter, timestamps, transcription checks and task evaluation |
| Databases | Exported plain text and connector setup guidance | Least-privilege backend connector, account isolation, query limits and deletion tests |
| Feedback and failure memory | Existing event/history and adaptation components | Traceable real observations and repeated controlled retests |
| Fine-tuning | Small NumPy trainer and unexecuted larger-model training adapter routes | Real model/dataset adapter, train/validation/test split, checkpoints and rollback |

Prefer one measurable beginner coding or retrieval task first. Establish a baseline, collect only permitted sources, change one component, evaluate fresh held-out tasks and keep regression results. Training records supplied by a user remain unverified until reproduced. A source count or a planned trial is not mastery.

Official implementation references: [browser inference](https://huggingface.co/docs/transformers.js/en/index), [supervised fine-tuning](https://huggingface.co/docs/trl/en/sft_trainer), [GitHub Pages hosting](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages).

## Plugin and connection boundary

The GitHub connector can access the selected user and organization installations in this assistant. The Hugging Face connector authenticated the Dreamcobots account during this session. Those permissions belong to this assistant session; no credential has been transferred into GitHub Pages. A documentation-search operation on the Hugging Face connector failed, so official web documentation was used instead. No paid jobs were started.

Use the existing Setup Center and Resource Connection Center for the repository's service links. Configure actual Buddy integrations in a private backend or local service, store credentials there, and test a scoped read before enabling writes. ChatGPT plugins, Grok, CodeRabbit, MCP tools and hosting providers must each have their own supported runtime connection and authorization. Public Pages cannot hold provider secrets or become an authenticated multi-user backend by adding buttons.

## Local project reconciliation

A private local inventory compares four identified older Dreamcobots copies against the current repository. The September copy largely overlaps the current project. Three older project trees contain thousands of paths absent from the current repository, including Python bots and tests. These are not automatically executable current bots and have not been silently merged or discarded.

Next: confirm the intended primary folder; deduplicate those trees by content; inspect old entry points, dependencies and original requirements; preserve originals in a versioned private recovery area; port shared capabilities with compatibility tests; then publish only reviewed public-safe material. This is not yet a whole-computer completeness claim.

## Production work still open

1. Complete and reconcile the49conversation sources, attachments and per-requirement evidence. Archive none until complete.
2. Recover and test the additional older local code trees. Preserve original inputs and source hashes.
3. Deploy authentication, isolated user storage, background execution, private connectors and secret management; verify access denial and deletion across users.
4. Connect each promised bot capability to a real artifact-producing handler and verify original behavior, failure handling and human review.
5. Implement actual model/dataset training adapters and run independent held-out evaluations. The small character model is not Buddy's general chat model or AGI.
6. Verify live deployments and rollback for the intended pilot. Passing repository checks and publishing the static site do not certify the entire product.
