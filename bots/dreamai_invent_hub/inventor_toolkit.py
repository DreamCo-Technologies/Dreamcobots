# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""
Inventor Toolkit for the DreamAIInvent Hub.

Provides four AI-powered tools for inventors:
  1. DesignBot           — AI-assisted product design and concept refinement
  2. FinancialProjectionBot — Hardware cost, revenue, and break-even projections
  3. ManufacturingSimulator — Simulate production scenarios before committing capital
  4. PatentSupportAI        — Prior-art search, claims drafting, and filing guidance
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import math


# ===========================================================================
# 1. Design Bot
# ===========================================================================

class DesignDomain(Enum):
    ROBOTICS = "robotics"
    CONSUMER_ELECTRONICS = "consumer_electronics"
    IOT = "iot"
    WEARABLES = "wearables"
    INDUSTRIAL = "industrial"
    MEDICAL_DEVICES = "medical_devices"
    AUTOMOTIVE = "automotive"
    AEROSPACE = "aerospace"


class DesignStage(Enum):
    CONCEPT = "concept"
    PROTOTYPE = "prototype"
    MVP = "mvp"
    PRODUCTION_READY = "production_ready"


@dataclass
class DesignSession:
    session_id: str
    product_name: str
    domain: DesignDomain
    stage: DesignStage
    requirements: list
    suggestions: list = field(default_factory=list)
    components: list = field(default_factory=list)
    iterations: int = 0

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "product_name": self.product_name,
            "domain": self.domain.value,
            "stage": self.stage.value,
            "requirements": self.requirements,
            "suggestions": self.suggestions,
            "components": self.components,
            "iterations": self.iterations,
        }


class DesignBot:
    """AI-assisted product design and concept refinement tool."""

    COMPONENT_LIBRARY: dict = {
        DesignDomain.ROBOTICS: [
            "servo motors", "encoders", "motor drivers", "microcontroller (ARM Cortex)",
            "LiDAR sensor", "ultrasonic sensors", "battery management IC", "chassis frame",
        ],
        DesignDomain.CONSUMER_ELECTRONICS: [
            "SoC (ARM)", "NAND flash", "PMIC", "USB-C controller",
            "display driver IC", "bluetooth module", "wifi module", "haptic motor",
        ],
        DesignDomain.IOT: [
            "ESP32 MCU", "LoRa module", "MQTT gateway", "temperature sensor",
            "humidity sensor", "accelerometer", "LiPo battery", "antenna",
        ],
        DesignDomain.WEARABLES: [
            "low-power MCU", "PPG sensor", "accelerometer/gyroscope IMU",
            "BLE 5.0 module", "flexible PCB", "OLED display", "wireless charging IC",
        ],
        DesignDomain.INDUSTRIAL: [
            "PLC controller", "Modbus RTU module", "heavy-duty servo",
            "industrial Ethernet switch", "HMI panel", "RFID reader", "vibration sensor",
        ],
        DesignDomain.MEDICAL_DEVICES: [
            "medical-grade MCU", "ECG analog front-end", "SpO2 sensor",
            "secure BLE module", "rechargeable battery", "biocompatible enclosure",
        ],
        DesignDomain.AUTOMOTIVE: [
            "automotive MCU (ISO 26262)", "CAN bus transceiver", "radar sensor",
            "camera module", "LiDAR unit", "12V power regulator", "OBD-II interface",
        ],
        DesignDomain.AEROSPACE: [
            "radiation-hardened MCU", "GPS/IMU module", "RF transceiver",
            "high-reliability connector", "thermal management module", "FPGA",
        ],
    }

    DESIGN_SUGGESTIONS: dict = {
        DesignStage.CONCEPT: [
            "Define your core value proposition and target user persona.",
            "Create a simple block diagram showing major system components.",
            "Identify the top 3 technical risks and mitigation strategies.",
            "Research existing patents in your space to ensure differentiation.",
        ],
        DesignStage.PROTOTYPE: [
            "Use off-the-shelf dev boards (Arduino, Raspberry Pi) to validate concepts quickly.",
            "Build a breadboard prototype before committing to custom PCB.",
            "Document all design decisions and component choices.",
            "Conduct user testing with 5–10 target users at this stage.",
        ],
        DesignStage.MVP: [
            "Optimise power consumption for battery-powered devices.",
            "Design for manufacturability (DFM) — minimise unique components.",
            "Plan your enclosure and IP rating requirements.",
            "Implement OTA firmware update capability from the start.",
        ],
        DesignStage.PRODUCTION_READY: [
            "Complete EMC/FCC/CE certification testing.",
            "Establish a supply chain with at least two sources per critical component.",
            "Create detailed assembly and test procedures.",
            "Perform a design failure mode and effects analysis (DFMEA).",
        ],
    }

    def __init__(self) -> None:
        self._sessions: dict[str, DesignSession] = {}
        self._counter: int = 0

    def start_session(
        self,
        product_name: str,
        domain: DesignDomain,
        stage: DesignStage,
        requirements: Optional[list] = None,
    ) -> DesignSession:
        self._counter += 1
        session_id = f"DESIGN-{self._counter:04d}"
        session = DesignSession(
            session_id=session_id,
            product_name=product_name,
            domain=domain,
            stage=stage,
            requirements=requirements or [],
            suggestions=self.DESIGN_SUGGESTIONS.get(stage, []),
            components=self.COMPONENT_LIBRARY.get(domain, []),
        )
        self._sessions[session_id] = session
        return session

    def iterate(self, session_id: str, new_requirements: list) -> Optional[DesignSession]:
        """Add requirements and refresh suggestions for a session."""
        session = self._sessions.get(session_id)
        if not session:
            return None
        session.requirements.extend(new_requirements)
        session.iterations += 1
        return session

    def get_session(self, session_id: str) -> Optional[DesignSession]:
        return self._sessions.get(session_id)

    def recommend_components(self, domain: DesignDomain) -> list:
        return self.COMPONENT_LIBRARY.get(domain, [])


