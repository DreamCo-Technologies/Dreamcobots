# BuddyAI – Central AI connector for all Dreamcobots category bots
# Connects OOH Major Occupational Group bots, Mobile App Category bots,
# and Business Category / Industry Classification bots to the Buddy system.

from __future__ import annotations

import sys
from pathlib import Path


_ROOT = Path(__file__).resolve().parents[1]
_GOVERNMENT_CONTRACT_BOT_DIR = _ROOT / "bots" / "government-contract-grant-bot"
if str(_GOVERNMENT_CONTRACT_BOT_DIR) not in sys.path:
    sys.path.insert(0, str(_GOVERNMENT_CONTRACT_BOT_DIR))

# ── Government Contract & Grant Bot ──────────────────────────────────────
from government_contract_grant_bot import GovernmentContractGrantBot

# ── OOH Occupational Group bots ──────────────────────────────────────────
from Occupational_bots.administrative_support_bot import AdministrativeSupportBot
from Occupational_bots.architecture_engineering_bot import ArchitectureEngineeringBot
from Occupational_bots.arts_media_bot import ArtsMediaBot
from Occupational_bots.building_maintenance_bot import BuildingMaintenanceBot
from Occupational_bots.business_financial_bot import BusinessFinancialBot
from Occupational_bots.community_service_bot import CommunityServiceBot
from Occupational_bots.computer_math_bot import ComputerMathBot
from Occupational_bots.construction_extraction_bot import ConstructionExtractionBot
from Occupational_bots.education_library_bot import EducationLibraryBot
from Occupational_bots.farming_fishing_forestry_bot import FarmingFishingForestryBot
from Occupational_bots.food_service_bot import FoodServiceBot
from Occupational_bots.healthcare_practitioner_bot import HealthcarePractitionerBot
from Occupational_bots.healthcare_support_bot import HealthcareSupportBot
from Occupational_bots.installation_maintenance_bot import InstallationMaintenanceBot
from Occupational_bots.legal_bot import LegalBot
from Occupational_bots.management_bot import ManagementBot
from Occupational_bots.military_bot import MilitaryBot
from Occupational_bots.personal_care_bot import PersonalCareBot
from Occupational_bots.production_bot import ProductionBot
from Occupational_bots.protective_service_bot import ProtectiveServiceBot
from Occupational_bots.sales_bot import SalesBot
from Occupational_bots.science_bot import ScienceBot
from Occupational_bots.transportation_bot import TransportationBot

# ── Mobile App Category bots ─────────────────────────────────────────────
from App_bots.books_app_bot import BooksAppBot
from App_bots.business_app_bot import BusinessAppBot
from App_bots.education_app_bot import EducationAppBot
from App_bots.entertainment_app_bot import EntertainmentAppBot
from App_bots.finance_app_bot import FinanceAppBot
from App_bots.food_drink_app_bot import FoodDrinkAppBot
from App_bots.games_app_bot import GamesAppBot
from App_bots.health_fitness_app_bot import HealthFitnessAppBot
from App_bots.kids_family_app_bot import KidsFamilyAppBot
from App_bots.lifestyle_app_bot import LifestyleAppBot
from App_bots.medical_app_bot import MedicalAppBot
from App_bots.music_app_bot import MusicAppBot
from App_bots.navigation_app_bot import NavigationAppBot
from App_bots.news_app_bot import NewsAppBot
from App_bots.photo_video_app_bot import PhotoVideoAppBot
from App_bots.productivity_app_bot import ProductivityAppBot
from App_bots.reference_app_bot import ReferenceAppBot
from App_bots.shopping_app_bot import ShoppingAppBot
from App_bots.social_networking_app_bot import SocialNetworkingAppBot
from App_bots.sports_app_bot import SportsAppBot
from App_bots.travel_app_bot import TravelAppBot
from App_bots.utilities_app_bot import UtilitiesAppBot
from App_bots.weather_app_bot import WeatherAppBot

# ── Business Category / Industry Classification bots ─────────────────────
from Business_bots.accommodation_food_bot import AccommodationFoodBot
from Business_bots.administrative_support_industry_bot import AdministrativeSupportIndustryBot
from Business_bots.agriculture_bot import AgricultureBot
from Business_bots.arts_entertainment_bot import ArtsEntertainmentBot
from Business_bots.construction_bot import ConstructionBot
from Business_bots.educational_services_bot import EducationalServicesBot
from Business_bots.finance_insurance_bot import FinanceInsuranceBot
from Business_bots.health_care_bot import HealthCareBot
from Business_bots.information_bot import InformationBot
from Business_bots.management_companies_bot import ManagementCompaniesBot
from Business_bots.manufacturing_bot import ManufacturingBot
from Business_bots.mining_bot import MiningBot
from Business_bots.other_services_bot import OtherServicesBot
from Business_bots.professional_services_bot import ProfessionalServicesBot
from Business_bots.public_administration_bot import PublicAdministrationBot
from Business_bots.real_estate_leasing_bot import RealEstateLeasingBot
from Business_bots.retail_trade_bot import RetailTradeBot
from Business_bots.transportation_warehousing_bot import TransportationWarehousingBot
from Business_bots.utilities_bot import UtilitiesBot
from Business_bots.wholesale_trade_bot import WholesaleTradeBot


