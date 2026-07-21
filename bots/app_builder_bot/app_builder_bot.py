"""App Builder Bot — tier-aware application project creation and scaffolding."""
import sys, os
import uuid
from datetime import datetime, timezone
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, get_tier_config, get_upgrade_path
from bots.app_builder_bot.tiers import BOT_FEATURES, get_bot_tier_info
from framework import GlobalAISourcesFlow  # noqa: F401


class AppBuilderBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class AppBuilderBot:
    """Tier-aware application project creation and scaffolding bot."""

    PROJECT_LIMITS = {Tier.FREE: 1, Tier.PRO: 10, Tier.ENTERPRISE: None}
    APP_TYPES = ["web", "mobile", "desktop", "api", "fullstack"]

    SCAFFOLDS = {
        "web": {
            "directories": ["src/", "src/components/", "src/pages/", "src/styles/", "public/", "tests/"],
            "files": ["src/App.tsx", "src/index.tsx", "public/index.html", "package.json", "tsconfig.json", "README.md"],
            "commands": ["npm install", "npm run dev"],
        },
        "mobile": {
            "directories": ["src/", "src/screens/", "src/components/", "src/navigation/", "src/services/", "assets/"],
            "files": ["src/App.tsx", "app.json", "package.json", "babel.config.js", "README.md"],
            "commands": ["npm install", "npx expo start"],
        },
        "desktop": {
            "directories": ["src/", "src/main/", "src/renderer/", "src/preload/", "assets/"],
            "files": ["src/main/index.ts", "src/renderer/App.tsx", "package.json", "electron-builder.yml", "README.md"],
            "commands": ["npm install", "npm run dev"],
        },
        "api": {
            "directories": ["app/", "app/routers/", "app/models/", "app/schemas/", "app/services/", "tests/"],
            "files": ["app/main.py", "app/routers/health.py", "requirements.txt", "Dockerfile", "README.md"],
            "commands": ["pip install -r requirements.txt", "uvicorn app.main:app --reload"],
        },
        "fullstack": {
            "directories": ["frontend/", "frontend/src/", "backend/", "backend/app/", "shared/", "docker/"],
            "files": ["frontend/src/App.tsx", "backend/app/main.py", "docker-compose.yml", "README.md"],
            "commands": ["docker-compose up", "npm run dev (frontend)", "uvicorn main:app (backend)"],
        },
    }

    HOURS_PER_FEATURE = {"web": 4, "mobile": 6, "desktop": 5, "api": 3, "fullstack": 8}

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._projects: dict = {}

    def _active_project_count(self) -> int:
        return sum(1 for p in self._projects.values() if p.get("status") != "archived")

    def create_project(self, name: str, app_type: str) -> dict:
        """Create a new project, returns project dict with id."""
        limit = self.PROJECT_LIMITS[self.tier]
        if limit is not None and self._active_project_count() >= limit:
            raise AppBuilderBotTierError(
                f"Project limit of {limit} reached on {self.config.name} tier. "
                "Archive existing projects or upgrade."
            )
        if app_type not in self.APP_TYPES:
            raise ValueError(f"Invalid app_type '{app_type}'. Must be one of: {self.APP_TYPES}")

        project_id = str(uuid.uuid4())[:8]
        project = {
            "id": project_id,
            "name": name,
            "app_type": app_type,
            "features": [],
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "tier": self.tier.value,
        }
        self._projects[project_id] = project
        return project

    def add_feature(self, project_id: str, feature: str) -> dict:
        """Add a feature to an existing project."""
        if project_id not in self._projects:
            raise KeyError(f"Project '{project_id}' not found.")
        project = self._projects[project_id]
        if feature not in project["features"]:
            project["features"].append(feature)
        return project

    def generate_code_scaffold(self, project_id: str) -> dict:
        """Generate the code structure/scaffold for the project."""
        if project_id not in self._projects:
            raise KeyError(f"Project '{project_id}' not found.")
        project = self._projects[project_id]
        app_type = project["app_type"]
        scaffold = self.SCAFFOLDS.get(app_type, self.SCAFFOLDS["web"]).copy()

        result = {
            "project_id": project_id,
            "project_name": project["name"],
            "app_type": app_type,
            "scaffold": scaffold,
            "custom_features": project["features"],
            "tier": self.tier.value,
        }
        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            result["code_generation_enabled"] = True
            result["premium_templates"] = [f"{app_type}-auth", f"{app_type}-dashboard", f"{app_type}-payments"]
        if self.tier == Tier.ENTERPRISE:
            result["ai_generated"] = True
            result["ci_cd_config"] = {
                "ci_tool": "GitHub Actions",
                "cd_tool": "AWS CodeDeploy",
                "pipeline": [".github/workflows/ci.yml", ".github/workflows/cd.yml"],
            }
        return result

    def estimate_development_time(self, project_id: str) -> dict:
        """Estimate development time in hours and days."""
        if project_id not in self._projects:
            raise KeyError(f"Project '{project_id}' not found.")
        project = self._projects[project_id]
        app_type = project["app_type"]
        base_hours = {"web": 80, "mobile": 120, "desktop": 100, "api": 60, "fullstack": 200}.get(app_type, 80)
        feature_hours = len(project["features"]) * self.HOURS_PER_FEATURE.get(app_type, 4)
        total_hours = base_hours + feature_hours
        multiplier = 1.0 if self.tier == Tier.ENTERPRISE else (0.9 if self.tier == Tier.PRO else 1.0)
        total_hours = int(total_hours * multiplier)

        return {
            "project_id": project_id,
            "project_name": project["name"],
            "app_type": app_type,
            "base_hours": base_hours,
            "feature_hours": feature_hours,
            "total_hours": total_hours,
            "estimated_days": round(total_hours / 8, 1),
            "estimated_weeks": round(total_hours / 40, 1),
            "team_size_recommended": 1 if total_hours < 200 else (2 if total_hours < 500 else 3),
            "tier": self.tier.value,
        }

    def describe_tier(self) -> str:
        info = get_bot_tier_info(self.tier)
        lines = [
            f"=== {info['name']} App Builder Bot Tier ===",
            f"Price: ${info['price_usd_monthly']:.2f}/month",
            f"Support: {info['support_level']}",
            "Features:",
        ]
        for f in info["features"]:
            lines.append(f"  \u2713 {f}")
        output = "\n".join(lines)
        print(output)
        return output