# ===========================================================================
# 2. Financial Projection Bot
# ===========================================================================

@dataclass
class HardwareCostBreakdown:
    bom_cost_usd: float
    tooling_cost_usd: float
    certification_cost_usd: float
    overhead_pct: float
    units: int

    @property
    def unit_cost_usd(self) -> float:
        overhead = self.bom_cost_usd * (self.overhead_pct / 100)
        return round(self.bom_cost_usd + overhead, 2)

    @property
    def total_cogs_usd(self) -> float:
        return round(self.unit_cost_usd * self.units, 2)

    @property
    def total_investment_usd(self) -> float:
        return round(self.tooling_cost_usd + self.certification_cost_usd + self.total_cogs_usd, 2)

    def to_dict(self) -> dict:
        return {
            "bom_cost_usd": self.bom_cost_usd,
            "unit_cost_usd": self.unit_cost_usd,
            "tooling_cost_usd": self.tooling_cost_usd,
            "certification_cost_usd": self.certification_cost_usd,
            "overhead_pct": self.overhead_pct,
            "units": self.units,
            "total_cogs_usd": self.total_cogs_usd,
            "total_investment_usd": self.total_investment_usd,
        }


class FinancialProjectionBot:
    """Financial projection and break-even analysis for hardware products."""

    def project_revenue(
        self,
        unit_price_usd: float,
        units_year1: int,
        growth_rate_pct: float = 50.0,
        years: int = 5,
    ) -> list:
        """Project revenue over multiple years with compound growth."""
        projections = []
        units = units_year1
        for year in range(1, years + 1):
            revenue = round(unit_price_usd * units, 2)
            projections.append({"year": year, "units": units, "revenue_usd": revenue})
            units = int(units * (1 + growth_rate_pct / 100))
        return projections

    def break_even_analysis(
        self,
        fixed_costs_usd: float,
        unit_price_usd: float,
        unit_cost_usd: float,
    ) -> dict:
        """Calculate break-even point in units and revenue."""
        contribution_margin = unit_price_usd - unit_cost_usd
        if contribution_margin <= 0:
            return {
                "error": "Unit price must exceed unit cost.",
                "break_even_units": None,
                "break_even_revenue_usd": None,
            }
        be_units = math.ceil(fixed_costs_usd / contribution_margin)
        be_revenue = round(be_units * unit_price_usd, 2)
        return {
            "fixed_costs_usd": fixed_costs_usd,
            "unit_price_usd": unit_price_usd,
            "unit_cost_usd": unit_cost_usd,
            "contribution_margin_usd": round(contribution_margin, 2),
            "break_even_units": be_units,
            "break_even_revenue_usd": be_revenue,
        }

    def roi_analysis(
        self,
        total_investment_usd: float,
        annual_profit_usd: float,
    ) -> dict:
        """Calculate return on investment metrics."""
        if total_investment_usd <= 0:
            return {"error": "Total investment must be greater than zero."}
        roi_pct = (annual_profit_usd / total_investment_usd) * 100
        payback_months = (
            round((total_investment_usd / annual_profit_usd) * 12, 1)
            if annual_profit_usd > 0
            else None
        )
        return {
            "total_investment_usd": total_investment_usd,
            "annual_profit_usd": annual_profit_usd,
            "roi_pct": round(roi_pct, 2),
            "payback_months": payback_months,
        }

    def hardware_cost_estimate(
        self,
        bom_cost_usd: float,
        tooling_cost_usd: float,
        certification_cost_usd: float,
        overhead_pct: float,
        units: int,
    ) -> HardwareCostBreakdown:
        return HardwareCostBreakdown(
            bom_cost_usd=bom_cost_usd,
            tooling_cost_usd=tooling_cost_usd,
            certification_cost_usd=certification_cost_usd,
            overhead_pct=overhead_pct,
            units=units,
        )


