"""Car Flipping Bot — tier-aware car deal finder and flip profit estimator."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, get_tier_config, get_upgrade_path
from bots.car_flipping_bot.tiers import BOT_FEATURES, get_bot_tier_info
from framework import GlobalAISourcesFlow  # noqa: F401


class CarFlippingBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class CarFlippingBot:
    """Tier-aware car deal finder and flip profit estimator."""

    RESULT_LIMITS = {Tier.FREE: 5, Tier.PRO: 20, Tier.ENTERPRISE: 50}

    CAR_DATABASE = [
        {"id": "c001", "year": 2018, "make": "Toyota", "model": "Camry", "mileage": 72000, "buy_price": 11500, "market_value": 16800, "condition": "Good", "repair_cost": 800, "color": "Silver", "transmission": "Automatic"},
        {"id": "c002", "year": 2017, "make": "Honda", "model": "Civic", "mileage": 85000, "buy_price": 9200, "market_value": 14500, "condition": "Fair", "repair_cost": 1200, "color": "Blue", "transmission": "Automatic"},
        {"id": "c003", "year": 2019, "make": "Ford", "model": "F-150", "mileage": 61000, "buy_price": 21000, "market_value": 30500, "condition": "Good", "repair_cost": 600, "color": "White", "transmission": "Automatic"},
        {"id": "c004", "year": 2016, "make": "Chevrolet", "model": "Silverado 1500", "mileage": 95000, "buy_price": 15500, "market_value": 22000, "condition": "Fair", "repair_cost": 1800, "color": "Black", "transmission": "Automatic"},
        {"id": "c005", "year": 2020, "make": "Toyota", "model": "RAV4", "mileage": 45000, "buy_price": 19500, "market_value": 27000, "condition": "Very Good", "repair_cost": 400, "color": "Red", "transmission": "Automatic"},
        {"id": "c006", "year": 2018, "make": "Honda", "model": "CR-V", "mileage": 68000, "buy_price": 15000, "market_value": 22500, "condition": "Good", "repair_cost": 700, "color": "Gray", "transmission": "Automatic"},
        {"id": "c007", "year": 2015, "make": "BMW", "model": "3 Series", "mileage": 88000, "buy_price": 12000, "market_value": 19000, "condition": "Fair", "repair_cost": 2200, "color": "Black", "transmission": "Automatic"},
        {"id": "c008", "year": 2019, "make": "Ford", "model": "Mustang", "mileage": 38000, "buy_price": 22000, "market_value": 31000, "condition": "Very Good", "repair_cost": 500, "color": "Red", "transmission": "Manual"},
        {"id": "c009", "year": 2017, "make": "Chevrolet", "model": "Malibu", "mileage": 79000, "buy_price": 8500, "market_value": 13500, "condition": "Good", "repair_cost": 900, "color": "Silver", "transmission": "Automatic"},
        {"id": "c010", "year": 2020, "make": "Toyota", "model": "Tacoma", "mileage": 42000, "buy_price": 26000, "market_value": 35000, "condition": "Very Good", "repair_cost": 300, "color": "Gray", "transmission": "Automatic"},
        {"id": "c011", "year": 2016, "make": "Honda", "model": "Accord", "mileage": 92000, "buy_price": 8800, "market_value": 13200, "condition": "Fair", "repair_cost": 1100, "color": "White", "transmission": "Automatic"},
        {"id": "c012", "year": 2018, "make": "Jeep", "model": "Wrangler", "mileage": 55000, "buy_price": 24000, "market_value": 34500, "condition": "Good", "repair_cost": 800, "color": "Green", "transmission": "Manual"},
        {"id": "c013", "year": 2019, "make": "Hyundai", "model": "Elantra", "mileage": 61000, "buy_price": 9500, "market_value": 14000, "condition": "Good", "repair_cost": 500, "color": "Blue", "transmission": "Automatic"},
        {"id": "c014", "year": 2017, "make": "Subaru", "model": "Outback", "mileage": 74000, "buy_price": 14500, "market_value": 21000, "condition": "Good", "repair_cost": 700, "color": "White", "transmission": "Automatic"},
        {"id": "c015", "year": 2015, "make": "Mercedes-Benz", "model": "C300", "mileage": 82000, "buy_price": 14000, "market_value": 21500, "condition": "Fair", "repair_cost": 2500, "color": "Silver", "transmission": "Automatic"},
        {"id": "c016", "year": 2020, "make": "Kia", "model": "Sorento", "mileage": 49000, "buy_price": 17000, "market_value": 24500, "condition": "Very Good", "repair_cost": 350, "color": "Black", "transmission": "Automatic"},
        {"id": "c017", "year": 2018, "make": "Nissan", "model": "Altima", "mileage": 70000, "buy_price": 10000, "market_value": 15500, "condition": "Good", "repair_cost": 600, "color": "Silver", "transmission": "Automatic"},
        {"id": "c018", "year": 2016, "make": "Volkswagen", "model": "Jetta", "mileage": 86000, "buy_price": 7500, "market_value": 11500, "condition": "Good", "repair_cost": 800, "color": "White", "transmission": "Automatic"},
        {"id": "c019", "year": 2019, "make": "Mazda", "model": "CX-5", "mileage": 52000, "buy_price": 18500, "market_value": 26000, "condition": "Very Good", "repair_cost": 400, "color": "Red", "transmission": "Automatic"},
        {"id": "c020", "year": 2017, "make": "GMC", "model": "Sierra 1500", "mileage": 88000, "buy_price": 18000, "market_value": 25500, "condition": "Good", "repair_cost": 1200, "color": "Black", "transmission": "Automatic"},
    ]

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._current_make: str = None

    def search_cars(self, make: str, budget: float) -> list:
        """Return cars under budget for that make."""
        if self.tier == Tier.FREE and self._current_make is not None and make.lower() != self._current_make.lower():
            raise CarFlippingBotTierError(
                f"FREE tier is limited to 1 make at a time. Currently searching '{self._current_make}'. "
                "Upgrade to PRO to search any make."
            )
        self._current_make = make
        limit = self.RESULT_LIMITS[self.tier]
        results = [
            car for car in self.CAR_DATABASE
            if car["make"].lower() == make.lower() and car["buy_price"] <= budget
        ]
        results = results[:limit]
        return [self._annotate_car(car) for car in results]

    def _annotate_car(self, car: dict) -> dict:
        profit = self.estimate_flip_profit(car)
        condition_score = {"Very Good": 90, "Good": 70, "Fair": 50, "Poor": 25}.get(car["condition"], 60)
        return {
            **car,
            "flip_profit_est": round(profit, 2),
            "condition_score": condition_score,
            "profit_margin_pct": round((car["market_value"] - car["buy_price"]) / car["market_value"] * 100, 1),
        }

    def evaluate_car(self, car: dict) -> dict:
        """Return condition score, market value, and flip potential."""
        profit = self.estimate_flip_profit(car)
        condition_score = {"Very Good": 90, "Good": 70, "Fair": 50, "Poor": 25}.get(car.get("condition", "Good"), 60)
        if profit > 5000:
            flip_potential = "Excellent"
        elif profit > 2500:
            flip_potential = "Good"
        elif profit > 1000:
            flip_potential = "Fair"
        else:
            flip_potential = "Low"

        result = {
            "id": car.get("id"),
            "year_make_model": f"{car.get('year')} {car.get('make')} {car.get('model')}",
            "buy_price": car["buy_price"],
            "market_value": car["market_value"],
            "repair_cost": car.get("repair_cost", 0),
            "estimated_flip_profit": round(profit, 2),
            "condition_score": condition_score,
            "flip_potential": flip_potential,
            "tier": self.tier.value,
        }
        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            result["vehicle_history"] = {"accidents": 0, "owners": 2, "clean_title": True}
            result["repair_breakdown"] = {"mechanical": round(car.get("repair_cost", 0) * 0.6, 2), "cosmetic": round(car.get("repair_cost", 0) * 0.4, 2)}
        if self.tier == Tier.ENTERPRISE:
            result["market_prediction_90d"] = round(car["market_value"] * 1.03, 2)
            result["auction_data_available"] = True
        return result

    def estimate_flip_profit(self, car: dict) -> float:
        """Return estimated profit after repair costs and fees."""
        return (car["market_value"] - car["buy_price"] - car.get("repair_cost", 0)) * 0.92

    def get_best_opportunities(self, limit: int = 5) -> list:
        """Return top flip opportunities sorted by profit."""
        allowed_limit = self.RESULT_LIMITS[self.tier]
        sample = self.CAR_DATABASE[:allowed_limit]
        annotated = [self._annotate_car(car) for car in sample]
        return sorted(annotated, key=lambda x: x["flip_profit_est"], reverse=True)[:limit]

    def describe_tier(self) -> str:
        info = get_bot_tier_info(self.tier)
        lines = [
            f"=== {info['name']} Car Flipping Bot Tier ===",
            f"Price: ${info['price_usd_monthly']:.2f}/month",
            f"Support: {info['support_level']}",
            "Features:",
        ]
        for f in info["features"]:
            lines.append(f"  \u2713 {f}")
        output = "\n".join(lines)
        print(output)
        return output


# ---------------------------------------------------------------------------
# Stripe integration for CarFlippingBot
# ---------------------------------------------------------------------------
from bots.stripe_integration.stripe_client import StripeClient as _StripeClientCFB

_CFB_PRICES = {
    Tier.PRO: 4900,         # $49/month
    Tier.ENTERPRISE: 29900, # $299/month
}

_orig_cfb_init = CarFlippingBot.__init__


def _cfb_new_init(self, tier: Tier = Tier.FREE) -> None:
    _orig_cfb_init(self, tier)
    self._stripe = _StripeClientCFB()


def _cfb_create_checkout_session(self, upgrade_tier: Tier, customer_email: str = None) -> dict:
    if upgrade_tier == Tier.FREE:
        raise CarFlippingBotTierError("Cannot create checkout for FREE tier.")
    price_cents = _CFB_PRICES.get(upgrade_tier, 4900)
    result = self._stripe.create_checkout_session(plan=f"CarFlipping {upgrade_tier.value.title()}", amount_cents=price_cents)
    if customer_email:
        result["customer_email"] = customer_email
    result["mode"] = "subscription"
    return result


def _cfb_create_payment_link(self, upgrade_tier: Tier) -> dict:
    if upgrade_tier == Tier.FREE:
        raise CarFlippingBotTierError("Cannot create payment link for FREE tier.")
    price_cents = _CFB_PRICES.get(upgrade_tier, 4900)
    return self._stripe.create_payment_link(plan=f"CarFlipping {upgrade_tier.value.title()}", amount_cents=price_cents)


CarFlippingBot.__init__ = _cfb_new_init
CarFlippingBot.create_checkout_session = _cfb_create_checkout_session
CarFlippingBot.create_payment_link = _cfb_create_payment_link
