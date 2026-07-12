"""
Buddy OS — App Framework

Provides modular tools for universal mobile/desktop app support,
browser-based interfaces, and smart-device connectivity.

Modules:
  - AppRegistry      — register and manage installed apps
  - BrowserToolkit   — browser automation and web-access tools
  - SmartDeviceHub   — IFTTT/smart-home integrations
  - NvidiaToolsHub   — NVIDIA AI/GPU tools (Isaac, Omniverse, CUDA, Jetson)
  - StarlinkManager  — Starlink satellite internet management & resale

GLOBAL AI SOURCES FLOW: participates via buddy_os.py pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from framework import GlobalAISourcesFlow  # noqa: F401


# ===========================================================================
# App Registry
# ===========================================================================

class AppCategory(Enum):
    PRODUCTIVITY = "productivity"
    ENTERTAINMENT = "entertainment"
    COMMUNICATION = "communication"
    UTILITIES = "utilities"
    AI_TOOLS = "ai_tools"
    GAMES = "games"
    SMART_HOME = "smart_home"
    DEVELOPER = "developer"


class AppPlatform(Enum):
    MOBILE = "mobile"
    DESKTOP = "desktop"
    WEB = "web"
    TV = "tv"
    CONSOLE = "console"
    UNIVERSAL = "universal"


@dataclass
class App:
    """Represents a registered application."""

    app_id: str
    name: str
    category: AppCategory
    platforms: list
    version: str = "1.0.0"
    enabled: bool = True
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "app_id": self.app_id,
            "name": self.name,
            "category": self.category.value,
            "platforms": [p if isinstance(p, str) else p.value for p in self.platforms],
            "version": self.version,
            "enabled": self.enabled,
        }


class AppRegistry:
    """Register, enable, disable, and query installed apps."""

    def __init__(self) -> None:
        self._apps: dict[str, App] = {}
        self._counter: int = 0

    def install(
        self,
        name: str,
        category: AppCategory,
        platforms: list,
        version: str = "1.0.0",
        metadata: Optional[dict] = None,
    ) -> App:
        """Install (register) an application."""
        self._counter += 1
        app_id = f"app_{self._counter:04d}"
        app = App(
            app_id=app_id,
            name=name,
            category=category,
            platforms=list(platforms),
            version=version,
            metadata=dict(metadata or {}),
        )
        self._apps[app_id] = app
        return app

    def uninstall(self, app_id: str) -> None:
        self._apps.pop(app_id, None)

    def enable(self, app_id: str) -> App:
        app = self._get(app_id)
        app.enabled = True
        return app

    def disable(self, app_id: str) -> App:
        app = self._get(app_id)
        app.enabled = False
        return app

    def list_apps(
        self,
        category: Optional[AppCategory] = None,
        platform: Optional[AppPlatform] = None,
        enabled_only: bool = False,
    ) -> list[App]:
        apps = list(self._apps.values())
        if category is not None:
            apps = [a for a in apps if a.category == category]
        if platform is not None:
            apps = [
                a for a in apps
                if platform in a.platforms or AppPlatform.UNIVERSAL in a.platforms
            ]
        if enabled_only:
            apps = [a for a in apps if a.enabled]
        return apps

    def get_app(self, app_id: str) -> App:
        return self._get(app_id)

    def _get(self, app_id: str) -> App:
        if app_id not in self._apps:
            raise KeyError(f"App '{app_id}' not found.")
        return self._apps[app_id]


# ===========================================================================
# Browser Toolkit
# ===========================================================================

@dataclass
class BrowserTool:
    """A browser-based tool or automation script."""

    tool_id: str
    name: str
    url: str
    description: str = ""
    enabled: bool = True
    mode: str = "client_safe"
    sandbox_profile: str = "browser_tool_sandbox"
    resource_library_id: str = ""
    approval_required: bool = True

    def to_dict(self) -> dict:
        return {
            "tool_id": self.tool_id,
            "name": self.name,
            "url": self.url,
            "description": self.description,
            "enabled": self.enabled,
            "mode": self.mode,
            "sandbox_profile": self.sandbox_profile,
            "resource_library_id": self.resource_library_id,
            "approval_required": self.approval_required,
        }


class BrowserToolkit:
    """Manage browser-based automation tools and web-app shortcuts."""

    def __init__(self) -> None:
        self._tools: dict[str, BrowserTool] = {}
        self._counter: int = 0

    def add_tool(
        self,
        name: str,
        url: str,
        description: str = "",
        mode: str = "client_safe",
        sandbox_profile: str = "browser_tool_sandbox",
        resource_library_id: str = "",
        approval_required: bool = True,
    ) -> BrowserTool:
        self._counter += 1
        tool_id = f"btool_{self._counter:04d}"
        tool = BrowserTool(
            tool_id=tool_id,
            name=name,
            url=url,
            description=description,
            mode=mode,
            sandbox_profile=sandbox_profile,
            resource_library_id=resource_library_id,
            approval_required=approval_required,
        )
        self._tools[tool_id] = tool
        return tool

    def remove_tool(self, tool_id: str) -> None:
        self._tools.pop(tool_id, None)

    def list_tools(self, enabled_only: bool = False) -> list[BrowserTool]:
        tools = list(self._tools.values())
        if enabled_only:
            tools = [t for t in tools if t.enabled]
        return tools

    def get_tool(self, tool_id: str) -> BrowserTool:
        if tool_id not in self._tools:
            raise KeyError(f"Browser tool '{tool_id}' not found.")
        return self._tools[tool_id]

    def productivity_manifest(self) -> dict:
        """Return browser workspace metadata for dashboards and sandbox launchers."""
        tools = [tool.to_dict() for tool in self.list_tools()]
        return {
            "tool_count": len(tools),
            "client_safe_tools": sum(1 for tool in tools if tool["mode"] == "client_safe"),
            "approval_required_tools": sum(1 for tool in tools if tool["approval_required"]),
            "sandbox_profiles": sorted({tool["sandbox_profile"] for tool in tools}),
            "resource_libraries": sorted({tool["resource_library_id"] for tool in tools if tool["resource_library_id"]}),
            "tools": tools,
        }


# ===========================================================================
# Smart Device Hub
# ===========================================================================

class SmartDeviceProtocol(Enum):
    IFTTT = "ifttt"
    MATTER = "matter"
    ZIGBEE = "zigbee"
    ZWAVE = "zwave"
    WIFI = "wifi"
    THREAD = "thread"


@dataclass
class SmartDevice:
    """A smart-home device managed by the hub."""

    device_id: str
    name: str
    protocol: SmartDeviceProtocol
    room: str = ""
    online: bool = False
    state: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "device_id": self.device_id,
            "name": self.name,
            "protocol": self.protocol.value,
            "room": self.room,
            "online": self.online,
            "state": self.state,
        }


class SmartDeviceHub:
    """Connect and control smart-home / IoT devices."""

    def __init__(self) -> None:
        self._devices: dict[str, SmartDevice] = {}
        self._counter: int = 0

    def add_device(
        self,
        name: str,
        protocol: SmartDeviceProtocol,
        room: str = "",
        initial_state: Optional[dict] = None,
    ) -> SmartDevice:
        self._counter += 1
        device_id = f"sd_{self._counter:04d}"
        device = SmartDevice(
            device_id=device_id,
            name=name,
            protocol=protocol,
            room=room,
            state=dict(initial_state or {}),
        )
        self._devices[device_id] = device
        return device

    def remove_device(self, device_id: str) -> None:
        self._devices.pop(device_id, None)

    def set_online(self, device_id: str, online: bool) -> SmartDevice:
        device = self._get(device_id)
        device.online = online
        return device

    def update_state(self, device_id: str, state_patch: dict) -> SmartDevice:
        device = self._get(device_id)
        device.state.update(state_patch)
        return device

    def list_devices(self, room: Optional[str] = None) -> list[SmartDevice]:
        devices = list(self._devices.values())
        if room is not None:
            devices = [d for d in devices if d.room == room]
        return devices

    def get_device(self, device_id: str) -> SmartDevice:
        return self._get(device_id)

    def _get(self, device_id: str) -> SmartDevice:
        if device_id not in self._devices:
            raise KeyError(f"Smart device '{device_id}' not found.")
        return self._devices[device_id]


# ===========================================================================
# NVIDIA Tools Hub
# ===========================================================================

NVIDIA_TOOLS: list[dict] = [
    {
        "id": "isaac_sdk",
        "name": "NVIDIA Isaac SDK",
        "description": "Robotics development toolkit for autonomous machines.",
        "category": "robotics",
    },
    {
        "id": "jetson",
        "name": "NVIDIA Jetson",
        "description": "Edge AI hardware and software for IoT/robotics.",
        "category": "edge_ai",
    },
    {
        "id": "omniverse",
        "name": "NVIDIA Omniverse",
        "description": "3D simulation and collaboration platform.",
        "category": "simulation",
    },
    {
        "id": "cuda",
        "name": "NVIDIA CUDA",
        "description": "Parallel computing platform and programming model.",
        "category": "compute",
    },
    {
        "id": "tensorrt",
        "name": "NVIDIA TensorRT",
        "description": "High-performance deep learning inference optimizer.",
        "category": "ml_inference",
    },
    {
        "id": "triton",
        "name": "NVIDIA Triton Inference Server",
        "description": "Open-source inference serving software.",
        "category": "ml_serving",
    },
    {
        "id": "nemo",
        "name": "NVIDIA NeMo",
        "description": "Framework for building large language models.",
        "category": "llm",
    },
    {
        "id": "rapids",
        "name": "NVIDIA RAPIDS",
        "description": "GPU-accelerated data science and ML pipelines.",
        "category": "data_science",
    },
]

NVIDIA_MARKUP_PCT: float = 25.0


class NvidiaToolsHub:
    """
    Manage NVIDIA AI/GPU tool integrations.

    Lists all available NVIDIA tools, applies a 25% markup for resale,
    and tracks which tools are activated on the current installation.
    """

    def __init__(self) -> None:
        self._activated: set[str] = set()

    def list_tools(self) -> list[dict]:
        """Return all known NVIDIA tools with their resale prices."""
        return [
            {**tool, "markup_pct": NVIDIA_MARKUP_PCT}
            for tool in NVIDIA_TOOLS
        ]

    def activate_tool(self, tool_id: str) -> dict:
        """Activate an NVIDIA tool by ID."""
        tool = self._find_tool(tool_id)
        self._activated.add(tool_id)
        return {"activated": True, "tool": tool}

    def deactivate_tool(self, tool_id: str) -> dict:
        """Deactivate an NVIDIA tool by ID."""
        self._activated.discard(tool_id)
        return {"activated": False, "tool_id": tool_id}

    def get_activated_tools(self) -> list[dict]:
        """Return details of all currently activated tools."""
        return [
            {**tool, "markup_pct": NVIDIA_MARKUP_PCT}
            for tool in NVIDIA_TOOLS
            if tool["id"] in self._activated
        ]

    def _find_tool(self, tool_id: str) -> dict:
        for tool in NVIDIA_TOOLS:
            if tool["id"] == tool_id:
                return tool
        raise KeyError(f"NVIDIA tool '{tool_id}' not found.")


# ===========================================================================
# Starlink Manager
# ===========================================================================

STARLINK_BASE_PRICE_USD: float = 120.0
STARLINK_HARDWARE_BASE_USD: float = 599.0
STARLINK_MARKUP_PCT: float = 25.0


@dataclass
class StarlinkSubscription:
    """Represents a Starlink subscription for a client."""

    subscription_id: str
    client_name: str
    plan: str
    monthly_usd: float
    hardware_usd: float
    active: bool = True
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "subscription_id": self.subscription_id,
            "client_name": self.client_name,
            "plan": self.plan,
            "monthly_usd": self.monthly_usd,
            "hardware_usd": self.hardware_usd,
            "active": self.active,
        }


STARLINK_PLANS: dict = {
    "residential": {
        "base_monthly_usd": STARLINK_BASE_PRICE_USD,
        "description": "Residential satellite internet service.",
    },
    "roam": {
        "base_monthly_usd": 150.0,
        "description": "Mobile/roaming satellite internet.",
    },
    "business": {
        "base_monthly_usd": 500.0,
        "description": "Business-grade satellite internet.",
    },
    "priority": {
        "base_monthly_usd": 1000.0,
        "description": "Priority throughput for critical operations.",
    },
}


class StarlinkManager:
    """
    Manage and resell Starlink satellite internet subscriptions.

    Applies a 25% markup on all Starlink plans and hardware.
    """

    def __init__(self) -> None:
        self._subscriptions: dict[str, StarlinkSubscription] = {}
        self._counter: int = 0

    def list_plans(self) -> list[dict]:
        """Return available Starlink plans with the marked-up price."""
        result = []
        for plan_id, info in STARLINK_PLANS.items():
            base = info["base_monthly_usd"]
            marked_up = round(base * (1 + STARLINK_MARKUP_PCT / 100), 2)
            hardware_marked_up = round(
                STARLINK_HARDWARE_BASE_USD * (1 + STARLINK_MARKUP_PCT / 100), 2
            )
            result.append(
                {
                    "plan_id": plan_id,
                    "description": info["description"],
                    "base_monthly_usd": base,
                    "marked_up_monthly_usd": marked_up,
                    "hardware_marked_up_usd": hardware_marked_up,
                    "markup_pct": STARLINK_MARKUP_PCT,
                }
            )
        return result

    def create_subscription(
        self,
        client_name: str,
        plan: str,
        custom_monthly_override: Optional[float] = None,
    ) -> StarlinkSubscription:
        """Create a new Starlink subscription for a client."""
        if plan not in STARLINK_PLANS:
            raise ValueError(f"Unknown Starlink plan '{plan}'.")
        base = STARLINK_PLANS[plan]["base_monthly_usd"]
        monthly = custom_monthly_override if custom_monthly_override else round(
            base * (1 + STARLINK_MARKUP_PCT / 100), 2
        )
        hardware = round(STARLINK_HARDWARE_BASE_USD * (1 + STARLINK_MARKUP_PCT / 100), 2)
        self._counter += 1
        subscription_id = f"sl_{self._counter:04d}"
        sub = StarlinkSubscription(
            subscription_id=subscription_id,
            client_name=client_name,
            plan=plan,
            monthly_usd=monthly,
            hardware_usd=hardware,
        )
        self._subscriptions[subscription_id] = sub
        return sub

    def cancel_subscription(self, subscription_id: str) -> StarlinkSubscription:
        """Cancel an active subscription."""
        sub = self._get(subscription_id)
        sub.active = False
        return sub

    def list_subscriptions(self, active_only: bool = False) -> list[StarlinkSubscription]:
        subs = list(self._subscriptions.values())
        if active_only:
            subs = [s for s in subs if s.active]
        return subs

    def get_subscription(self, subscription_id: str) -> StarlinkSubscription:
        return self._get(subscription_id)

    def _get(self, subscription_id: str) -> StarlinkSubscription:
        if subscription_id not in self._subscriptions:
            raise KeyError(f"Subscription '{subscription_id}' not found.")
        return self._subscriptions[subscription_id]