# ===========================================================================
# 3. Manufacturing Simulator
# ===========================================================================

class ManufacturingMethod(Enum):
    PCB_ASSEMBLY = "pcb_assembly"
    INJECTION_MOLDING = "injection_molding"
    CNC_MACHINING = "cnc_machining"
    ADDITIVE_3D_PRINT = "additive_3d_print"
    DIE_CASTING = "die_casting"
    SHEET_METAL = "sheet_metal"


@dataclass
class SimulationResult:
    method: ManufacturingMethod
    units: int
    unit_time_minutes: float
    setup_time_hours: float
    estimated_yield_pct: float
    cost_per_unit_usd: float
    total_cost_usd: float
    lead_time_days: int
    notes: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "method": self.method.value,
            "units": self.units,
            "unit_time_minutes": self.unit_time_minutes,
            "setup_time_hours": self.setup_time_hours,
            "estimated_yield_pct": self.estimated_yield_pct,
            "cost_per_unit_usd": self.cost_per_unit_usd,
            "total_cost_usd": self.total_cost_usd,
            "lead_time_days": self.lead_time_days,
            "notes": self.notes,
        }


class ManufacturingSimulator:
    """Simulate production scenarios before committing capital."""

    # Base parameters per manufacturing method
    METHOD_PARAMS: dict = {
        ManufacturingMethod.PCB_ASSEMBLY: {
            "unit_time_min": 2.5,
            "setup_hours": 4.0,
            "yield_pct": 97.0,
            "base_cost_usd": 3.50,
            "lead_days": 14,
        },
        ManufacturingMethod.INJECTION_MOLDING: {
            "unit_time_min": 0.5,
            "setup_hours": 40.0,
            "yield_pct": 99.0,
            "base_cost_usd": 1.20,
            "lead_days": 45,
        },
        ManufacturingMethod.CNC_MACHINING: {
            "unit_time_min": 15.0,
            "setup_hours": 2.0,
            "yield_pct": 98.5,
            "base_cost_usd": 12.00,
            "lead_days": 10,
        },
        ManufacturingMethod.ADDITIVE_3D_PRINT: {
            "unit_time_min": 60.0,
            "setup_hours": 0.5,
            "yield_pct": 95.0,
            "base_cost_usd": 8.00,
            "lead_days": 3,
        },
        ManufacturingMethod.DIE_CASTING: {
            "unit_time_min": 1.0,
            "setup_hours": 80.0,
            "yield_pct": 98.0,
            "base_cost_usd": 0.80,
            "lead_days": 60,
        },
        ManufacturingMethod.SHEET_METAL: {
            "unit_time_min": 5.0,
            "setup_hours": 8.0,
            "yield_pct": 99.5,
            "base_cost_usd": 4.50,
            "lead_days": 7,
        },
    }

    def simulate(
        self,
        method: ManufacturingMethod,
        units: int,
        material_cost_per_unit_usd: float = 0.0,
        labor_rate_per_hour_usd: float = 25.0,
    ) -> SimulationResult:
        """Run a production simulation for the given method and volume."""
        params = self.METHOD_PARAMS[method]
        unit_time = params["unit_time_min"]
        setup_hours = params["setup_hours"]
        yield_pct = params["yield_pct"]
        base_cost = params["base_cost_usd"]
        lead_days = params["lead_days"]

        # Adjust for volume (economy of scale)
        volume_factor = max(0.5, 1.0 - (units / 100_000) * 0.3)
        labor_cost_per_unit = (unit_time / 60) * labor_rate_per_hour_usd * volume_factor
        cost_per_unit = round(
            (base_cost + material_cost_per_unit_usd + labor_cost_per_unit) * volume_factor, 4
        )
        # Account for yield loss
        effective_cost = round(cost_per_unit / (yield_pct / 100), 4)
        total_cost = round(effective_cost * units, 2)

        notes = []
        if units < 100:
            notes.append("Low volume — consider 3D printing for prototyping phase.")
        if units > 10_000:
            notes.append("High volume — negotiate tooling amortisation with manufacturer.")
        if yield_pct < 97:
            notes.append("Yield below 97% — invest in automated optical inspection (AOI).")

        return SimulationResult(
            method=method,
            units=units,
            unit_time_minutes=unit_time,
            setup_time_hours=setup_hours,
            estimated_yield_pct=yield_pct,
            cost_per_unit_usd=effective_cost,
            total_cost_usd=total_cost,
            lead_time_days=lead_days,
            notes=notes,
        )

    def compare_methods(
        self,
        units: int,
        material_cost_per_unit_usd: float = 0.0,
    ) -> list:
        """Compare all manufacturing methods for a given volume."""
        results = []
        for method in ManufacturingMethod:
            result = self.simulate(method, units, material_cost_per_unit_usd)
            results.append(result.to_dict())
        results.sort(key=lambda x: x["total_cost_usd"])
        return results


