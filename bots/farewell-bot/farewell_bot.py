"""Farewell Bot - Compassionate funeral planning, memorial services, and grief support."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from core.base_bot import BaseBot

COMPASSIONATE_NOTE = (
    "We extend our deepest condolences during this difficult time. "
    "This assistant is here to help with practical planning while honoring the memory of your loved one."
)


class FarewellBot(BaseBot):
    """AI bot for compassionate funeral planning, memorial services, and grief support."""

    def __init__(self):
        """Initialize the FarewellBot with compassionate, respectful tone."""
        super().__init__(
            name="farewell-bot",
            description="Provides compassionate assistance with funeral planning, memorial services, obituaries, and grief support.",
            version="2.0.0",
        )
        self.priority = "medium"

    def run(self):
        """Run the farewell bot main workflow."""
        self.start()
        return self.grief_support_resources()

    def plan_service(self, deceased_info: dict, family_preferences: dict) -> dict:
        """Create a comprehensive funeral or memorial service plan."""
        name = deceased_info.get("name", "Your Loved One")
        service_type = family_preferences.get("service_type", "traditional")
        self.log(f"Planning service for: {name}")
        return {
            "note": COMPASSIONATE_NOTE,
            "service_plan": {
                "deceased": name,
                "service_type": service_type.title(),
                "suggested_timeline": {
                    "day_1": [
                        "Obtain death certificate (funeral home assists)",
                        "Notify immediate family and close friends",
                        "Contact funeral home to arrange transport",
                        "Discuss burial vs cremation with family",
                    ],
                    "day_2_3": [
                        "Select casket/urn with funeral home",
                        "Draft obituary",
                        "Schedule service date and venue",
                        "Notify employer, bank, social security",
                        "Contact life insurance companies",
                    ],
                    "day_4_7": [
                        "Coordinate service logistics",
                        "Select music and readings",
                        "Arrange catering for reception if desired",
                        "Create memory slideshow",
                        "Notify distant family and friends",
                    ],
                },
                "service_elements": [
                    "Opening prayer or moment of reflection",
                    "Musical selections (2-3 songs)",
                    "Eulogies (2-3 speakers, 3-5 min each)",
                    "Reading of obituary",
                    "Photo/video tribute",
                    "Committal service",
                    "Reception",
                ],
            },
            "estimated_attendees": family_preferences.get("expected_guests", 50),
            "ftc_rights": self.ftc_compliance_guide(),
        }

    def write_obituary(self, name: str, birth_date: str, death_date: str, life_highlights: list) -> dict:
        """Write a compassionate, personalized obituary."""
        highlights_text = ". ".join(life_highlights) if life_highlights else "a life well-lived and deeply cherished."
        obituary = f"""
{name}, beloved [relationship], passed away on {death_date}. Born on {birth_date}, {name} was known for [character traits] and touched the lives of everyone who knew them.

{highlights_text}

{name} is survived by [list of survivors]. They were preceded in death by [predecessors if applicable].

A [service type] service will be held on [date] at [location]. In lieu of flowers, the family requests donations to [charity].

