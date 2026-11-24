# FreeCodeCamp YouTube learning library

## Source and discovery

DreamCo's FreeCodeCamp learning library uses the verified official channel
[freeCodeCamp.org](https://www.youtube.com/@freecodecamp) with channel ID
`UC8butISFwT-Wl7EV0hUK0BQ`. The cataloger uses the official YouTube Data API
v3 channel uploads playlist, follows every `nextPageToken`, de-duplicates video
IDs, and retrieves metadata in batches of up to 50 videos.

Run it manually after setting `YOUTUBE_DATA_API_KEY` in the environment:

```bash
python tools/catalog_freecodecamp_youtube.py --out artifacts/learning/freecodecamp-youtube-catalog.json
```

The API key is never written to the output. Default CI does not call YouTube or
download media. The cataloger records titles, descriptions, tags, publication
dates, duration, video links, and heuristic subject/skill-level labels only.

## Learning taxonomy

The first-pass multi-label taxonomy covers programming foundations, Python,
JavaScript/TypeScript, HTML/CSS, frontend, backend/APIs, SQL/databases, data
engineering, data science, machine learning, deep learning, generative AI,
agents/automation, DevOps/cloud, cybersecurity, computer science, algorithms,
math/statistics, mobile, game development, UX/design, career/interview,
business/product, and Linux/networking.

A video may belong to multiple categories. Classification is a discovery aid,
not a certification. Every record retains the title, tags, and source link;
ambiguous records go to `other_needs_review`. MasterBot assignments are
candidates only until the division owner approves them.

## Learning together

The catalog is a shared reference index for users and Buddy. From each video
record, the Bootcamp can create a linked lesson plan, original exercises,
quizzes, coding labs, skill maps, and benchmark tasks. Learner progress and
model-training evidence remain separate. Buddy must cite the video and use
timestamps when a lesson was actually inspected.

## Rights and platform boundaries

The default ownership class is `THIRD_PARTY_REFERENCE_ONLY`. Cataloging a
public video does not grant permission to download it, copy its transcript,
train on its contents, redistribute it, or sell derived material. No video,
audio, captions, transcript, comments, or viewer information is fetched by
this tool. Any future transcript workflow needs a separate lawful-access and
rights review. Original exercises must be independently authored, quality
reviewed, and checked for substantial similarity before training approval.

## Completion evidence

A catalog run may report complete only when playlist pagination is exhausted,
all IDs are de-duplicated, metadata retrieval counts are reconciled, and the
retrieval timestamp is stored. This is metadata catalog completeness—not proof
that every lesson was watched, categorized by an expert, licensed for training,
or completed by a learner.
