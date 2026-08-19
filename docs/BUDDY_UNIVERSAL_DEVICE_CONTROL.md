# Buddy Universal Device Control + Downloads

## Goal
Let users discover and control compatible electronics they own or are explicitly authorized to control, across Bluetooth/BLE, local Wi-Fi/LAN, USB and supported platform/vendor APIs.

## Important boundary
Being connected to the same network or being Bluetooth-visible does **not** automatically grant permission. Buddy must require user authorization, device pairing, an approved integration, or another legitimate access mechanism. It must never bypass authentication, pairing, access controls, encryption, or vendor security.

## Device center
Users should see a live inventory with:

- device name
- category
- manufacturer/model when available
- connection type
- connection strength/status
- capabilities
- permissions granted
- required adapter/driver
- security state
- supported Buddy commands
- last seen
- battery/power state where available
- firmware/version where available
- sandbox/compatibility score

## Control model

`Discover → Identify → Ask permission → Pair/authenticate → Sandbox → Capability test → Show controls → Execute → Audit`

Sensitive commands require confirmation. High-risk operations remain blocked unless the integration explicitly supports them and the user has appropriate authorization.

## Supported capability families

- media playback/volume
- displays
- lights
- thermostats
- printers
- scanners
- cameras
- microphones
- speakers
- keyboards/controllers
- sensors
- smart-home devices
- POS peripherals
- supported vehicle interfaces
- computers/tablets/phones through platform-approved APIs
- industrial/IoT equipment through authorized protocols

"Universal" means a growing adapter ecosystem, not a claim that every device has a public controllable API.

## Downloadable Buddy

The repository should publish a release/download center for supported platforms, with signed artifacts where feasible:

- macOS
- Windows
- Linux
- Android
- iOS through the appropriate app-distribution process
- Web/PWA where supported

The download page should detect the platform, show the correct installer, display version/build/checksum information, and link to release notes. The GitHub Pages experience can provide the download center, while native app stores are used where platform rules require them.

## Device-control safety

- least privilege by default
- explicit per-device permissions
- visible connected-device indicator
- revoke-all button
- audit log
- pairing/authentication required
- no silent LAN scanning beyond the user-approved discovery flow
- no credential harvesting
- no bypass of security controls
- safe command allowlists for sensitive equipment
- emergency stop/disable controls where supported