"{name} may be gone from our sight, but will never leave our hearts."
"""
        return {
            "note": COMPASSIONATE_NOTE,
            "name": name,
            "birth_date": birth_date,
            "death_date": death_date,
            "obituary_draft": obituary.strip(),
            "word_count": len(obituary.split()),
            "publication_options": [
                "Local newspaper (print + online): $150-$400",
                "Legacy.com (national memorial site): $50-$200",
                "Funeral home website: Usually free",
                "Family social media: Free",
            ],
            "tips": [
                "Keep to 150-300 words for newspaper publication",
                "Include a recent, warm photo",
                "Proofread with at least two family members",
            ],
        }

    def memorial_video_concept(self, photos_available: int, music_preference: str) -> dict:
        """Create a memorial video concept for a tribute slideshow."""
        return {
            "note": COMPASSIONATE_NOTE,
            "video_concept": {
                "recommended_length": "5-8 minutes",
                "photos_needed": min(photos_available, 40),
                "seconds_per_photo": 4,
                "music_preference": music_preference,
                "suggested_structure": [
                    {"segment": "Intro", "duration": "30 sec", "content": "Name, dates, meaningful quote"},
                    {"segment": "Early Life", "duration": "1.5 min", "content": "Childhood and family photos"},
                    {"segment": "Milestones", "duration": "2 min", "content": "Major life events, career, milestones"},
                    {"segment": "Family & Friends", "duration": "2 min", "content": "Relationships and gatherings"},
                    {"segment": "Final Years", "duration": "1 min", "content": "Recent photos and memories"},
                    {"segment": "Tribute", "duration": "30 sec", "content": "Final photo with dates and tribute text"},
                ],
                "diy_tools": ["iMovie (Mac/iOS)", "Windows Video Editor", "Animoto", "Tribute.co"],
                "professional_services": "$200-$800 from local videographers",
            },
            "suggested_songs": {
                "classical": ["Ave Maria", "Amazing Grace", "Somewhere Over the Rainbow"],
                "contemporary": ["Hallelujah (Cohen)", "My Way (Sinatra)", "You Are So Beautiful"],
                "gospel": ["How Great Thou Art", "I Can Only Imagine", "Blessed Assurance"],
            },
        }

    def grief_support_resources(self) -> dict:
        """Return comprehensive grief support resources."""
        return {
            "note": COMPASSIONATE_NOTE,
            "immediate_support": [
                {"resource": "National Grief Share Helpline", "phone": "1-800-395-5755", "available": "24/7"},
                {"resource": "Crisis Text Line", "contact": "Text HOME to 741741", "available": "24/7"},
                {"resource": "Compassionate Friends (child loss)", "phone": "1-877-969-0010", "available": "M-F 9am-5pm ET"},
            ],
            "online_communities": [
                "GriefShare.org - local and online groups",
                "Reddit r/GriefSupport - peer support community",
                "Open to Hope Foundation (opentohope.com)",
            ],
            "books_and_resources": [
                "On Grief and Grieving by Elisabeth Kübler-Ross",
                "A Grief Observed by C.S. Lewis",
                "Option B by Sheryl Sandberg",
                "It's OK That You're Not OK by Megan Devine",
            ],
            "stages_of_grief": [
                "Denial - Shock and disbelief are normal",
                "Anger - A natural response to loss",
                "Bargaining - 'What if' thoughts are common",
                "Depression - Deep sadness is part of healing",
                "Acceptance - Finding a new normal",
            ],
            "reminder": "Grief is not linear. Be patient and compassionate with yourself.",
        }

    def compare_costs(self, service_options: list) -> dict:
        """Compare funeral and memorial service options by cost."""
        analyzed = []
        for option in service_options:
            service_type = option.get("type", "traditional")
            cost_ranges = {
                "traditional_burial": (7000, 12000),
                "cremation": (1500, 4000),
                "green_burial": (1000, 4000),
                "direct_cremation": (700, 2000),
                "celebration_of_life": (500, 5000),
            }
            key = service_type.lower().replace(" ", "_")
            low, high = cost_ranges.get(key, (3000, 8000))
            analyzed.append({
                "service_type": service_type,
                "estimated_cost_low": f"${low:,}",
                "estimated_cost_high": f"${high:,}",
                "average": f"${(low + high) // 2:,}",
                "includes": option.get("includes", ["Basic services", "Transportation", "Documentation"]),
            })
        analyzed.sort(key=lambda x: int(x["estimated_cost_low"].replace("$", "").replace(",", "")))
        return {
            "note": COMPASSIONATE_NOTE,
            "options_compared": analyzed,
            "financial_assistance": [
                "Veterans benefits (VA burial allowance: up to $2,000)",
                "Social Security lump-sum death benefit ($255 to surviving spouse)",
                "State burial assistance programs (varies by state)",
                "Life insurance proceeds",
                "Crowdfunding (GoFundMe)",
            ],
            "ftc_reminder": "Funeral homes must provide itemized price lists. You have the right to choose only services you want.",
        }

    def find_venues(self, location: str, capacity: int) -> list:
        """Find suitable memorial service venues for a given location and capacity."""
        return [
            {
                "venue": f"{location} Community Church",
                "type": "Religious",
                "capacity": max(capacity, 100),
                "cost": "Often free or suggested donation",
                "features": ["Parking", "Accessibility", "Audio/Visual"],
                "contact": "Contact local churches directly",
            },
            {
                "venue": f"{location} Funeral Home Chapel",
                "type": "Funeral Home",
                "capacity": max(capacity, 75),
                "cost": "Included in funeral package",
                "features": ["Parking", "Casket display", "Streaming"],
                "contact": "Through funeral home arrangement",
            },
            {
                "venue": f"{location} Memorial Park Pavilion",
                "type": "Outdoor",
                "capacity": capacity + 50,
                "cost": "$200-$600",
                "features": ["Natural setting", "Photo opportunities", "Catering allowed"],
                "contact": "Parks & Recreation department",
            },
            {
                "venue": "Virtual / Online Memorial",
                "type": "Virtual",
                "capacity": "Unlimited",
                "cost": "$0-$100",
                "features": ["Global attendance", "Recorded", "Accessible to all"],
                "contact": "Zoom, Gather.town, or GatheringUs.com",
            },
        ]

    def ftc_compliance_guide(self) -> dict:
        """Return FTC Funeral Rule compliance information for consumer rights."""
        return {
            "rule": "FTC Funeral Rule (16 CFR Part 453)",
            "consumer_rights": [
                "Request itemized price list - funeral homes MUST provide",
                "Choose only services you want - no 'package-only' requirement",
                "Use casket purchased elsewhere - funeral home cannot refuse",
                "Get written price quote before making decisions",
                "Ask for alternative containers if choosing cremation",
            ],
            "what_funeral_homes_must_provide": [
                "General Price List (GPL) upon request",
                "Casket Price List before showing caskets",
                "Outer Burial Container Price List",
                "Itemized Statement of Goods and Services Selected",
            ],
            "red_flags": [
                "Refusing to provide itemized pricing",
                "Claiming embalming is required when it is not (in most states)",
                "Refusing caskets purchased from third parties",
                "High-pressure sales tactics",
            ],
            "file_complaint": "FTC: ReportFraud.ftc.gov | State funeral regulatory board",
        }

    def cremation_vs_burial_analysis(self, preferences: dict, budget: float) -> dict:
        """Provide a compassionate analysis of cremation vs burial options."""
        return {
            "note": COMPASSIONATE_NOTE,
            "budget": f"${budget:,.0f}",
            "cremation": {
                "average_cost": "$1,500 - $4,000",
                "within_budget": budget >= 1500,
                "pros": [
                    "Generally lower cost",
                    "Flexible timing for service",
                    "Portable remains (urn)",
                    "Many scattering options (sea, mountains, etc.)",
                    "Lower environmental footprint",
                ],
                "cons": [
                    "Some religious traditions discourage",
                    "Permanent - cannot be reversed",
                ],
                "options": ["Traditional cremation with service", "Direct cremation (minimal)", "Aquamation (water-based, eco-friendly)"],
            },
            "burial": {
                "average_cost": "$7,000 - $12,000",
                "within_budget": budget >= 7000,
                "pros": [
                    "Traditional and familiar",
                    "Physical gravesite for visiting",
                    "Accepted by all major religions",
                    "Permanent memorial location",
                ],
                "cons": [
                    "Higher cost",
                    "Ongoing cemetery fees",
                    "Less flexibility",
                ],
                "options": ["Traditional burial", "Green/natural burial", "Mausoleum/entombment"],
            },
            "recommendation": "Cremation" if budget < 5000 else "Either option is financially feasible",
            "personal_note": "The most important factor is honoring your loved one's wishes and your family's values.",
        }

    def plan_virtual_funeral(self, platform_preference: str, expected_attendees: int) -> dict:
        """Plan a virtual funeral or memorial streaming service."""
        platforms = {
            "zoom": {"cost": "$15-150/month", "max_attendees": 1000, "features": ["Video", "Chat", "Recording", "Breakout rooms"]},
            "youtube": {"cost": "Free", "max_attendees": "Unlimited", "features": ["Live stream", "Replay", "Chat", "Private link"]},
            "gatheringus": {"cost": "$199-399 flat", "max_attendees": 500, "features": ["Dedicated memorial platform", "Photo sharing", "Tribute wall", "Recording"]},
        }
        platform_key = platform_preference.lower()
        platform_info = platforms.get(platform_key, platforms["zoom"])
        return {
            "note": COMPASSIONATE_NOTE,
            "platform": platform_preference,
            "platform_details": platform_info,
            "expected_attendees": expected_attendees,
            "planning_checklist": [
                "Send streaming link 48 hours in advance",
                "Assign a technical host (not the officiant)",
                "Test audio/video 2 hours before service",
                "Mute all attendees by default; unmute for speakers",
                "Designate a moderator for chat",
                "Record for those who cannot attend",
                "Share recording link within 24 hours after service",
            ],
            "technical_requirements": {
                "host_internet": "10+ Mbps upload speed recommended",
                "camera": "HD webcam or phone camera",
                "audio": "External microphone strongly recommended",
                "lighting": "Face light source; avoid backlight",
            },
            "memorial_features": [
                "Virtual condolences wall (open before/after service)",
                "Digital guestbook for attendee signatures",
                "Online memorial page (Everplans, GatheringUs)",
            ],
        }
