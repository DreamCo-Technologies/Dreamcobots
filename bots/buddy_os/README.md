# Buddy OS

Advanced operating-system-like bot for the DreamCobots ecosystem.

## Overview

Buddy OS runs on **any device** — smartphone, tablet, desktop, smart TV, or gaming console — and provides a unified control layer for device management, Bluetooth/WiFi connectivity, screen casting, app management, smart-home integrations, hardware protocols, robust security, and flexible deployment.

## Features

| Module | Description |
|---|---|
| **Device Manager** | Universal compatibility: TVs, gaming consoles, phones, tablets, computers (Apple, Google, Windows, Linux, Samsung, Sony, Microsoft) |
| **Bluetooth Engine** | Device discovery, pairing, trust, connection, and file transfer (OPP/FTP) |
| **WiFi Engine** | Network scanning, WPA2/WPA3 authentication, hotspot mode, and IoT device pairing over WiFi |
| **Cast Engine** | Screen casting via Google Cast, Apple AirPlay, Miracast, HDMI, DLNA |
| **App Registry** | Install, enable, disable apps across mobile, desktop, web, TV, and console platforms |
| **Browser Toolkit** | Browser-based tool shortcuts and web-app management |
| **Smart Device Hub** | IoT/smart-home control via IFTTT, Matter, Zigbee, Z-Wave, Wi-Fi, Thread |
| **Hardware Protocols** | UART, I2C, SPI, and OBD-II (automotive diagnostics) hardware communication |
| **Security Manager** | Device tokens, encryption key management, secure PIN pairing, cloud/local sync mode, tamper-evident audit log |
| **Deployment Manager** | Zip packaging, flash-drive bootable ISO, and modular bot installation via USB or WiFi |
| **NVIDIA Tools Hub** | Isaac SDK, Jetson, Omniverse, CUDA, TensorRT, Triton, NeMo, RAPIDS — with 25% markup |
| **Starlink Manager** | Satellite internet plans and subscription management with 25% markup resale |

## Tiers

| Tier | Price | Paired Devices | Cast Targets | Key Features |
|---|---|---|---|---|
| Free | $0/month | 3 | 1 | Devices, Bluetooth, WiFi, Security |
| Pro | $49/month | 25 | 10 | + Hardware Protocols, Deployment, Flash Boot |
| Enterprise | $199/month | Unlimited | Unlimited | + Cloud Sync, White Label, MDM |

## Quick Start

```python
from bots.buddy_os import BuddyOS, Tier
from bots.buddy_os import (
    DeviceType, DevicePlatform, CastProtocol, ContentType,
    WiFiSecurity, InstallMethod,
)

# Create Buddy OS
buddy = BuddyOS(tier=Tier.PRO)

# Connect a device
phone = buddy.device_manager.register_device(
    "My iPhone", DeviceType.PHONE, DevicePlatform.APPLE, os_version="17.0"
)
buddy.device_manager.connect(phone.device_id)

# Pair a Bluetooth device
buddy.bluetooth.add_discovered_device("AA:BB:CC:DD:EE:FF", "JBL Charge 5", rssi=-55)
buddy.bluetooth.pair_device("AA:BB:CC:DD:EE:FF")
buddy.bluetooth.connect("AA:BB:CC:DD:EE:FF")

# Connect to WiFi
buddy.wifi.add_discovered_network("HomeNet", "AA:BB:CC:DD:EE:01", security=WiFiSecurity.WPA2)
conn = buddy.wifi.connect("HomeNet", password="mypassword")

# Pair an IoT device over WiFi
smart_light = buddy.wifi.pair_iot_device("Living Room Light", "AA:BB:CC:00:00:01",
                                          ip_address="192.168.1.20", device_type="light")

# Use hardware protocols
ch = buddy.hardware.uart.open_channel("/dev/ttyUSB0", baud_rate=9600)
sensor = buddy.hardware.i2c.add_device(0x48, "Temperature Sensor")
obd = buddy.hardware.obd2.open_session("/dev/ttyUSB1", vehicle_vin="1HGCM82633A123456")

# Security: issue tokens and set sync mode
raw_token, token = buddy.security.issue_token("MyLaptop", scopes=["read"])
buddy.security.set_sync_mode(__import__('bots.buddy_os.security_manager', fromlist=['SyncMode']).SyncMode.CLOUD)

# Package and deploy bots
pkg = buddy.deployment.create_zip_package("MyBot", "1.0.0",
    files={"main.py": b"print('hello')"})
record = buddy.deployment.install_bot(pkg.package_id, method=InstallMethod.USB)

# Create a bootable flash-drive configuration
boot_cfg = buddy.deployment.create_boot_config(label="Buddy OS v1.0")
manifest = buddy.deployment.generate_iso_manifest(boot_cfg.config_id)

# Cast to a screen
recv = buddy.cast.add_receiver("Living Room TV", CastProtocol.GOOGLE_CAST, ip_address="192.168.1.50")
session = buddy.cast.start_cast(recv.receiver_id, ContentType.VIDEO, "https://example.com/video.mp4")

# System status (now includes WiFi, hardware, security, deployment)
print(buddy.system_status())

# Chat interface (BuddyAI compatible)
response = buddy.chat("wifi status")
print(response["message"])
```

## Directory Structure

```
bots/buddy_os/
├── buddy_os.py              # Main BuddyOS class
├── tiers.py                 # FREE/PRO/ENTERPRISE tiers + feature flags
├── device_manager.py        # Universal device compatibility
├── bluetooth_engine.py      # Bluetooth pairing and file transfer
├── wifi_engine.py           # WiFi scanning, connection, hotspot, IoT pairing
├── cast_engine.py           # Screen casting (Cast/AirPlay/Miracast/HDMI)
├── app_framework.py         # App registry, browser tools, smart devices,
│                            #   NVIDIA tools, Starlink manager
├── hardware_protocols.py    # UART, I2C, SPI, OBD-II hardware protocols
├── security_manager.py      # Token auth, encryption, secure pairing,
│                            #   cloud/local sync, audit log
├── deployment_manager.py    # Zip packaging, ISO/flash-drive boot,
│                            #   modular bot install (USB/WiFi)
├── __init__.py
└── README.md
```

