# DreamCo Beginner-First Standard

Buddy is for beginners. The repository should feel understandable before it feels powerful.

## Golden rule
Every feature must answer four questions immediately:

1. **What is this?**
2. **Why would I use it?**
3. **What happens if I click it?**
4. **What should I do next?**

## Beginner experience

- Plain-English labels before technical labels
- One recommended next step on important pages
- Safe defaults
- Explain errors in normal language
- Show the fix beside the error when possible
- Never require users to understand Git, branches, commits, CI, APIs, containers, or cloud infrastructure before using Buddy
- Advanced controls remain available under an Advanced section
- Every destructive action gets a clear confirmation
- Every automation shows what it will change before execution when practical
- Every important action has a progress/status/result view

## GitHub made simple

Translate GitHub concepts into Buddy language:

| GitHub term | Buddy explanation |
|---|---|
| Repository | Your project's home |
| Branch | A safe workspace for changes |
| Commit | A saved checkpoint |
| Pull request | A proposed change for review |
| Issue | A problem or improvement to track |
| Action | An automated job |
| Workflow | A recipe for automation |
| Failed check | Something that needs attention |
| Merge | Put approved changes together |
| Release | A version people can install |
| Artifact | A file produced by a build |
| Environment variable | A private setting |
| Dependency | Software your project relies on |

## Every page

Each major page should have:

- **Start here** button
- **What this does** summary
- **Recommended action**
- **Status**
- **Problems found**
- **Fix** button when safe/possible
- **Learn** link
- **Advanced** controls
- **History**
- **Undo/rollback** where supported

## Actions page

Actions should be presented as cards rather than raw workflow names. Each card shows:

`Purpose → Current status → Last run → What failed → Recommended fix → Run → View details`

Technical logs remain available, but are not the first screen.

## Pull requests

Buddy should explain:

- what changed
- why it changed
- risk level
- tests run
- tests that failed
- recommended decision
- files affected
- rollback plan

The user always controls final approval/merge unless they explicitly enable automation.

## Learning mode

Every advanced screen can offer a **Teach me** action that explains the current concept using the user's project as the example.

## Accessibility

Use readable contrast, keyboard navigation, large touch targets, descriptive buttons, mobile layouts, and plain-language status messages.

## Quality gate

A beginner should be able to install Buddy, open the repository, find the next recommended action, understand an error, and know how to recover without reading a Git manual.
