# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""
R&D Marketplace for the DreamAIInvent Hub.

Expands the marketplace to include:
  - Electronics firms
  - Circuit designers
  - AI specialists
  - Robotics manufacturers
  - IoT solution providers

Features:
  - Directory listings with search and filter
  - Forums for discussions and prototyping topics
  - Live prototyping tool posts
  - Testing outcome sharing
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Directory enums
# ---------------------------------------------------------------------------

class DirectoryCategory(Enum):
    ELECTRONICS_FIRM = "electronics_firm"
    CIRCUIT_DESIGNER = "circuit_designer"
    AI_SPECIALIST = "ai_specialist"
    ROBOTICS_MANUFACTURER = "robotics_manufacturer"
    IOT_PROVIDER = "iot_provider"
    SEMICONDUCTOR = "semiconductor"
    CONTRACT_MANUFACTURER = "contract_manufacturer"
    MATERIALS_SUPPLIER = "materials_supplier"


class ServiceType(Enum):
    DESIGN = "design"
    MANUFACTURING = "manufacturing"
    CONSULTING = "consulting"
    LICENSING = "licensing"
    DISTRIBUTION = "distribution"
    TESTING_CERTIFICATION = "testing_certification"
    SOFTWARE_FIRMWARE = "software_firmware"
    AI_INTEGRATION = "ai_integration"


class ListingStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    FEATURED = "featured"
    PENDING_REVIEW = "pending_review"


# ---------------------------------------------------------------------------
# Forum enums
# ---------------------------------------------------------------------------

class ForumCategory(Enum):
    GENERAL = "general"
    PROTOTYPING = "prototyping"
    AI_ROBOTICS = "ai_robotics"
    IOT = "iot"
    PATENTS = "patents"
    FUNDING = "funding"
    MANUFACTURING = "manufacturing"
    PARTNERSHIPS = "partnerships"


class PostType(Enum):
    DISCUSSION = "discussion"
    PROTOTYPING_SHOWCASE = "prototyping_showcase"
    TEST_OUTCOME = "test_outcome"
    QUESTION = "question"
    RESOURCE = "resource"
    ANNOUNCEMENT = "announcement"


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class DirectoryListing:
    """A company or individual listed in the R&D marketplace directory."""

    listing_id: str
    name: str
    category: DirectoryCategory
    services: list
    description: str
    location: str = ""
    website: str = ""
    contact_email: str = ""
    specialisations: list = field(default_factory=list)
    certifications: list = field(default_factory=list)
    min_order_usd: float = 0.0
    rating: float = 0.0
    review_count: int = 0
    status: ListingStatus = ListingStatus.ACTIVE
    verified: bool = False

    def to_dict(self) -> dict:
        return {
            "listing_id": self.listing_id,
            "name": self.name,
            "category": self.category.value,
            "services": [s.value for s in self.services],
            "description": self.description,
            "location": self.location,
            "website": self.website,
            "specialisations": self.specialisations,
            "certifications": self.certifications,
            "min_order_usd": self.min_order_usd,
            "rating": self.rating,
            "review_count": self.review_count,
            "status": self.status.value,
            "verified": self.verified,
        }


@dataclass
class ForumPost:
    """A post in the DreamAIInvent Hub forum."""

    post_id: str
    author_id: str
    title: str
    content: str
    category: ForumCategory
    post_type: PostType
    tags: list = field(default_factory=list)
    replies: list = field(default_factory=list)
    upvotes: int = 0
    views: int = 0
    pinned: bool = False
    attachments: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "post_id": self.post_id,
            "author_id": self.author_id,
            "title": self.title,
            "content": self.content,
            "category": self.category.value,
            "post_type": self.post_type.value,
            "tags": self.tags,
            "replies": self.replies,
            "upvotes": self.upvotes,
            "views": self.views,
            "pinned": self.pinned,
            "attachments": self.attachments,
        }


