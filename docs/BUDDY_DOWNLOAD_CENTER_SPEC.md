# Buddy Download Center

## User experience

The public GitHub Pages front page should expose a prominent **Download Buddy** button. The download center detects the user's platform and presents the appropriate supported build.

## Release channels

- Stable — production-oriented signed/reproducible release
- Beta — broader integration testing
- Nightly — developers/testers
- Source — repository and build instructions

## Platform targets

- macOS desktop
- Windows desktop
- Linux desktop
- Android
- iOS through App Store/TestFlight or another Apple-approved distribution path
- Web/PWA where appropriate

## Every release should publish

- version
- platform/architecture
- release notes
- checksum
- signature/provenance when available
- minimum OS version
- known limitations
- rollback version
- security advisories

## Installation principle

The download experience should feel like a normal application installation, while respecting each operating system's security and distribution rules. GitHub Pages is the discovery/download surface; platform stores or approved installation mechanisms handle platforms that prohibit arbitrary web installation.

## Updates

Buddy should check for updates only with user permission and should provide:

- update available notification
- release notes
- install now/later
- rollback where supported
- automatic security updates when the user explicitly enables them

## Device onboarding

After installation Buddy can show a permissioned Device Center:

`Discover → identify → user approval → pair/authenticate → sandbox → test → enable`

Discovery alone never grants control.