# ===========================================================================
# 4. Patent Support AI
# ===========================================================================

class PatentType(Enum):
    UTILITY = "utility"
    DESIGN = "design"
    PLANT = "plant"
    PROVISIONAL = "provisional"


class PatentStatus(Enum):
    IDEA = "idea"
    PRIOR_ART_SEARCH = "prior_art_search"
    CLAIMS_DRAFTED = "claims_drafted"
    PROVISIONAL_FILED = "provisional_filed"
    FULL_APPLICATION = "full_application"
    GRANTED = "granted"


@dataclass
class PatentDossier:
    dossier_id: str
    invention_title: str
    patent_type: PatentType
    status: PatentStatus
    description: str
    claims: list = field(default_factory=list)
    prior_art_references: list = field(default_factory=list)
    filing_guidance: list = field(default_factory=list)
    estimated_cost_usd: float = 0.0

    def to_dict(self) -> dict:
        return {
            "dossier_id": self.dossier_id,
            "invention_title": self.invention_title,
            "patent_type": self.patent_type.value,
            "status": self.status.value,
            "description": self.description,
            "claims": self.claims,
            "prior_art_references": self.prior_art_references,
            "filing_guidance": self.filing_guidance,
            "estimated_cost_usd": self.estimated_cost_usd,
        }