@dataclass
class PrototypingTool:
    """A live prototyping resource shared in the marketplace."""

    tool_id: str
    name: str
    description: str
    tool_type: str
    author_id: str
    demo_url: str = ""
    source_url: str = ""
    tags: list = field(default_factory=list)
    upvotes: int = 0
    forks: int = 0

    def to_dict(self) -> dict:
        return {
            "tool_id": self.tool_id,
            "name": self.name,
            "description": self.description,
            "tool_type": self.tool_type,
            "author_id": self.author_id,
            "demo_url": self.demo_url,
            "source_url": self.source_url,
            "tags": self.tags,
            "upvotes": self.upvotes,
            "forks": self.forks,
        }


# ---------------------------------------------------------------------------
# Marketplace
# ---------------------------------------------------------------------------

class RDMarketplace:
    """
    R&D Marketplace directory and forum engine for the DreamAIInvent Hub.
    """

    def __init__(self) -> None:
        self._listings: dict[str, DirectoryListing] = {}
        self._posts: dict[str, ForumPost] = {}
        self._tools: dict[str, PrototypingTool] = {}
        self._listing_counter: int = 0
        self._post_counter: int = 0
        self._tool_counter: int = 0

        self._seed_listings()
        self._seed_posts()

    # ------------------------------------------------------------------
    # Directory management
    # ------------------------------------------------------------------

    def add_listing(self, listing: DirectoryListing) -> str:
        self._listings[listing.listing_id] = listing
        return listing.listing_id

    def create_listing(
        self,
        name: str,
        category: DirectoryCategory,
        services: list,
        description: str,
        **kwargs,
    ) -> DirectoryListing:
        self._listing_counter += 1
        listing_id = f"LST-{self._listing_counter:04d}"
        listing = DirectoryListing(
            listing_id=listing_id,
            name=name,
            category=category,
            services=services,
            description=description,
            **kwargs,
        )
        self._listings[listing_id] = listing
        return listing

    def search_directory(
        self,
        query: str = "",
        category: Optional[DirectoryCategory] = None,
        service_type: Optional[ServiceType] = None,
        min_rating: float = 0.0,
        verified_only: bool = False,
    ) -> list:
        """Search and filter directory listings."""
        results = list(self._listings.values())

        if category:
            results = [r for r in results if r.category == category]
        if service_type:
            results = [r for r in results if service_type in r.services]
        if min_rating > 0:
            results = [r for r in results if r.rating >= min_rating]
        if verified_only:
            results = [r for r in results if r.verified]
        if query:
            q = query.lower()
            results = [
                r for r in results
                if q in r.name.lower()
                or q in r.description.lower()
                or any(q in s.lower() for s in r.specialisations)
            ]
        # Active/featured first, sorted by rating
        results = [
            r for r in results
            if r.status in (ListingStatus.ACTIVE, ListingStatus.FEATURED)
        ]
        results.sort(key=lambda x: (x.status == ListingStatus.FEATURED, x.rating), reverse=True)
        return [r.to_dict() for r in results]

    def get_listing(self, listing_id: str) -> Optional[DirectoryListing]:
        return self._listings.get(listing_id)

    def list_categories(self) -> list:
        return [c.value for c in DirectoryCategory]

    # ------------------------------------------------------------------
    # Forum
    # ------------------------------------------------------------------

    def create_post(
        self,
        author_id: str,
        title: str,
        content: str,
        category: ForumCategory,
        post_type: PostType = PostType.DISCUSSION,
        tags: Optional[list] = None,
    ) -> ForumPost:
        self._post_counter += 1
        post_id = f"POST-{self._post_counter:04d}"
        post = ForumPost(
            post_id=post_id,
            author_id=author_id,
            title=title,
            content=content,
            category=category,
            post_type=post_type,
            tags=tags or [],
        )
        self._posts[post_id] = post
        return post

    def reply_to_post(self, post_id: str, author_id: str, content: str) -> bool:
        post = self._posts.get(post_id)
        if not post:
            return False
        post.replies.append({"author_id": author_id, "content": content})
        return True

    def upvote_post(self, post_id: str) -> bool:
        post = self._posts.get(post_id)
        if not post:
            return False
        post.upvotes += 1
        return True

    def view_post(self, post_id: str) -> Optional[ForumPost]:
        post = self._posts.get(post_id)
        if post:
            post.views += 1
        return post

    def list_posts(
        self,
        category: Optional[ForumCategory] = None,
        post_type: Optional[PostType] = None,
        tag: Optional[str] = None,
    ) -> list:
        posts = list(self._posts.values())
        if category:
            posts = [p for p in posts if p.category == category]
        if post_type:
            posts = [p for p in posts if p.post_type == post_type]
        if tag:
            posts = [p for p in posts if tag.lower() in [t.lower() for t in p.tags]]
        # Pinned first, then by upvotes
        posts.sort(key=lambda x: (x.pinned, x.upvotes), reverse=True)
        return [p.to_dict() for p in posts]

    # ------------------------------------------------------------------
    # Prototyping tools
    # ------------------------------------------------------------------

    def submit_tool(
        self,
        author_id: str,
        name: str,
        description: str,
        tool_type: str,
        demo_url: str = "",
        source_url: str = "",
        tags: Optional[list] = None,
    ) -> PrototypingTool:
        self._tool_counter += 1
        tool_id = f"TOOL-{self._tool_counter:04d}"
        tool = PrototypingTool(
            tool_id=tool_id,
            name=name,
            description=description,
            tool_type=tool_type,
            author_id=author_id,
            demo_url=demo_url,
            source_url=source_url,
            tags=tags or [],
        )
        self._tools[tool_id] = tool
        return tool

    def upvote_tool(self, tool_id: str) -> bool:
        tool = self._tools.get(tool_id)
        if not tool:
            return False
        tool.upvotes += 1
        return True

    def fork_tool(self, tool_id: str) -> bool:
        tool = self._tools.get(tool_id)
        if not tool:
            return False
        tool.forks += 1
        return True

    def list_tools(self, tag: Optional[str] = None) -> list:
        tools = list(self._tools.values())
        if tag:
            tools = [t for t in tools if tag.lower() in [tg.lower() for tg in t.tags]]
        tools.sort(key=lambda x: x.upvotes, reverse=True)
        return [t.to_dict() for t in tools]

    def get_tool(self, tool_id: str) -> Optional[PrototypingTool]:
        return self._tools.get(tool_id)

    # ------------------------------------------------------------------
    # Seed data
    # ------------------------------------------------------------------

    def _seed_listings(self) -> None:
        seed = [
            DirectoryListing(
                listing_id="DIR-ELEC-001",
                name="CircuitCraft Electronics",
                category=DirectoryCategory.ELECTRONICS_FIRM,
                services=[ServiceType.DESIGN, ServiceType.MANUFACTURING, ServiceType.TESTING_CERTIFICATION],
                description="Full-service electronics ODM — from schematic to mass production.",
                location="Shenzhen, China",
                specialisations=["IoT modules", "wearable electronics", "PCB assembly"],
                certifications=["ISO 9001", "UL", "CE", "FCC"],
                min_order_usd=5000.0,
                rating=4.6,
                review_count=84,
                status=ListingStatus.FEATURED,
                verified=True,
            ),
            DirectoryListing(
                listing_id="DIR-CIRC-001",
                name="Precision Circuit Designers",
                category=DirectoryCategory.CIRCUIT_DESIGNER,
                services=[ServiceType.DESIGN, ServiceType.CONSULTING],
                description="Boutique RF and mixed-signal circuit design for demanding applications.",
                location="Boston, MA",
                specialisations=["RF engineering", "analog design", "PCB layout"],
                certifications=["IPC-A-610"],
                rating=4.9,
                review_count=37,
                status=ListingStatus.FEATURED,
                verified=True,
            ),
            DirectoryListing(
                listing_id="DIR-AI-001",
                name="NeuralForge Labs",
                category=DirectoryCategory.AI_SPECIALIST,
                services=[ServiceType.AI_INTEGRATION, ServiceType.SOFTWARE_FIRMWARE, ServiceType.CONSULTING],
                description="Embedded AI and computer-vision solutions for robotics and IoT.",
                location="San Francisco, CA",
                specialisations=["edge AI", "computer vision", "NLP", "TinyML"],
                rating=4.7,
                review_count=55,
                status=ListingStatus.FEATURED,
                verified=True,
            ),
            DirectoryListing(
                listing_id="DIR-ROB-001",
                name="Apex Robotics Manufacturing",
                category=DirectoryCategory.ROBOTICS_MANUFACTURER,
                services=[ServiceType.MANUFACTURING, ServiceType.DESIGN, ServiceType.TESTING_CERTIFICATION],
                description="ISO-certified robotics manufacturer for commercial and industrial automation.",
                location="Detroit, MI",
                specialisations=["servo systems", "industrial robots", "cobots", "CNC fabrication"],
                certifications=["ISO 9001", "ISO 13849"],
                min_order_usd=10000.0,
                rating=4.8,
                review_count=102,
                status=ListingStatus.ACTIVE,
                verified=True,
            ),
            DirectoryListing(
                listing_id="DIR-IOT-001",
                name="SmartEdge IoT",
                category=DirectoryCategory.IOT_PROVIDER,
                services=[ServiceType.SOFTWARE_FIRMWARE, ServiceType.AI_INTEGRATION, ServiceType.CONSULTING],
                description="End-to-end IoT platform: edge devices, cloud integration, and AI analytics.",
                location="Seattle, WA",
                specialisations=["MQTT", "LoRaWAN", "edge computing", "device management"],
                rating=4.4,
                review_count=29,
                status=ListingStatus.ACTIVE,
                verified=True,
            ),
            DirectoryListing(
                listing_id="DIR-SEM-001",
                name="ChipSource Semiconductors",
                category=DirectoryCategory.SEMICONDUCTOR,
                services=[ServiceType.DISTRIBUTION, ServiceType.CONSULTING],
                description="Global semiconductor distributor with technical design support.",
                location="Austin, TX",
                specialisations=["MCU", "FPGA", "power management ICs", "RF chips"],
                min_order_usd=500.0,
                rating=4.3,
                review_count=61,
                status=ListingStatus.ACTIVE,
                verified=False,
            ),
        ]
        for listing in seed:
            self._listings[listing.listing_id] = listing

    def _seed_posts(self) -> None:
        seed_posts = [
            ForumPost(
                post_id="POST-SEED-001",
                author_id="SEED-INV-001",
                title="Best approach for prototyping IoT wearable with AI inference?",
                content=(
                    "I'm building a wearable health monitor that needs on-device ML inference. "
                    "What's the fastest path from concept to working prototype?"
                ),
                category=ForumCategory.PROTOTYPING,
                post_type=PostType.QUESTION,
                tags=["iot", "wearable", "edge-ai", "prototype"],
                upvotes=14,
                views=203,
            ),
            ForumPost(
                post_id="POST-SEED-002",
                author_id="SEED-AI-001",
                title="How we achieved 95% accuracy on a TinyML gesture recognition model",
                content=(
                    "We recently deployed a gesture recognition model on a Cortex-M4 MCU. "
                    "Here's our approach to model compression and quantisation."
                ),
                category=ForumCategory.AI_ROBOTICS,
                post_type=PostType.TEST_OUTCOME,
                tags=["tinyml", "edge-ai", "model-compression"],
                upvotes=31,
                views=487,
                pinned=True,
            ),
            ForumPost(
                post_id="POST-SEED-003",
                author_id="SEED-ROB-001",
                title="Manufacturing tolerance checklist for precision robotics components",
                content=(
                    "After 100+ production runs, here is our go-to tolerance checklist "
                    "for servo mounts and bearing housings."
                ),
                category=ForumCategory.MANUFACTURING,
                post_type=PostType.RESOURCE,
                tags=["manufacturing", "robotics", "quality"],
                upvotes=22,
                views=310,
            ),
        ]
        for post in seed_posts:
            self._posts[post.post_id] = post
