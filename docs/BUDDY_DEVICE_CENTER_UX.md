# Buddy Device Center UX

## Requirement
Buddy should show users the devices that are discoverable through the operating system, approved Bluetooth/BLE APIs, authorized local-network discovery mechanisms, USB enumeration, or supported vendor/platform integrations.

The UI must distinguish **visible/discovered** from **authorized/controllable**.

## Device inventory

Every discovered device card should show:

- Name
- Manufacturer/model when available
- Device category
- Connection transport
- Online/offline/unknown status
- Signal/connection quality when available
- Battery/power state when available
- Capabilities
- Compatibility score
- Required permissions
- Pair/authenticate button
- Test button
- Control button only after authorization
- Last seen
- Remove/forget button

## Filters

Users can filter by:

- All
- Bluetooth/BLE
- Wi-Fi/LAN
- USB
- Cloud/vendor API
- Vehicle
- Home
- Office
- POS
- Computer
- Phone/tablet
- Audio
- Display
- Printer
- Camera
- Sensor
- Other

## Privacy

Discovery is user initiated or explicitly enabled. Buddy should explain what discovery can observe before starting. It must not use discovery to defeat access controls or obtain credentials.

## Control states

`Discovered → Awaiting permission → Paired/authenticated → Sandbox testing → Authorized → Controllable → Revoked/forgotten`

A device can be displayed even when Buddy cannot control it. This prevents the UI from misleading users about compatibility.
