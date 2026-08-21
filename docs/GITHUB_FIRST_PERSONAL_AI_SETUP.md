# GitHub-First Personal AI Setup

## Purpose

This guide explains the architecture for running DreamCo's Personal AI product from the GitHub-controlled repository while keeping the customer experience beginner-friendly.

## What GitHub is responsible for

GitHub is the source-control and automation layer for DreamCo:

- source code
- product configuration
- Personal AI contracts
- skill definitions
- benchmark definitions
- tests
- GitHub Actions
- version history
- pull requests
- release evidence
- documentation

## What GitHub should NOT store

Never commit:

- passwords
- API keys
- raw payment credentials
- private customer media
- private conversation logs
- private memory databases
- unapproved copyrighted media
- production secrets

Customer data belongs in the authorized runtime/storage layer, not in the public repository.

## Beginner path

A beginner should see:

**Create my AI → Tell Buddy what I need → Add knowledge → Teach a skill → Try it → Save it**

They should not need to understand Git branches or pull requests.

## Developer path

A developer can use:

```text
GitHub repository
  -> configuration
  -> local runtime
  -> tests
  -> GitHub Actions
  -> deployment
  -> monitored runtime
```

Personal AI configurations should be versionable so a developer can reproduce a configuration without exposing private data.

## Personal AI package

A portable AI package should contain only safe configuration and references:

- identity metadata
- personality configuration
- skill manifests
- tool capability contracts
- benchmark tasks
- routing preferences
- memory policy
- source references
- provenance records
- version

Private source contents remain outside the public package unless the owner explicitly exports them.

## GitHub Actions quality gates

Before a Personal AI package is promoted:

1. schema validation
2. permission validation
3. provenance validation
4. secret scan
5. rights/asset manifest validation
6. skill contract validation
7. benchmark smoke tests
8. regression tests
9. build/type checks
10. deployment/package verification

A failed gate should explain the problem in beginner language while linking to technical details.

## Rollback

Every published Personal AI configuration should have:

- version identifier
- creation time
- previous known-good version
- benchmark evidence
- change summary
- rollback action

Rollback must restore configuration and skill behavior without silently deleting user data.

## Cost efficiency

Buddy should calculate the cheapest verified route before choosing an expensive model where possible.

Routing should consider:

- capability fit
- quality evidence
- cost
- latency
- privacy
- availability
- plan entitlement

A premium route requires entitlement and explicit approval according to the current policy.

## GitHub Pages

Static pages can provide the beginner experience, documentation, demos, and local-first planning UI. Any operation requiring private server credentials, durable background execution, payment processing, or protected customer data must use an authenticated backend rather than pretending GitHub Pages alone provides those capabilities.

The current repository already contains a GitHub Pages-to-backend bridge pattern. Reuse and test that canonical path rather than creating another deployment path.

## First production milestone

The minimum sellable technical loop is:

```text
Create Personal AI
 -> save configuration
 -> add one authorized source
 -> create one skill
 -> run one benchmark
 -> show result
 -> store approved memory
 -> repeat task
 -> show improvement
 -> offer paid upgrade
 -> enforce entitlement
```

Do not expand the product surface until this loop is reliable.
