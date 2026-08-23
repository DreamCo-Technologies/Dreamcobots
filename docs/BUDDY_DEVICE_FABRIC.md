# Buddy Universal Device Fabric

## Goal

Allow Buddy to discover, classify, pair with, and use compatible nearby devices through supported operating-system and hardware APIs while respecting user permissions and platform security.

Buddy should understand not just that a device exists, but what capabilities it exposes.

## Device capability model

```text
DEVICE
 ├── identity
 ├── transport
 │    ├── Bluetooth Classic
 │    ├── BLE
 │    ├── Wi-Fi / LAN
 │    ├── AirPlay / Cast / DLNA where supported
 │    └── OS-specific device APIs
 ├── capabilities
 │    ├── audio-output
 │    ├── audio-input
 │    ├── display
 │    ├── video-output
 │    ├── camera
 │    ├── microphone
 │    ├── game-controller
 │    ├── keyboard
 │    ├── mouse
 │    ├── sensor
 │    ├── storage
 │    └── other declared services
 ├── permissions
 ├── connection state
 └── health / battery / availability
```

## Device classes

Buddy should recognize classes such as:

- phones/tablets;
- computers;
- televisions/displays;
- speakers;
- headphones/earbuds;
- microphones;
- cameras;
- game controllers and supported game systems;
- keyboards/mice;
- printers;
- sensors and wearables;
- smart-home devices;
- vehicles and other supported accessories.

Classification must be based on observed platform/service metadata, not assumptions from a device name alone.

## Capability-aware routing

Examples:

```text
Need audio → choose compatible speaker/headphones
Need video → choose compatible display/TV
Need presentation → choose display + audio if required
Need game input → choose compatible controller
Need voice input → choose authorized microphone
Need local file transfer → choose authorized compatible transport
```

Buddy should select the best available device using capability compatibility, user preference, connection quality, battery/state, proximity when available, privacy level and task requirements.

## Pairing and permissions

Buddy cannot silently pair with arbitrary devices or bypass operating-system security. Discovery, pairing, connection, microphone/camera access, screen sharing and similar privileged operations require the platform's permission/consent mechanisms.

A device that is merely discoverable is not automatically authorized for use.

## Connection lifecycle

```text
DISCOVER
 ↓
IDENTIFY
 ↓
CLASSIFY
 ↓
READ DECLARED CAPABILITIES
 ↓
CHECK PERMISSIONS
 ↓
PAIR / CONNECT WITH AUTHORIZATION
 ↓
VERIFY CAPABILITIES
 ↓
USE
 ↓
MONITOR
 ↓
DISCONNECT / RELEASE
```

## Capability verification

After connection, Buddy should verify the actual services/features it can use. A device name such as `TV` is not sufficient proof that video casting is supported.

## Privacy

Device inventory, identifiers, location/proximity signals, microphones, cameras and screen-sharing state are sensitive. Store only what is necessary, use explicit permissions, and expose connection status to the user.

## Failure handling

If a device is unavailable or incompatible, Buddy should select another authorized device when possible and explain the fallback when it materially changes the experience.

## Platform adapters

Implement the fabric behind adapters rather than hard-coding Bluetooth logic into Buddy. Candidate adapters include:

- iOS/iPadOS native connectivity and media APIs;
- macOS native connectivity and media APIs;
- Android Bluetooth/media APIs;
- Windows device/media APIs;
- Linux BlueZ and desktop media APIs;
- supported TV/casting protocols;
- supported game-system APIs.

Availability varies by platform, device and permissions.
