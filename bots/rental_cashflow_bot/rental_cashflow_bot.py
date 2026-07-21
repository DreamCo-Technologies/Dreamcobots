"""Rental Cash Flow Bot — tier-aware rental property analysis and portfolio tracker."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, get_tier_config, get_upgrade_path
from bots.rental_cashflow_bot.tiers import BOT_FEATURES, get_bot_tier_info
from framework import GlobalAISourcesFlow  # noqa: F401


class RentalCashflowBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class RentalCashflowBot:
    """Tier-aware rental property cash flow analyzer and portfolio tracker."""

    PORTFOLIO_LIMITS = {Tier.FREE: 1, Tier.PRO: 10, Tier.ENTERPRISE: None}

    # ~20 sample rental properties
    RENTAL_DATABASE = {
        "RNT001": {
            "address": "1204 Oak Blvd, Austin TX",
            "purchase_price": 320000,
            "down_payment_pct": 0.20,
            "mortgage_rate_pct": 6.75,
            "mortgage_term_years": 30,
            "beds": 3, "baths": 2, "sqft": 1450,
            "type": "single_family",
            "monthly_rent": 2400,
            "year_built": 1998,
            "market": "austin",
            "property_tax_annual": 6400,
            "insurance_annual": 1800,
            "hoa_monthly": 0,
        },
        "RNT002": {
            "address": "3901 E Indian School Rd, Phoenix AZ",
            "purchase_price": 285000,
            "down_payment_pct": 0.20,
            "mortgage_rate_pct": 6.75,
            "mortgage_term_years": 30,
            "beds": 3, "baths": 2, "sqft": 1550,
            "type": "single_family",
            "monthly_rent": 2100,
            "year_built": 1995,
            "market": "phoenix",
            "property_tax_annual": 4560,
            "insurance_annual": 1400,
            "hoa_monthly": 0,
        },
        "RNT003": {
            "address": "2204 Belmont Blvd, Nashville TN",
            "purchase_price": 415000,
            "down_payment_pct": 0.25,
            "mortgage_rate_pct": 6.75,
            "mortgage_term_years": 30,
            "beds": 3, "baths": 2, "sqft": 1700,
            "type": "single_family",
            "monthly_rent": 2900,
            "year_built": 1997,
            "market": "nashville",
            "property_tax_annual": 2490,
            "insurance_annual": 1600,
            "hoa_monthly": 0,
        },
        "RNT004": {
            "address": "1502 Larimer St #4C, Denver CO",
            "purchase_price": 265000,
            "down_payment_pct": 0.20,
            "mortgage_rate_pct": 6.75,
            "mortgage_term_years": 30,
            "beds": 1, "baths": 1, "sqft": 750,
            "type": "condo",
            "monthly_rent": 2000,
            "year_built": 2007,
            "market": "denver",
            "property_tax_annual": 2120,
            "insurance_annual": 900,
            "hoa_monthly": 350,
        },
        "RNT005": {
            "address": "4810 W Kennedy Blvd, Tampa FL",
            "purchase_price": 310000,
            "down_payment_pct": 0.20,
            "mortgage_rate_pct": 6.75,
            "mortgage_term_years": 30,
            "beds": 3, "baths": 2, "sqft": 1550,
            "type": "single_family",
            "monthly_rent": 2300,
            "year_built": 1993,
            "market": "tampa",
            "property_tax_annual": 4960,
            "insurance_annual": 2400,
            "hoa_monthly": 0,
        },
        "RNT006": {
            "address": "2215 Park Rd, Charlotte NC",
            "purchase_price": 295000,
            "down_payment_pct": 0.20,
            "mortgage_rate_pct": 6.75,
            "mortgage_term_years": 30,
            "beds": 3, "baths": 2, "sqft": 1480,
            "type": "single_family",
            "monthly_rent": 2100,
            "year_built": 1996,
            "market": "charlotte",
            "property_tax_annual": 3540,
            "insurance_annual": 1200,
            "hoa_monthly": 0,
        },
        "RNT007": {
            "address": "1350 Spring St NW, Atlanta GA",
            "purchase_price": 380000,
            "down_payment_pct": 0.20,
            "mortgage_rate_pct": 6.75,
            "mortgage_term_years": 30,
            "beds": 3, "baths": 2, "sqft": 1700,
            "type": "single_family",
            "monthly_rent": 2600,
            "year_built": 2001,
            "market": "atlanta",
            "property_tax_annual": 4560,
            "insurance_annual": 1500,
            "hoa_monthly": 0,
        },
        "RNT008": {
            "address": "4421 Lemmon Ave, Dallas TX",
            "purchase_price": 350000,
            "down_payment_pct": 0.20,
            "mortgage_rate_pct": 6.75,
            "mortgage_term_years": 30,
            "beds": 3, "baths": 2, "sqft": 1600,
            "type": "single_family",
            "monthly_rent": 2500,
            "year_built": 1999,
            "market": "dallas",
            "property_tax_annual": 7000,
            "insurance_annual": 1600,
            "hoa_monthly": 0,
        },
        "RNT009": {
            "address": "3901 Richmond Ave, Houston TX",
            "purchase_price": 290000,
            "down_payment_pct": 0.20,
            "mortgage_rate_pct": 6.75,
            "mortgage_term_years": 30,
            "beds": 3, "baths": 2, "sqft": 1500,
            "type": "single_family",
            "monthly_rent": 2000,
            "year_built": 1994,
            "market": "houston",
            "property_tax_annual": 5800,
            "insurance_annual": 1500,
            "hoa_monthly": 0,
        },
        "RNT010": {
            "address": "8901 W Charleston Blvd, Las Vegas NV",
            "purchase_price": 320000,
            "down_payment_pct": 0.20,
            "mortgage_rate_pct": 6.75,
            "mortgage_term_years": 30,
            "beds": 3, "baths": 2, "sqft": 1700,
            "type": "single_family",
            "monthly_rent": 2200,
            "year_built": 2002,
            "market": "las_vegas",
            "property_tax_annual": 3200,
            "insurance_annual": 1200,
            "hoa_monthly": 0,
        },
        "RNT011": {
            "address": "500 Church St #1205, Nashville TN",
            "purchase_price": 310000,
            "down_payment_pct": 0.20,
            "mortgage_rate_pct": 6.75,
            "mortgage_term_years": 30,
            "beds": 2, "baths": 2, "sqft": 1100,
            "type": "condo",
            "monthly_rent": 2400,
            "year_built": 2012,
            "market": "nashville",
            "property_tax_annual": 1860,
            "insurance_annual": 1000,
            "hoa_monthly": 425,
        },
        "RNT012": {
            "address": "6120 N 7th Ave, Phoenix AZ",
            "purchase_price": 220000,
            "down_payment_pct": 0.20,
            "mortgage_rate_pct": 6.75,
            "mortgage_term_years": 30,
            "beds": 3, "baths": 2, "sqft": 1350,
            "type": "single_family",
            "monthly_rent": 1800,
            "year_built": 1988,
            "market": "phoenix",
            "property_tax_annual": 3520,
            "insurance_annual": 1100,
            "hoa_monthly": 0,
        },
        "RNT013": {
            "address": "820 S Congress Ave, Austin TX",
            "purchase_price": 450000,
            "down_payment_pct": 0.25,
            "mortgage_rate_pct": 6.75,
            "mortgage_term_years": 30,
            "beds": 4, "baths": 3, "sqft": 2100,
            "type": "single_family",
            "monthly_rent": 3200,
            "year_built": 2001,
            "market": "austin",
            "property_tax_annual": 9000,
            "insurance_annual": 2200,
            "hoa_monthly": 0,
        },
        "RNT014": {
            "address": "805 Peachtree St NE #14, Atlanta GA",
            "purchase_price": 290000,
            "down_payment_pct": 0.20,
            "mortgage_rate_pct": 6.75,
            "mortgage_term_years": 30,
            "beds": 2, "baths": 2, "sqft": 1200,
            "type": "condo",
            "monthly_rent": 2200,
            "year_built": 2009,
            "market": "atlanta",
            "property_tax_annual": 3480,
            "insurance_annual": 1000,
            "hoa_monthly": 380,
        },
        "RNT015": {
            "address": "2401 W Camelback Rd, Phoenix AZ",
            "purchase_price": 340000,
            "down_payment_pct": 0.20,
            "mortgage_rate_pct": 6.75,
            "mortgage_term_years": 30,
            "beds": 4, "baths": 2, "sqft": 1900,
            "type": "single_family",
            "monthly_rent": 2500,
            "year_built": 2000,
            "market": "phoenix",
            "property_tax_annual": 5440,
            "insurance_annual": 1500,
            "hoa_monthly": 0,
        },
        "RNT016": {
            "address": "7001 E Colfax Ave, Denver CO",
            "purchase_price": 325000,
            "down_payment_pct": 0.20,
            "mortgage_rate_pct": 6.75,
            "mortgage_term_years": 30,
            "beds": 3, "baths": 2, "sqft": 1500,
            "type": "single_family",
            "monthly_rent": 2500,
            "year_built": 1974,
            "market": "denver",
            "property_tax_annual": 2600,
            "insurance_annual": 1200,
            "hoa_monthly": 0,
        },
        "RNT017": {
            "address": "111 N 12th St #2205, Tampa FL",
            "purchase_price": 220000,
            "down_payment_pct": 0.20,
            "mortgage_rate_pct": 6.75,
            "mortgage_term_years": 30,
            "beds": 2, "baths": 2, "sqft": 1050,
            "type": "condo",
            "monthly_rent": 1900,
            "year_built": 2006,
            "market": "tampa",
            "property_tax_annual": 3520,
            "insurance_annual": 1800,
            "hoa_monthly": 410,
        },
        "RNT018": {
            "address": "500 W 5th St #1804, Charlotte NC",
            "purchase_price": 245000,
            "down_payment_pct": 0.20,
            "mortgage_rate_pct": 6.75,
            "mortgage_term_years": 30,
            "beds": 1, "baths": 1, "sqft": 820,
            "type": "condo",
            "monthly_rent": 1800,
            "year_built": 2014,
            "market": "charlotte",
            "property_tax_annual": 2940,
            "insurance_annual": 900,
            "hoa_monthly": 320,
        },
        "RNT019": {
            "address": "4401 Murphy Rd, Nashville TN",
            "purchase_price": 375000,
            "down_payment_pct": 0.20,
            "mortgage_rate_pct": 6.75,
            "mortgage_term_years": 30,
            "beds": 4, "baths": 3, "sqft": 2000,
            "type": "townhouse",
            "monthly_rent": 2700,
            "year_built": 2004,
            "market": "nashville",
            "property_tax_annual": 2250,
            "insurance_annual": 1500,
            "hoa_monthly": 150,
        },
        "RNT020": {
            "address": "2922 Elm St #301, Dallas TX",
            "purchase_price": 210000,
            "down_payment_pct": 0.20,
            "mortgage_rate_pct": 6.75,
            "mortgage_term_years": 30,
            "beds": 1, "baths": 1, "sqft": 780,
            "type": "condo",
            "monthly_rent": 1700,
            "year_built": 2011,
            "market": "dallas",
            "property_tax_annual": 4200,
            "insurance_annual": 850,
            "hoa_monthly": 295,
        },
    }

    MARKET_APPRECIATION = {
        "austin": 6.2, "phoenix": 4.8, "nashville": 5.5, "denver": 3.2,
        "tampa": 7.1, "charlotte": 5.9, "atlanta": 4.4, "dallas": 3.8,
        "houston": 3.1, "las_vegas": 4.9,
    }

    MARKET_RENT_GROWTH = {
        "austin": 4.5, "phoenix": 3.8, "nashville": 4.2, "denver": 2.9,
        "tampa": 5.1, "charlotte": 4.0, "atlanta": 3.6, "dallas": 3.0,
        "houston": 2.8, "las_vegas": 3.5,
    }

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._portfolio: dict = {}
        self.flow = GlobalAISourcesFlow(bot_name="RentalCashflowBot")

    def _check_portfolio_limit(self, property_id: str) -> None:
        limit = self.PORTFOLIO_LIMITS[self.tier]
        if (
            limit is not None
            and len(self._portfolio) >= limit
            and property_id not in self._portfolio
        ):
            raise RentalCashflowBotTierError(
                f"Portfolio limit of {limit} reached on {self.config.name} tier. "
                "Upgrade to track more properties."
            )

    def _get_property(self, address_or_id: str) -> tuple:
        """Return (pid, property_dict) by ID or partial address match."""
        if address_or_id in self.RENTAL_DATABASE:
            return address_or_id, dict(self.RENTAL_DATABASE[address_or_id])
        for pid, prop in self.RENTAL_DATABASE.items():
            if address_or_id.lower() in prop["address"].lower():
                return pid, dict(prop)
        first_key = next(iter(self.RENTAL_DATABASE))
        return first_key, dict(self.RENTAL_DATABASE[first_key])

    def _compute_monthly_mortgage(self, principal: float, annual_rate_pct: float, term_years: int) -> float:
        """Compute fixed monthly mortgage payment."""
        r = (annual_rate_pct / 100) / 12
        n = term_years * 12
        if r == 0:
            return principal / n
        return principal * (r * (1 + r) ** n) / ((1 + r) ** n - 1)

    def _compute_cashflow(self, prop: dict) -> dict:
        """Compute core cash flow metrics for a property."""
        purchase_price = prop["purchase_price"]
        down_pct = prop.get("down_payment_pct", 0.20)
        down_payment = purchase_price * down_pct
        loan_amount = purchase_price - down_payment
        rate = prop.get("mortgage_rate_pct", 6.75)
        term = prop.get("mortgage_term_years", 30)

        monthly_mortgage = self._compute_monthly_mortgage(loan_amount, rate, term)
        monthly_rent = prop["monthly_rent"]

        vacancy_rate = 0.05
        vacancy_loss = monthly_rent * vacancy_rate
        effective_gross_income = monthly_rent - vacancy_loss

        property_tax_monthly = prop.get("property_tax_annual", purchase_price * 0.015) / 12
        insurance_monthly = prop.get("insurance_annual", purchase_price * 0.006) / 12
        maintenance_monthly = purchase_price * 0.01 / 12  # 1% rule annually
        management_monthly = monthly_rent * 0.10          # 10% PM fee
        hoa_monthly = prop.get("hoa_monthly", 0)

        total_expenses_monthly = (
            monthly_mortgage
            + property_tax_monthly
            + insurance_monthly
            + maintenance_monthly
            + management_monthly
            + hoa_monthly
        )

        monthly_cashflow = effective_gross_income - total_expenses_monthly
        annual_cashflow = monthly_cashflow * 12

        annual_noi = (effective_gross_income - property_tax_monthly - insurance_monthly
                      - maintenance_monthly - management_monthly - hoa_monthly) * 12
        cap_rate = round(annual_noi / purchase_price * 100, 2)

        annual_rent = monthly_rent * 12
        grm = round(purchase_price / annual_rent, 2)

        cash_on_cash = round(annual_cashflow / down_payment * 100, 2) if down_payment > 0 else 0

        dscr = round((effective_gross_income - (total_expenses_monthly - monthly_mortgage)) / monthly_mortgage, 2)

        return {
            "purchase_price_usd": purchase_price,
            "down_payment_usd": round(down_payment, 0),
            "loan_amount_usd": round(loan_amount, 0),
            "monthly_mortgage_usd": round(monthly_mortgage, 2),
            "monthly_rent_usd": monthly_rent,
            "vacancy_loss_usd": round(vacancy_loss, 2),
            "effective_gross_income_usd": round(effective_gross_income, 2),
            "property_tax_monthly_usd": round(property_tax_monthly, 2),
            "insurance_monthly_usd": round(insurance_monthly, 2),
            "maintenance_monthly_usd": round(maintenance_monthly, 2),
            "management_monthly_usd": round(management_monthly, 2),
            "hoa_monthly_usd": hoa_monthly,
            "total_expenses_monthly_usd": round(total_expenses_monthly, 2),
            "monthly_cashflow_usd": round(monthly_cashflow, 2),
            "annual_cashflow_usd": round(annual_cashflow, 2),
            "annual_noi_usd": round(annual_noi, 2),
            "cap_rate_pct": cap_rate,
            "gross_rent_multiplier": grm,
            "cash_on_cash_return_pct": cash_on_cash,
            "dscr": dscr,
        }

    def analyze_property(self, address_or_id: str) -> dict:
        """Return complete cash flow analysis for a property."""
        pid, prop = self._get_property(address_or_id)
        self._check_portfolio_limit(pid)
        # Track analyzed properties (use pid as key so re-analyzing the same property is free)
        if pid not in self._portfolio:
            self._portfolio[pid] = prop

        cf = self._compute_cashflow(prop)

        result = {
            "property_id": pid,
            "address": prop["address"],
            "beds": prop["beds"],
            "baths": prop["baths"],
            "sqft": prop["sqft"],
            "type": prop["type"],
            "tier": self.tier.value,
            **cf,
        }

        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            result["expense_breakdown"] = {
                "mortgage_pct": round(cf["monthly_mortgage_usd"] / cf["total_expenses_monthly_usd"] * 100, 1),
                "tax_pct": round(cf["property_tax_monthly_usd"] / cf["total_expenses_monthly_usd"] * 100, 1),
                "insurance_pct": round(cf["insurance_monthly_usd"] / cf["total_expenses_monthly_usd"] * 100, 1),
                "maintenance_pct": round(cf["maintenance_monthly_usd"] / cf["total_expenses_monthly_usd"] * 100, 1),
                "management_pct": round(cf["management_monthly_usd"] / cf["total_expenses_monthly_usd"] * 100, 1),
            }
            result["investment_grade"] = self._grade_investment(cf["cap_rate_pct"], cf["cash_on_cash_return_pct"])

        if self.tier == Tier.ENTERPRISE:
            market = prop.get("market", "austin")
            result["10_year_projection"] = self.project_returns(address_or_id, years=10)
            result["depreciation_annual_usd"] = round((prop["purchase_price"] * 0.8) / 27.5, 0)
            result["appreciation_rate_pct"] = self.MARKET_APPRECIATION.get(market, 4.0)

        return result

    def _grade_investment(self, cap_rate: float, coc: float) -> str:
        """Return letter grade for investment quality."""
        score = 0
        if cap_rate >= 8: score += 3
        elif cap_rate >= 6: score += 2
        elif cap_rate >= 4: score += 1

        if coc >= 10: score += 3
        elif coc >= 6: score += 2
        elif coc >= 3: score += 1

        if score >= 5: return "A"
        if score >= 4: return "B+"
        if score >= 3: return "B"
        if score >= 2: return "C+"
        return "C"

    def add_property(self, property_dict: dict) -> str:
        """Add a custom property to the tracking portfolio. Returns the assigned ID."""
        new_id = f"CUSTOM{len(self._portfolio) + 1:03d}"
        self._check_portfolio_limit(new_id)
        self._portfolio[new_id] = property_dict
        return new_id

    def get_portfolio_summary(self) -> dict:
        """Return aggregate metrics across all tracked portfolio properties.

        Uses built-in database properties when portfolio is empty.
        """
        if self.tier == Tier.FREE:
            raise RentalCashflowBotTierError(
                "Portfolio summary requires PRO or ENTERPRISE tier."
            )

        source = self._portfolio if self._portfolio else {
            pid: prop for pid, prop in list(self.RENTAL_DATABASE.items())[:5]
        }

        summaries = []
        for pid, prop in source.items():
            if pid in self.RENTAL_DATABASE:
                cf = self._compute_cashflow(self.RENTAL_DATABASE[pid])
            else:
                cf = self._compute_cashflow(prop)
            summaries.append(cf)

        total_value = sum(s["purchase_price_usd"] for s in summaries)
        total_monthly_cf = sum(s["monthly_cashflow_usd"] for s in summaries)
        total_annual_cf = sum(s["annual_cashflow_usd"] for s in summaries)
        avg_cap_rate = round(sum(s["cap_rate_pct"] for s in summaries) / len(summaries), 2)
        avg_coc = round(sum(s["cash_on_cash_return_pct"] for s in summaries) / len(summaries), 2)
        total_down = sum(s["down_payment_usd"] for s in summaries)

        return {
            "portfolio_size": len(summaries),
            "total_portfolio_value_usd": round(total_value, 0),
            "total_equity_invested_usd": round(total_down, 0),
            "total_monthly_cashflow_usd": round(total_monthly_cf, 2),
            "total_annual_cashflow_usd": round(total_annual_cf, 2),
            "average_cap_rate_pct": avg_cap_rate,
            "average_cash_on_cash_pct": avg_coc,
            "tier": self.tier.value,
        }

    def project_returns(self, address_or_id: str, years: int = 10) -> dict:
        """Return multi-year return projection for a property (PRO/ENTERPRISE only)."""
        if self.tier == Tier.FREE:
            raise RentalCashflowBotTierError(
                "Return projections require PRO or ENTERPRISE tier."
            )

        pid, prop = self._get_property(address_or_id)
        cf = self._compute_cashflow(prop)
        market = prop.get("market", "austin")

        appreciation_rate = self.MARKET_APPRECIATION.get(market, 4.0) / 100
        rent_growth_rate = self.MARKET_RENT_GROWTH.get(market, 3.5) / 100
        purchase_price = prop["purchase_price"]
        down_payment = purchase_price * prop.get("down_payment_pct", 0.20)

        yearly = []
        cumulative_cashflow = 0.0
        current_value = float(purchase_price)
        current_monthly_rent = float(prop["monthly_rent"])

        for year in range(1, years + 1):
            current_value *= (1 + appreciation_rate)
            current_monthly_rent *= (1 + rent_growth_rate)
            annual_cf = (current_monthly_rent * 0.95 - cf["total_expenses_monthly_usd"] +
                         cf["monthly_mortgage_usd"] * (1 - 0.35)) * 12  # simplified
            cumulative_cashflow += annual_cf
            monthly_rate = prop.get("mortgage_rate_pct", 6.75) / 100 / 12
            amortization_factor = 1 - (1.0 / (1 + monthly_rate) ** (year * 12))
            equity = current_value - cf["loan_amount_usd"] * amortization_factor
            yearly.append({
                "year": year,
                "property_value_usd": round(current_value, 0),
                "projected_monthly_rent_usd": round(current_monthly_rent, 0),
                "estimated_equity_usd": round(equity, 0),
                "annual_cashflow_usd": round(annual_cf, 0),
                "cumulative_cashflow_usd": round(cumulative_cashflow, 0),
            })

        total_return = (yearly[-1]["property_value_usd"] - purchase_price + cumulative_cashflow)
        irr_estimate = round(total_return / (down_payment * years) * 100, 1) if down_payment > 0 else 0

        return {
            "property_id": pid,
            "address": prop["address"],
            "projection_years": years,
            "purchase_price_usd": purchase_price,
            "initial_equity_invested_usd": round(down_payment, 0),
            "projected_value_year_{0}_usd".format(years): yearly[-1]["property_value_usd"],
            "estimated_irr_pct": irr_estimate,
            "yearly_breakdown": yearly,
        }

    def describe_tier(self) -> str:
        info = get_bot_tier_info(self.tier)
        lines = [
            f"=== {info['name']} Rental Cash Flow Bot Tier ===",
            f"Price: ${info['price_usd_monthly']:.2f}/month",
            f"Support: {info['support_level']}",
            "Features:",
        ]
        for f in info["features"]:
            lines.append(f"  \u2713 {f}")
        output = "\n".join(lines)
        print(output)
        return output

    def run(self) -> dict:
        """Run the GlobalAISourcesFlow pipeline with sample rental data."""
        sample_data = [
            {"property_id": pid, **{k: v for k, v in props.items()}}
            for pid, props in list(self.RENTAL_DATABASE.items())[:5]
        ]
        return self.flow.run_pipeline(
            raw_data={"rental_properties": sample_data, "tier": self.tier.value},
            learning_method="supervised",
        )