class PatentSupportAI:
    """AI assistant for patent prior-art search, claims drafting, and filing guidance."""

    FILING_COSTS: dict = {
        PatentType.PROVISIONAL: {"uspto_fee_usd": 320, "attorney_est_usd": 1500},
        PatentType.UTILITY: {"uspto_fee_usd": 800, "attorney_est_usd": 8000},
        PatentType.DESIGN: {"uspto_fee_usd": 580, "attorney_est_usd": 2500},
        PatentType.PLANT: {"uspto_fee_usd": 800, "attorney_est_usd": 5000},
    }

    FILING_STEPS: dict = {
        PatentType.PROVISIONAL: [
            "Prepare a detailed written description of your invention.",
            "Include drawings or diagrams where applicable.",
            "File a provisional application with the USPTO (12-month placeholder).",
            "Use the 'Patent Pending' designation immediately after filing.",
            "Within 12 months, file the full non-provisional (utility) application.",
        ],
        PatentType.UTILITY: [
            "Conduct a thorough prior-art search (USPTO, Google Patents, Espacenet).",
            "Draft independent and dependent patent claims.",
            "Prepare detailed drawings and specification.",
            "File with the USPTO via EFS-Web.",
            "Respond to office actions from the patent examiner.",
            "Pay issue fee upon allowance.",
        ],
        PatentType.DESIGN: [
            "Prepare formal drawings showing the ornamental design from multiple views.",
            "File a design patent application with the USPTO.",
            "Examiner reviews drawings for formal requirements.",
            "Pay issue fee upon allowance.",
        ],
        PatentType.PLANT: [
            "Prepare botanical description of the new plant variety.",
            "Include color photographs from multiple growth stages.",
            "File a plant patent application with the USPTO.",
        ],
    }

    def __init__(self) -> None:
        self._dossiers: dict[str, PatentDossier] = {}
        self._counter: int = 0

    def create_dossier(
        self,
        invention_title: str,
        description: str,
        patent_type: PatentType = PatentType.PROVISIONAL,
    ) -> PatentDossier:
        """Create a new patent dossier for an invention."""
        self._counter += 1
        dossier_id = f"PAT-{self._counter:04d}"
        costs = self.FILING_COSTS[patent_type]
        estimated_cost = costs["uspto_fee_usd"] + costs["attorney_est_usd"]
        dossier = PatentDossier(
            dossier_id=dossier_id,
            invention_title=invention_title,
            patent_type=patent_type,
            status=PatentStatus.IDEA,
            description=description,
            filing_guidance=self.FILING_STEPS[patent_type],
            estimated_cost_usd=estimated_cost,
        )
        self._dossiers[dossier_id] = dossier
        return dossier

    def search_prior_art(self, dossier_id: str, keywords: list) -> list:
        """Simulate a prior-art search returning relevant reference suggestions."""
        dossier = self._dossiers.get(dossier_id)
        if not dossier:
            return []
        # Simulated prior-art references based on keywords
        references = [
            f"US{10_000_000 + i}: Method and apparatus for {kw}" for i, kw in enumerate(keywords)
        ]
        dossier.prior_art_references = references
        dossier.status = PatentStatus.PRIOR_ART_SEARCH
        return references

    def draft_claims(self, dossier_id: str, invention_elements: list) -> list:
        """Generate claim skeletons from invention elements."""
        dossier = self._dossiers.get(dossier_id)
        if not dossier:
            return []
        claims = [f"Claim 1: A system comprising {invention_elements[0]}."] if invention_elements else []
        for i, element in enumerate(invention_elements[1:], start=2):
            claims.append(f"Claim {i}: The system of claim 1, further comprising {element}.")
        dossier.claims = claims
        dossier.status = PatentStatus.CLAIMS_DRAFTED
        return claims

    def get_dossier(self, dossier_id: str) -> Optional[PatentDossier]:
        return self._dossiers.get(dossier_id)

    def get_filing_guidance(self, patent_type: PatentType) -> list:
        return self.FILING_STEPS.get(patent_type, [])

    def estimate_cost(self, patent_type: PatentType) -> dict:
        return self.FILING_COSTS.get(patent_type, {})


# ===========================================================================
# Inventor Toolkit — aggregator
# ===========================================================================

class InventorToolkit:
    """
    Aggregates all four inventor tools into a single convenience interface.
    """

    def __init__(self) -> None:
        self.design_bot = DesignBot()
        self.financial_projection = FinancialProjectionBot()
        self.manufacturing_simulator = ManufacturingSimulator()
        self.patent_support = PatentSupportAI()

    def summary(self) -> dict:
        return {
            "tools": [
                "DesignBot",
                "FinancialProjectionBot",
                "ManufacturingSimulator",
                "PatentSupportAI",
            ],
            "description": (
                "AI-powered toolkit for inventors: product design assistance, "
                "hardware financial projections, manufacturing simulation, "
                "and patent filing support."
            ),
        }
