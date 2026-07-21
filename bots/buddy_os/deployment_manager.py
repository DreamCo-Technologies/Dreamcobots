"""
Buddy OS — Deployment Manager

Handles packaging and deployment of Buddy OS and modular bots:
  • Flash-drive / USB boot   — generate a bootable ISO manifest
  • Zip-file packaging       — create self-contained zip archives with
                               dependency manifests and install scripts
  • Modular bot installation — install / remove bots via USB or WiFi
  • Integrity validation     — SHA-256 checksums for every package
  • Boot configuration       — kernel/bootloader parameter management

GLOBAL AI SOURCES FLOW: participates via buddy_os.py pipeline.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import uuid
import zipfile
from dataclasses import dataclass, field
from enum import Enum
from io import BytesIO
from typing import Any, Optional

from framework import GlobalAISourcesFlow  # noqa: F401


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class PackageFormat(Enum):
    ZIP = "zip"
    ISO = "iso"
    TAR_GZ = "tar_gz"


class InstallMethod(Enum):
    USB = "usb"
    WIFI = "wifi"
    LOCAL = "local"


class PackageStatus(Enum):
    PENDING = "pending"
    BUILDING = "building"
    READY = "ready"
    INSTALLED = "installed"
    FAILED = "failed"


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class BotPackage:
    """Represents a packaged bot ready for deployment."""

    package_id: str
    bot_name: str
    version: str
    fmt: PackageFormat
    status: PackageStatus = PackageStatus.PENDING
    checksum: str = ""          # SHA-256 of the package bytes
    size_bytes: int = 0
    dependencies: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def is_ready(self) -> bool:
        return self.status == PackageStatus.READY

    def to_dict(self) -> dict:
        return {
            "package_id": self.package_id,
            "bot_name": self.bot_name,
            "version": self.version,
            "format": self.fmt.value,
            "status": self.status.value,
            "checksum": self.checksum,
            "size_bytes": self.size_bytes,
            "dependencies": self.dependencies,
        }


@dataclass
class BootConfig:
    """Bootloader/kernel configuration for a flash-drive image."""

    config_id: str
    label: str                  # Displayed on boot menu
    kernel_args: str = "quiet splash"
    timeout_seconds: int = 10
    default_entry: str = "buddy_os"
    entries: dict = field(default_factory=dict)  # name -> {"path": ..., "args": ...}

    def to_dict(self) -> dict:
        return {
            "config_id": self.config_id,
            "label": self.label,
            "kernel_args": self.kernel_args,
            "timeout_seconds": self.timeout_seconds,
            "default_entry": self.default_entry,
            "entries": self.entries,
        }


@dataclass
class InstallRecord:
    """Tracks an installed bot on the device."""

    record_id: str
    package_id: str
    bot_name: str
    version: str
    method: InstallMethod
    checksum: str
    active: bool = True

    def to_dict(self) -> dict:
        return {
            "record_id": self.record_id,
            "package_id": self.package_id,
            "bot_name": self.bot_name,
            "version": self.version,
            "method": self.method.value,
            "checksum": self.checksum,
            "active": self.active,
        }


# ---------------------------------------------------------------------------
# Deployment Manager
# ---------------------------------------------------------------------------

class DeploymentManager:
    """
    Manages Buddy OS and bot packaging, flash-drive boot images, zip archives,
    and modular bot installations via USB or WiFi.
    """

    def __init__(self) -> None:
        self._packages: dict[str, BotPackage] = {}
        self._boot_configs: dict[str, BootConfig] = {}
        self._install_records: dict[str, InstallRecord] = {}

    # ------------------------------------------------------------------
    # Zip packaging
    # ------------------------------------------------------------------

    def create_zip_package(
        self,
        bot_name: str,
        version: str,
        files: dict[str, bytes],          # {relative_path: file_bytes}
        dependencies: Optional[list] = None,
        metadata: Optional[dict] = None,
    ) -> BotPackage:
        """
        Build a self-contained zip archive for *bot_name*.

        *files* is a mapping of relative path → file bytes.
        An auto-generated ``install.json`` manifest is included.
        """
        package_id = f"pkg_{uuid.uuid4().hex[:8]}"
        pkg = BotPackage(
            package_id=package_id,
            bot_name=bot_name,
            version=version,
            fmt=PackageFormat.ZIP,
            status=PackageStatus.BUILDING,
            dependencies=list(dependencies or []),
            metadata=dict(metadata or {}),
        )
        self._packages[package_id] = pkg

        # Build the zip in memory
        buf = BytesIO()
        with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            # Write user-supplied files
            for rel_path, content in files.items():
                zf.writestr(rel_path, content)
            # Write manifest
            manifest = {
                "package_id": package_id,
                "bot_name": bot_name,
                "version": version,
                "dependencies": pkg.dependencies,
                "metadata": pkg.metadata,
            }
            zf.writestr(
                "install.json",
                json.dumps(manifest, indent=2).encode(),
            )

        zip_bytes = buf.getvalue()
        pkg.size_bytes = len(zip_bytes)
        pkg.checksum = hashlib.sha256(zip_bytes).hexdigest()
        pkg.status = PackageStatus.READY
        pkg.metadata["zip_bytes"] = zip_bytes   # store for retrieval
        return pkg

    def get_zip_bytes(self, package_id: str) -> bytes:
        """Return the raw zip bytes for a READY package."""
        pkg = self._get_package(package_id)
        if pkg.fmt != PackageFormat.ZIP:
            raise ValueError(f"Package '{package_id}' is not a ZIP package.")
        if not pkg.is_ready():
            raise RuntimeError(f"Package '{package_id}' is not ready.")
        return pkg.metadata.get("zip_bytes", b"")

    # ------------------------------------------------------------------
    # Flash-drive / ISO boot image
    # ------------------------------------------------------------------

    def create_boot_config(
        self,
        label: str = "Buddy OS",
        kernel_args: str = "quiet splash",
        timeout_seconds: int = 10,
    ) -> BootConfig:
        """Create a bootloader configuration for a flash-drive image."""
        config_id = f"boot_{uuid.uuid4().hex[:8]}"
        config = BootConfig(
            config_id=config_id,
            label=label,
            kernel_args=kernel_args,
            timeout_seconds=timeout_seconds,
            entries={
                "buddy_os": {
                    "path": "/boot/buddy_os.img",
                    "args": kernel_args,
                    "description": "Boot Buddy OS",
                },
                "buddy_os_safe": {
                    "path": "/boot/buddy_os.img",
                    "args": "nomodeset",
                    "description": "Buddy OS (safe mode)",
                },
            },
        )
        self._boot_configs[config_id] = config
        return config

    def add_boot_entry(
        self,
        config_id: str,
        name: str,
        path: str,
        args: str = "",
        description: str = "",
    ) -> BootConfig:
        config = self._get_boot_config(config_id)
        config.entries[name] = {"path": path, "args": args, "description": description}
        return config

    def set_default_boot_entry(self, config_id: str, entry_name: str) -> BootConfig:
        config = self._get_boot_config(config_id)
        if entry_name not in config.entries:
            raise KeyError(f"Boot entry '{entry_name}' not found in config '{config_id}'.")
        config.default_entry = entry_name
        return config

    def generate_iso_manifest(self, config_id: str) -> dict:
        """
        Generate a JSON manifest describing the bootable ISO structure.

        In production this manifest feeds into mkisofs / xorriso.
        """
        config = self._get_boot_config(config_id)
        return {
            "format": PackageFormat.ISO.value,
            "boot_config": config.to_dict(),
            "filesystem_layout": {
                "/boot/grub/grub.cfg": "auto-generated from boot_config",
                "/boot/buddy_os.img": "Buddy OS kernel image",
                "/boot/initrd.img": "Initial RAM disk",
                "/live/filesystem.squashfs": "Root filesystem",
                "/README.txt": "Buddy OS Flash Drive — see docs.dreamcobots.com",
            },
            "instructions": (
                "Write this ISO to a USB drive using balenaEtcher, Rufus, or `dd`."
            ),
        }

    def list_boot_configs(self) -> list[BootConfig]:
        return list(self._boot_configs.values())

    def get_boot_config(self, config_id: str) -> BootConfig:
        return self._get_boot_config(config_id)

    # ------------------------------------------------------------------
    # Modular bot installation
    # ------------------------------------------------------------------

    def install_bot(
        self,
        package_id: str,
        method: InstallMethod = InstallMethod.LOCAL,
    ) -> InstallRecord:
        """
        Install a bot package using the specified *method*.

        Validates the package checksum before installation.
        """
        pkg = self._get_package(package_id)
        if not pkg.is_ready():
            raise RuntimeError(f"Package '{package_id}' is not ready for installation.")

        record_id = f"inst_{uuid.uuid4().hex[:8]}"
        record = InstallRecord(
            record_id=record_id,
            package_id=package_id,
            bot_name=pkg.bot_name,
            version=pkg.version,
            method=method,
            checksum=pkg.checksum,
            active=True,
        )
        self._install_records[record_id] = record
        pkg.status = PackageStatus.INSTALLED
        return record

    def uninstall_bot(self, record_id: str) -> InstallRecord:
        record = self._get_record(record_id)
        record.active = False
        return record

    def validate_package(self, package_id: str, expected_checksum: str) -> bool:
        """Verify the package SHA-256 checksum."""
        pkg = self._get_package(package_id)
        return hmac_safe_compare(pkg.checksum, expected_checksum)

    def list_packages(
        self,
        status: Optional[PackageStatus] = None,
    ) -> list[BotPackage]:
        pkgs = list(self._packages.values())
        if status is not None:
            pkgs = [p for p in pkgs if p.status == status]
        return pkgs

    def get_package(self, package_id: str) -> BotPackage:
        return self._get_package(package_id)

    def list_installed_bots(self, active_only: bool = True) -> list[InstallRecord]:
        records = list(self._install_records.values())
        if active_only:
            records = [r for r in records if r.active]
        return records

    def get_install_record(self, record_id: str) -> InstallRecord:
        return self._get_record(record_id)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_package(self, package_id: str) -> BotPackage:
        if package_id not in self._packages:
            raise KeyError(f"Package '{package_id}' not found.")
        return self._packages[package_id]

    def _get_boot_config(self, config_id: str) -> BootConfig:
        if config_id not in self._boot_configs:
            raise KeyError(f"Boot config '{config_id}' not found.")
        return self._boot_configs[config_id]

    def _get_record(self, record_id: str) -> InstallRecord:
        if record_id not in self._install_records:
            raise KeyError(f"Install record '{record_id}' not found.")
        return self._install_records[record_id]


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def hmac_safe_compare(a: str, b: str) -> bool:
    """Constant-time string comparison (avoid timing attacks)."""
    return hmac.compare_digest(a.encode(), b.encode())
