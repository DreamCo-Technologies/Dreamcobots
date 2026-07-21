"""DreamCo Cloud Bot — AWS competitor for hosting and server management."""
import sys
import os
import uuid
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, get_tier_config, get_upgrade_path
from bots.dreamco_cloud_bot.tiers import BOT_FEATURES, get_bot_tier_info
from framework import GlobalAISourcesFlow  # noqa: F401


class DreamCoCloudBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class DreamCoCloudBotError(Exception):
    """Raised when a cloud operation fails."""


class ServerInstance:
    """Represents a managed server/compute instance."""

    def __init__(self, instance_id: str, name: str, region: str,
                 instance_type: str, user_id: str = "user"):
        self.instance_id = instance_id
        self.name = name
        self.region = region
        self.instance_type = instance_type
        self.user_id = user_id
        self.status = "running"
        self.ip_address = f"10.0.{hash(instance_id) % 256}.{hash(name) % 256}"
        self.created_at = time.time()
        self.tags: dict = {}

    def to_dict(self) -> dict:
        return {
            "instance_id": self.instance_id,
            "name": self.name,
            "region": self.region,
            "instance_type": self.instance_type,
            "user_id": self.user_id,
            "status": self.status,
            "ip_address": self.ip_address,
            "created_at": self.created_at,
            "tags": dict(self.tags),
        }


class DatabaseInstance:
    """Represents a managed database instance."""

    def __init__(self, db_id: str, name: str, engine: str,
                 version: str, storage_gb: int, user_id: str = "user"):
        self.db_id = db_id
        self.name = name
        self.engine = engine
        self.version = version
        self.storage_gb = storage_gb
        self.user_id = user_id
        self.status = "available"
        self.endpoint = f"{name.lower()}.db.dreamco.ai"
        self.created_at = time.time()

    def to_dict(self) -> dict:
        return {
            "db_id": self.db_id,
            "name": self.name,
            "engine": self.engine,
            "version": self.version,
            "storage_gb": self.storage_gb,
            "user_id": self.user_id,
            "status": self.status,
            "endpoint": self.endpoint,
            "created_at": self.created_at,
        }


