# FreeCodeCamp Bootcamp: full video and course coverage gate

**Purpose:** prove what is covered, what is only indexed, what needs classification, and what Buddy has actually studied.

## Source scope

The official source is [freeCodeCamp.org on YouTube](https://www.youtube.com/@freecodecamp), channel ID `UC8butISFwT-Wl7EV0hUK0BQ`, together with the official interactive learning platform at [freeCodeCamp Learn](https://www.freecodecamp.org/learn/).

The video archive must include all public uploads discoverable from the official channel, not only selected playlists or popular full courses. Reconcile channel uploads, pagination, unique video IDs, unavailable/deleted/private records where observable, and relevant video formats such as long-form courses, Shorts, and public livestream recordings. Keep partner videos and linked external courses attributed to their actual publishers.

The official channel currently displays approximately 2.3K videos. DreamCo's committed catalog has 1,740 rows and explicitly marks its inventory partial; an earlier CI artifact recorded 1,741. These are not interchangeable totals. Capture the exact current upstream count with a fresh complete enumeration and reconcile it before calling the archive complete.

## Current verified gaps in the committed snapshot

- **1,740** catalog rows, with `inventory.complete=false` and no persisted upstream expected count.
- **519** videos are tagged `other_or_unclassified` and require human taxonomy review (about 29.8% of the committed snapshot).
- The roadmap has **22** video subject tracks, **7** core certifications, **5** additional language/specialist certifications, and **7** curriculum primitives.
- The interactive curriculum inventory records a dated snapshot of 37 superblocks, 38 chapters, 217 modules, 779 unique blocks, and 14,038 challenges. It is marked for refresh; aggregate counts do not prove every current lesson/challenge ID, test, prerequisite, and project has been inventoried.
- The transcript rights manifest has **zero approved transcript assets**. No transcript-based detailed guide or transcript evaluation is authorized by the current manifest.
- A catalog row or queue item is not a completed lesson. No model training or mastery may be inferred from metadata.

These are dated repository observations, not permanent upstream totals.

## Required per-video Bootcamp record

Every unique official channel video ID must have:
1. Stable video ID, canonical URL, publisher/channel, title, publication date and duration where available.
2. Inventory provenance: retrieval time, enumerator/version, source page or uploads playlist, expected count, observed count, pagination completion, unavailable IDs, duplicate count, and source snapshot digest.
3. One or more subject tags, skill level where defensible, content format, and review state. Unclassified items remain visible in a human-review queue; never silently drop them.
4. Candidate course/division mappings with rationale and explicit owner approval where required.
5. A study state distinct from metadata discovery, rights approval, guide authoring, sandbox completion, assessment, and mastery.
6. A link to original source material and attribution. Partner material retains its original publisher identity.

## Original DreamCo course requirements

For every subject track, certification, and eligible video, DreamCo must build its own original teaching package:
- Prerequisites, outcomes, concepts, definitions and a coherent lesson sequence.
- Original explanations, worked examples, code, commands and architecture diagrams where relevant.
- At least three graduated exercises, with hints, acceptance criteria and deterministic tests.
- A practical lab/project, debugging exercise, common failure modes and security/privacy/cost notes.
- Knowledge checks with answer explanations, rubrics and answer keys.
- A capstone, unseen transfer task, teach-back, spaced repetition and remediation path.
- Versioned source references, provenance, technical review, accessibility review and freshness/revalidation date.
- Mapping to the appropriate 55 domain divisions and 65 MasterBot lanes. Shared foundations may be available broadly; specialty ownership remains evidence- and owner-reviewed.

Detailed source-based guides require the relevant source material and separate study, derivative-summary and evaluation permissions. Otherwise Buddy must use permitted official course materials or independently authored explanations of the underlying skills, cite the source, and keep transcript-derived work blocked. Never fabricate chapter timestamps, demonstrations, instructor claims or code from titles and metadata.

## Required verification

The Bootcamp workflow runs a coverage auditor after building the video queue and division routes. The report measures upstream inventory completeness, taxonomy gaps, all 22 video subject tracks, official curriculum inventory, 55 domain divisions, 65 MasterBot lanes, one queue and route record per catalog video, approved guides, authorized transcript assets, and separate model-training rights.

The audit intentionally reports `INCOMPLETE` while any gate remains open. CI validates the auditor and publishes the report without pretending that unresolved source rights or incomplete guides have passed.

## Commands

```bash
python tools/build_freecodecamp_study_guides.py --out-dir /tmp/freecodecamp-study-guides
python tools/audit_freecodecamp_bootcamp_coverage.py \
  --queue /tmp/freecodecamp-study-guides/detailed-study-guide-queue.json \
  --routes /tmp/freecodecamp-source-routes.json \
  --out /tmp/freecodecamp-coverage-audit.json
```

Use `--require-complete` only for a release gate after inventory, taxonomy, route, guide, and rights evidence genuinely satisfy every completion criterion.
