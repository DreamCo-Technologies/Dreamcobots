# Buddy Device Discovery Roadmap

## Objective
Give users the clearest possible view of devices Buddy can legitimately discover from their device and approved integrations.

## Discovery sources

1. Operating-system device inventory
2. Bluetooth/BLE APIs
3. User-enabled local-network discovery
4. USB enumeration
5. Vendor SDKs
6. Vendor cloud APIs
7. Platform-approved vehicle APIs
8. Smart-home hubs
9. Enterprise device-management APIs
10. User-imported device manifests

## Completeness model

The UI should show a discovery-health indicator explaining which sources were checked and which were unavailable because of OS permissions, missing adapters, network isolation, or vendor restrictions. Buddy must never claim "all devices" when an OS or vendor prevents discovery.

## Device cards

Every card has: discovered, compatible, paired, authorized, controllable, unsupported, or unavailable status. Users can open a capability list and see exactly why a capability is or is not available.

## Continuous refresh

With permission, the Device Center can refresh on demand and optionally monitor changes. New devices appear as candidates, but control remains disabled until authorization.

## Compatibility learning

Every successful integration becomes a versioned adapter test. Failed integrations become diagnostic cases and regression tests. Buddy Bootcamp uses these cases to improve device compatibility without silently changing permissions.