class DreamCoCloudBot:
    """
    DreamCo Cloud Bot — autonomous cloud hosting and server management platform
    competing with Amazon Web Services (AWS).

    Provides server provisioning, database hosting, load balancing, auto-scaling,
    CDN, serverless functions, and full cloud infrastructure management.

    Tiers
    -----
    FREE       : 1 server, 512 MB RAM, 10 GB storage, static hosting.
    PRO        : 10 servers, 8 GB RAM, 200 GB storage, load balancer, managed DB.
    ENTERPRISE : Unlimited servers, multi-region, Kubernetes, serverless, SLA.
    """

    INSTANCE_LIMITS = {
        Tier.FREE: 1,
        Tier.PRO: 10,
        Tier.ENTERPRISE: None,
    }

    DB_LIMITS = {
        Tier.FREE: 0,
        Tier.PRO: 3,
        Tier.ENTERPRISE: None,
    }

    REGIONS = {
        Tier.FREE: ["us-east-1"],
        Tier.PRO: ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"],
        Tier.ENTERPRISE: [
            "us-east-1", "us-east-2", "us-west-1", "us-west-2",
            "eu-west-1", "eu-central-1", "ap-southeast-1",
            "ap-northeast-1", "sa-east-1", "ca-central-1",
        ],
    }

    INSTANCE_TYPES = {
        Tier.FREE: ["dc1.nano"],
        Tier.PRO: ["dc1.nano", "dc1.small", "dc1.medium", "dc1.large", "dc2.xlarge"],
        Tier.ENTERPRISE: [
            "dc1.nano", "dc1.small", "dc1.medium", "dc1.large",
            "dc2.xlarge", "dc2.2xlarge", "dc2.4xlarge",
            "gpu1.small", "gpu1.large",
        ],
    }

    DB_ENGINES = ["postgresql", "mysql", "redis", "mongodb"]

    def __init__(self, tier: Tier = Tier.FREE, user_id: str = "user"):
        self.tier = tier
        self.config = get_tier_config(tier)
        self.user_id = user_id
        self._instances: dict = {}
        self._databases: dict = {}
        self._functions: dict = {}
        self._load_balancers: dict = {}

    # ------------------------------------------------------------------
    # Tier enforcement
    # ------------------------------------------------------------------

    def _require(self, feature: str) -> None:
        if feature not in BOT_FEATURES[self.tier.value]:
            upgrade = get_upgrade_path(self.tier)
            raise DreamCoCloudBotTierError(
                f"Feature '{feature}' is not available on the {self.config.name} tier. "
                f"Upgrade to {upgrade} for access."
            )

    def _check_instance_limit(self) -> None:
        limit = self.INSTANCE_LIMITS[self.tier]
        if limit is not None and len(self._instances) >= limit:
            raise DreamCoCloudBotTierError(
                f"Server instance limit of {limit} reached on {self.config.name} tier. "
                f"Upgrade to launch more instances."
            )

    def _check_db_limit(self) -> None:
        limit = self.DB_LIMITS[self.tier]
        if limit == 0:
            raise DreamCoCloudBotTierError(
                f"Managed databases not available on {self.config.name} tier. "
                f"Upgrade to PRO or ENTERPRISE."
            )
        if limit is not None and len(self._databases) >= limit:
            raise DreamCoCloudBotTierError(
                f"Database instance limit of {limit} reached on {self.config.name} tier. "
                f"Upgrade to create more databases."
            )

    # ------------------------------------------------------------------
    # Server management
    # ------------------------------------------------------------------

    def launch_instance(self, name: str, instance_type: str = "dc1.nano",
                        region: str = "us-east-1") -> ServerInstance:
        """
        Launch a new server instance.

        Parameters
        ----------
        name : str
            Human-readable instance name.
        instance_type : str
            Compute instance type (e.g. 'dc1.small').
        region : str
            Deployment region (e.g. 'us-east-1').

        Returns
        -------
        ServerInstance
        """
        self._check_instance_limit()

        allowed_regions = self.REGIONS[self.tier]
        if region not in allowed_regions:
            raise DreamCoCloudBotTierError(
                f"Region '{region}' not available on {self.config.name} tier. "
                f"Available regions: {allowed_regions}. Upgrade for more regions."
            )

        allowed_types = self.INSTANCE_TYPES[self.tier]
        if instance_type not in allowed_types:
            raise DreamCoCloudBotTierError(
                f"Instance type '{instance_type}' not available on {self.config.name} tier. "
                f"Available types: {allowed_types}. Upgrade for larger instances."
            )

        instance = ServerInstance(
            instance_id=str(uuid.uuid4()),
            name=name,
            region=region,
            instance_type=instance_type,
            user_id=self.user_id,
        )
        self._instances[instance.instance_id] = instance
        return instance

    def get_instance(self, instance_id: str) -> ServerInstance:
        """Return an existing instance by ID."""
        if instance_id not in self._instances:
            raise DreamCoCloudBotError(f"Instance '{instance_id}' not found.")
        return self._instances[instance_id]

    def list_instances(self) -> list:
        """Return all server instances."""
        return [inst.to_dict() for inst in self._instances.values()]

    def stop_instance(self, instance_id: str) -> dict:
        """Stop a running instance."""
        inst = self.get_instance(instance_id)
        inst.status = "stopped"
        return {"instance_id": instance_id, "status": "stopped"}

    def terminate_instance(self, instance_id: str) -> dict:
        """Permanently terminate an instance."""
        if instance_id not in self._instances:
            raise DreamCoCloudBotError(f"Instance '{instance_id}' not found.")
        del self._instances[instance_id]
        return {"instance_id": instance_id, "terminated": True}

    def list_regions(self) -> list:
        """Return available deployment regions for this tier."""
        return list(self.REGIONS[self.tier])

    def list_instance_types(self) -> list:
        """Return available instance types for this tier."""
        return list(self.INSTANCE_TYPES[self.tier])

    # ------------------------------------------------------------------
    # Static site hosting
    # ------------------------------------------------------------------

    def deploy_static_site(self, name: str, domain: str = "") -> dict:
        """
        Deploy a static website to DreamCo Cloud hosting.

        Parameters
        ----------
        name : str
            Site name.
        domain : str
            Optional custom domain.
        """
        site_id = str(uuid.uuid4())[:8]
        default_url = f"https://{name.lower().replace(' ', '-')}.dreamco.app"
        return {
            "site_id": site_id,
            "name": name,
            "url": default_url,
            "custom_domain": domain if domain else None,
            "ssl": True,
            "status": "deployed",
            "tier": self.tier.value,
        }

    # ------------------------------------------------------------------
    # Managed databases (PRO+)
    # ------------------------------------------------------------------

    def create_database(self, name: str, engine: str = "postgresql",
                        storage_gb: int = 10) -> DatabaseInstance:
        """
        Create a managed database instance.
        Requires PRO tier or higher.
        """
        self._check_db_limit()

        if engine.lower() not in self.DB_ENGINES:
            raise DreamCoCloudBotError(
                f"Database engine '{engine}' not supported. "
                f"Supported: {self.DB_ENGINES}"
            )

        db = DatabaseInstance(
            db_id=str(uuid.uuid4()),
            name=name,
            engine=engine.lower(),
            version="latest",
            storage_gb=storage_gb,
            user_id=self.user_id,
        )
        self._databases[db.db_id] = db
        return db

    def get_database(self, db_id: str) -> DatabaseInstance:
        """Return an existing database instance by ID."""
        if db_id not in self._databases:
            raise DreamCoCloudBotError(f"Database '{db_id}' not found.")
        return self._databases[db_id]

    def list_databases(self) -> list:
        """Return all managed database instances."""
        return [db.to_dict() for db in self._databases.values()]

    # ------------------------------------------------------------------
    # Load balancer (PRO+)
    # ------------------------------------------------------------------

    def create_load_balancer(self, name: str, instance_ids: list) -> dict:
        """
        Create a load balancer across multiple instances.
        Requires PRO tier or higher.
        """
        if self.tier == Tier.FREE:
            raise DreamCoCloudBotTierError(
                f"Load balancer not available on {self.config.name} tier. "
                f"Upgrade to PRO or ENTERPRISE."
            )
        lb_id = str(uuid.uuid4())
        lb = {
            "lb_id": lb_id,
            "name": name,
            "instance_ids": list(instance_ids),
            "dns": f"{name.lower().replace(' ', '-')}.lb.dreamco.ai",
            "status": "active",
            "tier": self.tier.value,
        }
        self._load_balancers[lb_id] = lb
        return lb

    # ------------------------------------------------------------------
    # Serverless functions (ENTERPRISE)
    # ------------------------------------------------------------------

    def deploy_function(self, name: str, runtime: str, code: str) -> dict:
        """
        Deploy a serverless function.
        Requires ENTERPRISE tier.
        """
        if self.tier != Tier.ENTERPRISE:
            raise DreamCoCloudBotTierError(
                f"Serverless functions not available on {self.config.name} tier. "
                f"Upgrade to ENTERPRISE."
            )
        fn_id = str(uuid.uuid4())
        fn = {
            "function_id": fn_id,
            "name": name,
            "runtime": runtime,
            "invoke_url": f"https://functions.dreamco.ai/{fn_id}",
            "status": "deployed",
            "tier": self.tier.value,
        }
        self._functions[fn_id] = fn
        return fn

    # ------------------------------------------------------------------
    # Cloud stats
    # ------------------------------------------------------------------

    def get_cloud_stats(self) -> dict:
        """Return cloud resource usage statistics."""
        inst_limit = self.INSTANCE_LIMITS[self.tier]
        db_limit = self.DB_LIMITS[self.tier]
        return {
            "instances_used": len(self._instances),
            "instances_limit": inst_limit,
            "instances_remaining": (inst_limit - len(self._instances)) if inst_limit is not None else None,
            "databases_used": len(self._databases),
            "databases_limit": db_limit if db_limit != 0 else None,
            "functions_deployed": len(self._functions),
            "load_balancers": len(self._load_balancers),
            "regions_available": len(self.REGIONS[self.tier]),
            "tier": self.tier.value,
        }

    # ------------------------------------------------------------------
    # Tier info
    # ------------------------------------------------------------------

    def get_tier_info(self) -> dict:
        """Return tier configuration and feature details."""
        return get_bot_tier_info(self.tier)

    # ------------------------------------------------------------------
    # Chat interface
    # ------------------------------------------------------------------

    def chat(self, message: str) -> dict:
        """Unified natural-language chat interface."""
        msg = message.lower()

        if any(kw in msg for kw in ("launch", "new server", "create instance", "provision")):
            inst = self.launch_instance("My Server")
            return {
                "message": f"Server '{inst.name}' launched in {inst.region}. IP: {inst.ip_address}",
                "data": inst.to_dict(),
            }

        if any(kw in msg for kw in ("list servers", "my servers", "instances")):
            instances = self.list_instances()
            return {
                "message": f"You have {len(instances)} server instance(s).",
                "data": instances,
            }

        if any(kw in msg for kw in ("regions", "available regions")):
            regions = self.list_regions()
            return {"message": f"Available regions: {', '.join(regions)}", "data": regions}

        if any(kw in msg for kw in ("database", "create db", "new database")):
            if self.tier == Tier.FREE:
                return {
                    "message": "Managed databases require PRO tier. Upgrade to unlock.",
                    "data": {"upgrade_required": True},
                }
            db = self.create_database("My Database")
            return {
                "message": f"Database '{db.name}' created. Endpoint: {db.endpoint}",
                "data": db.to_dict(),
            }

        if any(kw in msg for kw in ("stats", "usage", "resources")):
            stats = self.get_cloud_stats()
            return {"message": "Cloud resource statistics retrieved.", "data": stats}

        if "tier" in msg or "features" in msg or "upgrade" in msg:
            info = self.get_tier_info()
            return {"message": f"Current tier: {info['tier']}. Features: {info['features']}", "data": info}

        return {
            "message": (
                "DreamCo Cloud Bot ready. I can launch servers, host static sites, "
                "manage databases (PRO+), create load balancers (PRO+), and deploy "
                "serverless functions (ENTERPRISE). What would you like to build?"
            ),
            "data": {"tier": self.tier.value},
        }