class Buddy:
    """Central AI that manages and routes messages to all category bots.

    Usage::

        buddy = Buddy()
        buddy.start_all()
        buddy.route('ManagementBot', 'run')
    """

    def __init__(self):
        self.bots = {}
        self._register_all()

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def _register_all(self):
        """Instantiate and register every bot, connecting each back to Buddy."""
        all_bot_instances = [
            GovernmentContractGrantBot(),
        AdministrativeSupportBot(),
        ArchitectureEngineeringBot(),
        ArtsMediaBot(),
        BuildingMaintenanceBot(),
        BusinessFinancialBot(),
        CommunityServiceBot(),
        ComputerMathBot(),
        ConstructionExtractionBot(),
        EducationLibraryBot(),
        FarmingFishingForestryBot(),
        FoodServiceBot(),
        HealthcarePractitionerBot(),
        HealthcareSupportBot(),
        InstallationMaintenanceBot(),
        LegalBot(),
        ManagementBot(),
        MilitaryBot(),
        PersonalCareBot(),
        ProductionBot(),
        ProtectiveServiceBot(),
        SalesBot(),
        ScienceBot(),
        TransportationBot(),
        BooksAppBot(),
        BusinessAppBot(),
        EducationAppBot(),
        EntertainmentAppBot(),
        FinanceAppBot(),
        FoodDrinkAppBot(),
        GamesAppBot(),
        HealthFitnessAppBot(),
        KidsFamilyAppBot(),
        LifestyleAppBot(),
        MedicalAppBot(),
        MusicAppBot(),
        NavigationAppBot(),
        NewsAppBot(),
        PhotoVideoAppBot(),
        ProductivityAppBot(),
        ReferenceAppBot(),
        ShoppingAppBot(),
        SocialNetworkingAppBot(),
        SportsAppBot(),
        TravelAppBot(),
        UtilitiesAppBot(),
        WeatherAppBot(),
        AccommodationFoodBot(),
        AdministrativeSupportIndustryBot(),
        AgricultureBot(),
        ArtsEntertainmentBot(),
        ConstructionBot(),
        EducationalServicesBot(),
        FinanceInsuranceBot(),
        HealthCareBot(),
        InformationBot(),
        ManagementCompaniesBot(),
        ManufacturingBot(),
        MiningBot(),
        OtherServicesBot(),
        ProfessionalServicesBot(),
        PublicAdministrationBot(),
        RealEstateLeasingBot(),
        RetailTradeBot(),
        TransportationWarehousingBot(),
        UtilitiesBot(),
        WholesaleTradeBot(),
        ]
        for bot in all_bot_instances:
            self.register(bot)

    def register(self, bot):
        """Manually register an additional bot instance."""
        if hasattr(bot, "connect_to_buddy"):
            bot.connect_to_buddy(self)
        elif hasattr(bot, "buddy"):
            bot.buddy = self
        name = getattr(bot, "name", bot.__class__.__name__)
        self.bots[name] = bot

    # ------------------------------------------------------------------
    # Communication
    # ------------------------------------------------------------------

    def receive(self, bot_name: str, message: str):
        """Receive a message from a bot and log it."""
        print(f'[Buddy] Received from {bot_name}: {message}')
        return message

    def route(self, bot_name: str, method: str, *args, **kwargs):
        """Call a named method on a registered bot."""
        bot = self.bots.get(bot_name)
        if bot is None:
            raise KeyError(f'Bot not found: {bot_name}')
        fn = getattr(bot, method, None)
        if fn is None:
            raise AttributeError(f'{bot_name} has no method: {method}')
        return fn(*args, **kwargs)

    def broadcast(self, method: str, *args, **kwargs):
        """Call the same method on every registered bot."""
        return {name: getattr(bot, method)(*args, **kwargs)
                for name, bot in self.bots.items()
                if hasattr(bot, method)}

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start_all(self):
        """Start every registered bot."""
        for bot in self.bots.values():
            bot.start()

    def run_all(self):
        """Run every registered bot."""
        for bot in self.bots.values():
            bot.run()

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def list_bots(self):
        """Return the names of all registered bots."""
        return list(self.bots.keys())

    def capabilities_report(self):
        """Print a capabilities summary for every registered bot."""
        for bot in self.bots.values():
            try:
                summary = bot.capabilities_summary()
            except AttributeError:
                summary = {'bot': bot.name, 'note': 'no capabilities_summary method'}
            print(summary)


if __name__ == '__main__':
    buddy = Buddy()
    print(f'Buddy managing {len(buddy.list_bots())} bots:')
    buddy.capabilities_report()
