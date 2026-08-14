# Buddy Universal Equipment Compatibility

## Goal
Buddy should be able to assist users regardless of the equipment they already own, rather than forcing a single hardware vendor.

"Any equipment" means broad compatibility through adapters and standards, not an unsafe promise that every device is natively supported on day one.

## Compatibility layers

1. **Device discovery** — identify OS, model, capabilities, ports, network state and available APIs.
2. **Protocol detection** — USB, Bluetooth/BLE, Wi-Fi, Ethernet, NFC, serial, HID, MIDI, MQTT, HTTP(S), WebSocket, vendor SDKs and other documented protocols.
3. **Adapter registry** — map equipment to a standard capability interface.
4. **Driver/API bridge** — use the operating system or vendor-supported driver/API where required.
5. **Capability normalization** — expose common operations through a stable Buddy interface.
6. **Sandbox** — test a device integration before allowing production actions.
7. **Health monitoring** — latency, disconnects, errors, firmware/version compatibility and battery/network state where available.
8. **Fallback routing** — if one device or interface fails, select another compatible path when available.

## Example normalized capabilities

- camera.capture
- microphone.record
- speaker.play
- printer.print
- scanner.scan
- display.render
- keyboard.input
- pointer.input
- card_reader.accept
- terminal.present
- barcode.scan
- receipt.print
- sensor.read
- machine.telemetry
- industrial.protocol.read
- file.transfer
- network.connect

## Payments equipment

DreamPayments should support multiple terminal/POS/card-reader vendors through authorized SDKs, APIs and adapters. Buddy must never bypass device security, payment cryptography, firmware controls, PCI requirements, or vendor authorization.

## Bring-your-own-equipment policy

A merchant should be able to tell Buddy:

> "I already own this equipment. Can I use it?"

Buddy should return:

- compatibility status
- required adapter/driver
- supported capabilities
- missing capabilities
- setup steps
- supported payment providers
- estimated migration cost
- security/compliance requirements
- fallback equipment options

## Benchmark

Each adapter gets measured for:

- detection success
- connection success
- command success
- latency
- reliability
- recovery after disconnect
- compatibility coverage
- security checks
- sandbox test pass rate
- maintenance status

No device receives a "mastered" status until repeatable tests demonstrate the required capability.
