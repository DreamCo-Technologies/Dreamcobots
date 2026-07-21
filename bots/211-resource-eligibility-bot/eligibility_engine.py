"""
Eligibility Engine for the 211 Resource and Eligibility Checker Bot.

Calculates whether a household qualifies for common assistance programs
(SNAP, Medicaid, CHIP, WIC, RentAssistance) based on Federal Poverty
Level (FPL) thresholds defined in config.py.

No personally-identifiable information is stored here; the engine only
receives ephemeral income/household values from the session.
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

from config import FPL_BASE, FPL_ADDITIONAL_PER_PERSON, PROGRAMS


def get_fpl(household_size: int) -> float:
    """Return the annual Federal Poverty Level for a given household size."""
    if household_size <= 0:
        raise ValueError("Household size must be a positive integer.")
    if household_size in FPL_BASE:
        return float(FPL_BASE[household_size])
    # For households larger than 8, add the per-person increment
    return float(FPL_BASE[8] + (household_size - 8) * FPL_ADDITIONAL_PER_PERSON)


def check_eligibility(annual_income: float, household_size: int) -> dict:
    """
    Determine eligibility for all configured assistance programs.

    Parameters
    ----------
    annual_income : float
        Annual household income in USD (before taxes).
    household_size : int
        Total number of people in the household.

    Returns
    -------
    dict
        Keys are program names; values are dicts with keys:
        - ``eligible`` (bool)
        - ``description`` (str)
        - ``category`` (str)
        - ``fpl_percent`` (float) – income as % of FPL
    """
    if annual_income < 0:
        raise ValueError("Annual income cannot be negative.")

    fpl = get_fpl(household_size)
    fpl_percent = (annual_income / fpl) * 100 if fpl > 0 else float("inf")

    results = {}
    for program, details in PROGRAMS.items():
        threshold_income = fpl * details["fpl_threshold"]
        results[program] = {
            "eligible": annual_income <= threshold_income,
            "description": details["description"],
            "category": details["category"],
            "fpl_percent": round(fpl_percent, 1),
            "threshold_percent": int(details["fpl_threshold"] * 100),
        }
    return results


def format_eligibility_results(results: dict, lang: str = "en") -> str:
    """
    Format eligibility results into a human-readable string.

    Parameters
    ----------
    results : dict
        Output from :func:`check_eligibility`.
    lang : str
        Language code (currently affects ✓/✗ labels only).

    Returns
    -------
    str
        Formatted eligibility summary.
    """
    lines = []
    for program, info in results.items():
        status = "✓ Likely Eligible" if info["eligible"] else "✗ Likely Not Eligible"
        lines.append(
            f"  {program}: {status}\n"
            f"    {info['description']}\n"
            f"    (Your income is {info['fpl_percent']}% of FPL; "
            f"threshold is {info['threshold_percent']}% of FPL)"
        )
    return "\n".join(lines)
