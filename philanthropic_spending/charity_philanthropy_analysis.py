#!/usr/bin/env python3
"""
Comprehensive Analysis of Global Philanthropic Spending by Category (2015-2024)

Categories:
1. Global Health & Development (North Star: Against Malaria Foundation - cost-effective interventions)
2. Animal Welfare (North Star: Factory farming reform - e.g., The Humane League)
3. Existential Risk (North Star: Pandemic prevention, AI safety)

This analysis compiles data from multiple sources, avoiding double-counting,
and calculates both total spend and effectiveness-weighted spend.
"""

import json
from dataclasses import dataclass
from typing import Optional

# ============================================================================
# DATA COMPILATION
# ============================================================================

# All monetary values in millions USD unless otherwise specified

# -----------------------------------------------------------------------------
# GLOBAL HEALTH & DEVELOPMENT
# -----------------------------------------------------------------------------

# GiveWell Money Moved to Top Charities (includes Good Ventures/Open Phil contributions)
# Source: GiveWell annual metrics reports
GIVEWELL_MONEY_MOVED = {
    2015: 110.1,   # Includes $70.4M Good Ventures
    2016: 88.6,    # Includes $50.4M Good Ventures
    2017: 117.5,
    2018: 141.0,
    2019: 152.0,
    2020: 244.0,
    2021: 500.0,   # Changed metric to "funds directed"
    2022: 600.0,   # Largest year - includes $350M Open Phil
    2023: 197.0,   # Funds directed
    2024: 397.0,   # Funds directed
}

# Breakdown of GiveWell charities by effectiveness weight
# Weight: How closely aligned to "impartial cost-effective welfare improvement"
GIVEWELL_CHARITY_WEIGHTS = {
    "Against Malaria Foundation": 1.00,        # Perfect north star alignment
    "Malaria Consortium (SMC)": 0.95,          # Highly targeted malaria intervention
    "Helen Keller International (VitA)": 0.90, # Very cost-effective supplementation
    "New Incentives": 0.85,                    # Cash incentives for vaccination
    "GiveDirectly": 0.70,                      # Direct cash - very cost-effective but less targeted
    "Deworm the World": 0.60,                  # Deworming - less certain impact
    "SCI Foundation": 0.60,                    # Deworming
    "Sightsavers (deworming)": 0.60,
    "Evidence Action (other)": 0.55,
}

# Approximate allocation of GiveWell funds by charity type (estimated from reports)
# Used to calculate weighted average
GIVEWELL_ALLOCATION_ESTIMATE = {
    "malaria_interventions": 0.50,   # AMF, Malaria Consortium - weight ~0.97
    "nutrition_vaccination": 0.20,   # Helen Keller, New Incentives - weight ~0.87
    "cash_transfers": 0.15,          # GiveDirectly - weight 0.70
    "deworming": 0.10,               # Various - weight 0.60
    "other": 0.05,                   # Miscellaneous - weight 0.50
}

# Weighted average for GiveWell
GIVEWELL_WEIGHTED_AVG = (
    0.50 * 0.97 +  # malaria
    0.20 * 0.87 +  # nutrition/vax
    0.15 * 0.70 +  # cash
    0.10 * 0.60 +  # deworming
    0.05 * 0.50    # other
)  # = 0.84

# Gates Foundation Global Health Spending (estimated from annual budgets)
# Source: Gates Foundation annual reports, news releases
# Note: Much broader mandate than EA-style cost-effectiveness
GATES_FOUNDATION_GLOBAL_HEALTH = {
    2015: 3800,  # Estimated ~$3.8B global health portion of budget
    2016: 4000,
    2017: 4200,
    2018: 4300,
    2019: 4500,
    2020: 5000,  # COVID response increase
    2021: 5500,
    2022: 6000,
    2023: 6500,
    2024: 7000,  # $8.6B total budget, ~80% global health focus
}

# Gates Foundation effectiveness weight
# Much lower because: focus on polio (largely eradicated), vaccine R&D (speculative),
# agricultural development, etc. - less cost-effective per dollar than direct interventions
GATES_WEIGHT = 0.15

# Wellcome Trust Global Health Research
# Source: Wellcome Trust annual reports
WELLCOME_TRUST_GLOBAL_HEALTH = {
    2015: 800,
    2016: 850,
    2017: 900,
    2018: 950,
    2019: 1000,
    2020: 1100,
    2021: 1200,
    2022: 1250,
    2023: 1300,
    2024: 1350,
}

# Wellcome weight - research focused, speculative impact
WELLCOME_WEIGHT = 0.10

# Other EA-aligned Global Health Giving (Founders Pledge, GWWC members excluding GiveWell)
# Estimated based on GWWC reporting ~$70M/year, overlap adjusted
OTHER_EA_GLOBAL_HEALTH = {
    2015: 10,
    2016: 15,
    2017: 20,
    2018: 25,
    2019: 30,
    2020: 40,
    2021: 50,
    2022: 55,
    2023: 60,
    2024: 65,
}

OTHER_EA_WEIGHT = 0.80  # Generally high-quality but some variance

# Other Major Global Health Philanthropy (Global Fund, GAVI, other foundations)
# Source: Think Global Health, donor tracker data, multilateral reports
# REVISED: Added to capture broader global health philanthropy ecosystem
# Global Fund: ~$5B/year disbursements; GAVI: ~$2B/year; Other foundations: ~$2-3B/year
# Note: User research indicates total global health philanthropy roughly 2x Gates+Wellcome+GiveWell
OTHER_GLOBAL_HEALTH_PHILANTHROPY = {
    2015: 8000,   # Global Fund + GAVI + other foundations
    2016: 8500,
    2017: 9000,
    2018: 9500,
    2019: 10000,
    2020: 12000,  # COVID response spike
    2021: 11000,
    2022: 10500,
    2023: 10000,  # Declining DAH trend
    2024: 9500,   # Further decline per Think Global Health
}

# Lower weight because: includes government-influenced multilaterals,
# broad mandate programs, less cost-effective per dollar than GiveWell charities
OTHER_GLOBAL_HEALTH_WEIGHT = 0.12

# -----------------------------------------------------------------------------
# ANIMAL WELFARE
# -----------------------------------------------------------------------------

# Open Philanthropy Farm Animal Welfare
# Source: Open Philanthropy grants database, EA Forum historical funding data (2025 update)
# https://forum.effectivealtruism.org/posts/NWHb4nsnXRxDDFGLy/historical-ea-funding-data-2025-update
# REVISED: 2022-2024 figures updated based on actual grants database data
OPEN_PHIL_ANIMAL_WELFARE = {
    2015: 0,      # Program started in 2016
    2016: 14.4,   # Source: Vipul Naik database
    2017: 28.1,   # Source: Vipul Naik database
    2018: 28.0,   # Source: Vipul Naik database
    2019: 39.9,   # Source: Vipul Naik database, confirmed EA Forum
    2020: 25.2,   # Source: EA Forum analysis
    2021: 23.6,   # Source: EA Forum analysis (partial year)
    2022: 55.0,   # REVISED: Based on grants database (THL $8.3M, MFA ~$10M, GFI, etc.)
    2023: 65.0,   # REVISED: Increased activity per OP progress reports
    2024: 75.0,   # REVISED: $12.4M MFA, $8M+ THL, numerous other grants
}

# Open Phil animal welfare is highly aligned with factory farming reform
OPEN_PHIL_ANIMAL_WEIGHT = 0.90

# EA Animal Welfare Fund
# Source: EA Funds stats
EA_ANIMAL_FUND = {
    2015: 0,
    2016: 0,
    2017: 0.5,
    2018: 1.0,
    2019: 1.5,
    2020: 2.0,
    2021: 3.0,
    2022: 4.0,
    2023: 3.5,
    2024: 4.0,
}

EA_ANIMAL_FUND_WEIGHT = 0.95  # Highly targeted to effective interventions

# Animal Charity Evaluators influenced giving
# Source: ACE impact reports - $47M from 2019-2024, ~$59M total influenced
ACE_INFLUENCED = {
    2015: 2.0,
    2016: 3.0,
    2017: 4.0,
    2018: 5.0,
    2019: 6.5,
    2020: 8.0,
    2021: 10.0,
    2022: 11.0,
    2023: 12.0,
    2024: 12.3,
}

ACE_WEIGHT = 0.85  # ACE-recommended charities are well-aligned

# Traditional animal welfare (ASPCA, HSUS, Humane World, local shelters, etc.)
# These focus primarily on companion animals, wildlife, not factory farming
# Source: Animal Grantmakers reports, Giving USA data
# REVISED: User research indicates total animal philanthropy ~$1.2-1.5B annually
# This aligns with Animal Grantmakers foundation grants data (~$275M from major foundations)
# plus individual giving to animal causes (estimated $800M-1.2B additional)
# Note: Previous estimate of $5-7B was total charity REVENUES, not grants/donations specifically
TRADITIONAL_ANIMAL_WELFARE = {
    2015: 900,    # REVISED down significantly
    2016: 950,
    2017: 1000,
    2018: 1050,
    2019: 1100,
    2020: 1150,   # Some COVID impact
    2021: 1200,
    2022: 1250,
    2023: 1300,
    2024: 1350,
}

# Very low weight - companion animal focus has minimal impact on factory farming
TRADITIONAL_ANIMAL_WEIGHT = 0.02

# Major effective animal charities (The Humane League, Mercy For Animals, etc.)
# Direct budgets (some overlap with Open Phil funding, so we'll use Open Phil as primary)
# These are included for reference but mostly funded through Open Phil
HUMANE_LEAGUE_BUDGET = {
    2015: 2.0,
    2016: 3.5,
    2017: 5.0,
    2018: 7.0,
    2019: 10.0,
    2020: 12.0,
    2021: 15.0,
    2022: 18.0,
    2023: 22.0,
    2024: 24.3,
}

MERCY_FOR_ANIMALS_BUDGET = {
    2015: 5.0,
    2016: 6.0,
    2017: 8.0,
    2018: 10.0,
    2019: 12.0,
    2020: 14.0,
    2021: 16.0,
    2022: 18.0,
    2023: 19.0,
    2024: 19.0,
}

MAJOR_CHARITY_WEIGHT = 0.95  # Highly aligned with factory farming reform

# -----------------------------------------------------------------------------
# EXISTENTIAL RISK
# -----------------------------------------------------------------------------

# Open Philanthropy - Potential Risks from Advanced AI
# Source: Open Philanthropy grants database
OPEN_PHIL_AI_SAFETY = {
    2015: 1.2,
    2016: 6.6,
    2017: 43.2,
    2018: 4.2,
    2019: 8.2,
    2020: 15.6,
    2021: 81.7,
    2022: 58.0,
    2023: 58.0,
    2024: 75.0,  # Estimated
}

OPEN_PHIL_AI_WEIGHT = 0.90  # Highly aligned with AI safety

# Open Philanthropy - Biosecurity and Pandemic Preparedness
# Source: Open Philanthropy grants database
OPEN_PHIL_BIOSECURITY = {
    2015: 0.3,
    2016: 5.3,
    2017: 28.8,
    2018: 9.9,
    2019: 21.6,
    2020: 15.0,
    2021: 9.3,
    2022: 25.0,  # Estimated
    2023: 35.0,  # Estimated - increased post-COVID
    2024: 40.0,  # Estimated
}

OPEN_PHIL_BIO_WEIGHT = 0.85  # Highly aligned but some broader pandemic prep

# Open Philanthropy - Global Catastrophic Risks (other)
OPEN_PHIL_GCR = {
    2015: 0,
    2016: 0.6,
    2017: 4.1,
    2018: 12.7,
    2019: 0.6,
    2020: 1.0,
    2021: 2.0,
    2022: 3.0,
    2023: 4.0,
    2024: 5.0,
}

OPEN_PHIL_GCR_WEIGHT = 0.70  # Mixed - includes nuclear, climate

# Survival and Flourishing Fund (SFF)
# Source: SFF grant announcements
SFF_GRANTS = {
    2015: 0,
    2016: 0,
    2017: 0,
    2018: 0,
    2019: 2.0,   # Founded ~2019
    2020: 5.0,
    2021: 10.0,
    2022: 15.0,
    2023: 21.3,
    2024: 19.9,
}

# 2025 data shows $34M with 86% AI, 7% bio - historically similar allocation
SFF_WEIGHT = 0.85  # Highly aligned with x-risk reduction

# Long-Term Future Fund (LTFF)
# Source: EA Funds, payout reports
LTFF_GRANTS = {
    2015: 0,
    2016: 0,
    2017: 0,
    2018: 0.01,  # Minimal early grants
    2019: 1.35,
    2020: 1.5,
    2021: 3.0,
    2022: 5.0,
    2023: 6.67,
    2024: 5.36,
}

LTFF_WEIGHT = 0.80  # Highly aligned, some variance in grant quality

# FTX Future Fund (2022 only - collapsed Nov 2022)
# Source: Future Fund grants database
FTX_FUTURE_FUND = {
    2015: 0,
    2016: 0,
    2017: 0,
    2018: 0,
    2019: 0,
    2020: 0,
    2021: 0,
    2022: 32.0,  # AI safety grants before collapse
    2023: 0,
    2024: 0,
}

FTX_WEIGHT = 0.75  # Reasonably aligned but short-lived

# Future of Life Institute
# Source: FLI annual reports, 990 filings
FLI_GRANTS = {
    2015: 5.0,
    2016: 3.0,
    2017: 2.0,
    2018: 2.0,
    2019: 3.0,
    2020: 4.0,
    2021: 5.0,
    2022: 10.0,  # Shiba Inu windfall began
    2023: 50.0,  # Major increase from crypto
    2024: 100.0, # Now ~$674M org
}

FLI_WEIGHT = 0.70  # Good alignment but some broader AI ethics focus

# Government biosecurity spending (for context, not counted in philanthropic)
# Source: 80,000 Hours, various reports
# US: ~$17B (2019) to ~$24B (2023), but most is not x-risk focused
# We'll include a small portion that is philanthropically influenced

# Other x-risk research funding (academic, small foundations)
OTHER_XRISK = {
    2015: 2.0,
    2016: 3.0,
    2017: 4.0,
    2018: 5.0,
    2019: 6.0,
    2020: 8.0,
    2021: 10.0,
    2022: 12.0,
    2023: 15.0,
    2024: 18.0,
}

OTHER_XRISK_WEIGHT = 0.50  # Mixed alignment


# ============================================================================
# ANALYSIS FUNCTIONS
# ============================================================================

def calculate_category_totals():
    """Calculate total and weighted spending by category and year."""

    years = list(range(2015, 2025))

    results = {
        "global_health": {
            "total": {},
            "weighted": {},
            "components": {}
        },
        "animal_welfare": {
            "total": {},
            "weighted": {},
            "components": {}
        },
        "existential_risk": {
            "total": {},
            "weighted": {},
            "components": {}
        }
    }

    for year in years:
        # ---------------------------------------------------------------------
        # GLOBAL HEALTH & DEVELOPMENT
        # ---------------------------------------------------------------------

        # GiveWell (primary EA source - avoid double counting with Open Phil)
        givewell = GIVEWELL_MONEY_MOVED.get(year, 0)
        givewell_weighted = givewell * GIVEWELL_WEIGHTED_AVG

        # Gates Foundation (separate, minimal overlap with GiveWell)
        gates = GATES_FOUNDATION_GLOBAL_HEALTH.get(year, 0)
        gates_weighted = gates * GATES_WEIGHT

        # Wellcome Trust (separate)
        wellcome = WELLCOME_TRUST_GLOBAL_HEALTH.get(year, 0)
        wellcome_weighted = wellcome * WELLCOME_WEIGHT

        # Other EA global health (adjusted for GiveWell overlap)
        other_ea_gh = OTHER_EA_GLOBAL_HEALTH.get(year, 0)
        other_ea_gh_weighted = other_ea_gh * OTHER_EA_WEIGHT

        # Other major global health philanthropy (Global Fund, GAVI, other foundations)
        other_gh = OTHER_GLOBAL_HEALTH_PHILANTHROPY.get(year, 0)
        other_gh_weighted = other_gh * OTHER_GLOBAL_HEALTH_WEIGHT

        total_gh = givewell + gates + wellcome + other_ea_gh + other_gh
        weighted_gh = givewell_weighted + gates_weighted + wellcome_weighted + other_ea_gh_weighted + other_gh_weighted

        results["global_health"]["total"][year] = total_gh
        results["global_health"]["weighted"][year] = weighted_gh
        results["global_health"]["components"][year] = {
            "GiveWell": {"total": givewell, "weighted": givewell_weighted},
            "Gates Foundation": {"total": gates, "weighted": gates_weighted},
            "Wellcome Trust": {"total": wellcome, "weighted": wellcome_weighted},
            "Other EA": {"total": other_ea_gh, "weighted": other_ea_gh_weighted},
            "Other Global Health (Global Fund, GAVI, etc.)": {"total": other_gh, "weighted": other_gh_weighted},
        }

        # ---------------------------------------------------------------------
        # ANIMAL WELFARE
        # ---------------------------------------------------------------------

        # Open Phil is primary funder, avoid double-counting with charity budgets
        open_phil_aw = OPEN_PHIL_ANIMAL_WELFARE.get(year, 0)
        open_phil_aw_weighted = open_phil_aw * OPEN_PHIL_ANIMAL_WEIGHT

        # EA Animal Fund (separate from Open Phil)
        ea_animal = EA_ANIMAL_FUND.get(year, 0)
        ea_animal_weighted = ea_animal * EA_ANIMAL_FUND_WEIGHT

        # ACE influenced (some overlap with Open Phil, reduce by 50%)
        ace = ACE_INFLUENCED.get(year, 0) * 0.5
        ace_weighted = ace * ACE_WEIGHT

        # Traditional animal welfare
        traditional = TRADITIONAL_ANIMAL_WELFARE.get(year, 0)
        traditional_weighted = traditional * TRADITIONAL_ANIMAL_WEIGHT

        total_aw = open_phil_aw + ea_animal + ace + traditional
        weighted_aw = open_phil_aw_weighted + ea_animal_weighted + ace_weighted + traditional_weighted

        # Also track "effective" animal welfare separately (excluding traditional)
        effective_aw_total = open_phil_aw + ea_animal + ace
        effective_aw_weighted = open_phil_aw_weighted + ea_animal_weighted + ace_weighted

        results["animal_welfare"]["total"][year] = total_aw
        results["animal_welfare"]["weighted"][year] = weighted_aw
        results["animal_welfare"]["components"][year] = {
            "Open Philanthropy": {"total": open_phil_aw, "weighted": open_phil_aw_weighted},
            "EA Animal Fund": {"total": ea_animal, "weighted": ea_animal_weighted},
            "ACE Influenced": {"total": ace, "weighted": ace_weighted},
            "Traditional (HSUS, etc.)": {"total": traditional, "weighted": traditional_weighted},
            "Effective Total (excl traditional)": {"total": effective_aw_total, "weighted": effective_aw_weighted},
        }

        # ---------------------------------------------------------------------
        # EXISTENTIAL RISK
        # ---------------------------------------------------------------------

        # Open Phil AI Safety
        op_ai = OPEN_PHIL_AI_SAFETY.get(year, 0)
        op_ai_weighted = op_ai * OPEN_PHIL_AI_WEIGHT

        # Open Phil Biosecurity
        op_bio = OPEN_PHIL_BIOSECURITY.get(year, 0)
        op_bio_weighted = op_bio * OPEN_PHIL_BIO_WEIGHT

        # Open Phil GCR
        op_gcr = OPEN_PHIL_GCR.get(year, 0)
        op_gcr_weighted = op_gcr * OPEN_PHIL_GCR_WEIGHT

        # SFF (some overlap with LTFF regranting, reduce by 20%)
        sff = SFF_GRANTS.get(year, 0) * 0.8
        sff_weighted = sff * SFF_WEIGHT

        # LTFF
        ltff = LTFF_GRANTS.get(year, 0)
        ltff_weighted = ltff * LTFF_WEIGHT

        # FTX Future Fund
        ftx = FTX_FUTURE_FUND.get(year, 0)
        ftx_weighted = ftx * FTX_WEIGHT

        # FLI
        fli = FLI_GRANTS.get(year, 0)
        fli_weighted = fli * FLI_WEIGHT

        # Other x-risk
        other = OTHER_XRISK.get(year, 0)
        other_weighted = other * OTHER_XRISK_WEIGHT

        total_xr = op_ai + op_bio + op_gcr + sff + ltff + ftx + fli + other
        weighted_xr = op_ai_weighted + op_bio_weighted + op_gcr_weighted + sff_weighted + ltff_weighted + ftx_weighted + fli_weighted + other_weighted

        results["existential_risk"]["total"][year] = total_xr
        results["existential_risk"]["weighted"][year] = weighted_xr
        results["existential_risk"]["components"][year] = {
            "Open Phil AI Safety": {"total": op_ai, "weighted": op_ai_weighted},
            "Open Phil Biosecurity": {"total": op_bio, "weighted": op_bio_weighted},
            "Open Phil GCR": {"total": op_gcr, "weighted": op_gcr_weighted},
            "Survival & Flourishing Fund": {"total": sff, "weighted": sff_weighted},
            "Long-Term Future Fund": {"total": ltff, "weighted": ltff_weighted},
            "FTX Future Fund": {"total": ftx, "weighted": ftx_weighted},
            "Future of Life Institute": {"total": fli, "weighted": fli_weighted},
            "Other X-Risk": {"total": other, "weighted": other_weighted},
        }

    return results


def print_summary_table(results):
    """Print formatted summary tables."""

    print("=" * 100)
    print("PHILANTHROPIC SPENDING ANALYSIS BY CATEGORY (2015-2024)")
    print("All figures in millions USD")
    print("=" * 100)

    years = list(range(2015, 2025))

    categories = [
        ("global_health", "GLOBAL HEALTH & DEVELOPMENT", "North Star: Against Malaria Foundation"),
        ("animal_welfare", "ANIMAL WELFARE", "North Star: Factory Farming Reform (e.g., The Humane League)"),
        ("existential_risk", "EXISTENTIAL RISK", "North Star: Pandemic Prevention, AI Safety"),
    ]

    for key, name, north_star in categories:
        print(f"\n{'-' * 100}")
        print(f"{name}")
        print(f"{north_star}")
        print(f"{'-' * 100}")

        data = results[key]

        print(f"\n{'Year':<8} {'Total Spend':>15} {'Weighted Spend':>15} {'Effectiveness %':>18}")
        print("-" * 60)

        for year in years:
            total = data["total"][year]
            weighted = data["weighted"][year]
            eff_pct = (weighted / total * 100) if total > 0 else 0
            print(f"{year:<8} ${total:>13,.1f}M ${weighted:>13,.1f}M {eff_pct:>17.1f}%")

        # Print totals
        total_sum = sum(data["total"].values())
        weighted_sum = sum(data["weighted"].values())
        avg_eff = (weighted_sum / total_sum * 100) if total_sum > 0 else 0

        print("-" * 60)
        print(f"{'TOTAL':<8} ${total_sum:>13,.1f}M ${weighted_sum:>13,.1f}M {avg_eff:>17.1f}%")

        # Component breakdown for most recent year
        print(f"\n2024 Component Breakdown:")
        for component, values in data["components"][2024].items():
            if values["total"] > 0:
                print(f"  {component}: ${values['total']:.1f}M (weighted: ${values['weighted']:.1f}M)")

    print("\n" + "=" * 100)


def print_comparison_table(results):
    """Print side-by-side comparison of all categories."""

    print("\n" + "=" * 120)
    print("CROSS-CATEGORY COMPARISON")
    print("=" * 120)

    years = list(range(2015, 2025))

    print(f"\n{'Year':<6} | {'Global Health':^30} | {'Animal Welfare':^30} | {'Existential Risk':^30}")
    print(f"{'':6} | {'Total':>14} {'Weighted':>14} | {'Total':>14} {'Weighted':>14} | {'Total':>14} {'Weighted':>14}")
    print("-" * 120)

    for year in years:
        gh_t = results["global_health"]["total"][year]
        gh_w = results["global_health"]["weighted"][year]
        aw_t = results["animal_welfare"]["total"][year]
        aw_w = results["animal_welfare"]["weighted"][year]
        xr_t = results["existential_risk"]["total"][year]
        xr_w = results["existential_risk"]["weighted"][year]

        print(f"{year:<6} | {gh_t:>13,.0f}M {gh_w:>13,.0f}M | {aw_t:>13,.0f}M {aw_w:>13,.0f}M | {xr_t:>13,.0f}M {xr_w:>13,.0f}M")

    print("-" * 120)

    # Totals
    gh_total = sum(results["global_health"]["total"].values())
    gh_weighted = sum(results["global_health"]["weighted"].values())
    aw_total = sum(results["animal_welfare"]["total"].values())
    aw_weighted = sum(results["animal_welfare"]["weighted"].values())
    xr_total = sum(results["existential_risk"]["total"].values())
    xr_weighted = sum(results["existential_risk"]["weighted"].values())

    print(f"{'TOTAL':<6} | {gh_total:>13,.0f}M {gh_weighted:>13,.0f}M | {aw_total:>13,.0f}M {aw_weighted:>13,.0f}M | {xr_total:>13,.0f}M {xr_weighted:>13,.0f}M")
    print(f"{'Eff%':<6} | {gh_weighted/gh_total*100:>13.1f}% {'':>14} | {aw_weighted/aw_total*100:>13.1f}% {'':>14} | {xr_weighted/xr_total*100:>13.1f}% {'':>14}")


def print_effective_only_comparison(results):
    """Print comparison excluding traditional/low-weight sources."""

    print("\n" + "=" * 100)
    print("EFFECTIVE PHILANTHROPY ONLY (Excluding Traditional/Low-Weight Sources)")
    print("This view focuses on donations aligned with EA-style cost-effectiveness principles")
    print("=" * 100)

    years = list(range(2015, 2025))

    effective_gh = {}
    effective_aw = {}
    effective_xr = {}

    for year in years:
        # Global Health: GiveWell + Other EA (exclude Gates, Wellcome)
        effective_gh[year] = GIVEWELL_MONEY_MOVED.get(year, 0) + OTHER_EA_GLOBAL_HEALTH.get(year, 0)

        # Animal Welfare: Open Phil + EA Fund + ACE (exclude traditional)
        effective_aw[year] = (OPEN_PHIL_ANIMAL_WELFARE.get(year, 0) +
                             EA_ANIMAL_FUND.get(year, 0) +
                             ACE_INFLUENCED.get(year, 0) * 0.5)

        # Existential Risk: All sources (already mostly effective)
        effective_xr[year] = results["existential_risk"]["total"][year]

    print(f"\n{'Year':<6} | {'Global Health':>15} | {'Animal Welfare':>15} | {'Existential Risk':>15} | {'Total':>15}")
    print("-" * 80)

    for year in years:
        gh = effective_gh[year]
        aw = effective_aw[year]
        xr = effective_xr[year]
        total = gh + aw + xr
        print(f"{year:<6} | ${gh:>13,.1f}M | ${aw:>13,.1f}M | ${xr:>13,.1f}M | ${total:>13,.1f}M")

    print("-" * 80)

    gh_sum = sum(effective_gh.values())
    aw_sum = sum(effective_aw.values())
    xr_sum = sum(effective_xr.values())
    total_sum = gh_sum + aw_sum + xr_sum

    print(f"{'TOTAL':<6} | ${gh_sum:>13,.1f}M | ${aw_sum:>13,.1f}M | ${xr_sum:>13,.1f}M | ${total_sum:>13,.1f}M")

    print(f"\nDecade Growth Rates (2015 to 2024):")
    for name, data in [("Global Health", effective_gh), ("Animal Welfare", effective_aw), ("Existential Risk", effective_xr)]:
        if data[2015] > 0:
            growth = (data[2024] / data[2015] - 1) * 100
            cagr = ((data[2024] / data[2015]) ** (1/9) - 1) * 100
            print(f"  {name}: {growth:.0f}% total growth, {cagr:.1f}% CAGR")


def export_to_json(results):
    """Export results to JSON for further analysis."""

    # Convert to serializable format
    output = {
        "metadata": {
            "description": "Philanthropic spending analysis by category (2015-2024)",
            "units": "millions USD",
            "categories": {
                "global_health": "Global Health & Development (North Star: Against Malaria Foundation)",
                "animal_welfare": "Animal Welfare (North Star: Factory Farming Reform)",
                "existential_risk": "Existential Risk (North Star: Pandemic Prevention, AI Safety)"
            }
        },
        "data": results
    }

    with open("charity_analysis_results.json", "w") as f:
        json.dump(output, f, indent=2)

    print("\nResults exported to charity_analysis_results.json")


def main():
    """Run the full analysis."""

    results = calculate_category_totals()

    print_summary_table(results)
    print_comparison_table(results)
    print_effective_only_comparison(results)

    # Export data
    export_to_json(results)

    # Print key insights
    print("\n" + "=" * 100)
    print("KEY INSIGHTS")
    print("=" * 100)

    print("""
1. GLOBAL HEALTH & DEVELOPMENT
   - Total spending includes Gates Foundation, Wellcome Trust, Global Fund,
     GAVI, GiveWell-directed funds, and other foundations (~$150B over decade)
   - Effectiveness-weighted spending much lower due to broad-mandate programs
   - GiveWell-directed funds (~$2.5B total) have much higher cost-effectiveness
   - Weighted average effectiveness: ~10-12% (broad programs pull down average)
   - If focusing only on EA-aligned giving, effectiveness rises to ~84%

2. ANIMAL WELFARE
   - Total animal philanthropy estimated at ~$1.2-1.5B annually (revised down
     from earlier estimate which conflated charity revenues with donations)
   - Open Philanthropy dominates effective animal welfare (~$75M in 2024)
   - Factory farming focused spending has grown significantly 2022-2024
   - Traditional companion animal charities still receive majority of funds
   - Effectiveness ratio improving as EA-aligned giving grows

3. EXISTENTIAL RISK
   - Fastest growing category with ~30x growth 2015-2024
   - Highest effectiveness percentage (~80%) as most funding is already
     well-targeted
   - AI safety funding has grown dramatically, especially 2021+
   - Biosecurity funding increased post-COVID but still relatively small
   - FLI's crypto windfall has significantly increased field resources

4. CROSS-CATEGORY OBSERVATIONS
   - Total philanthropic spending: Global Health >> Animal Welfare > X-Risk
   - Effectiveness-weighted: Global Health > X-Risk > Animal Welfare
   - Best targeted category: Existential Risk (80% effectiveness)
   - Most room for reallocation: Animal Welfare (traditional → factory farming)
   - Fastest growing: Existential Risk (AI safety specifically)

NOTE: Figures revised based on user feedback and additional research from
EA Forum historical funding data (2025 update) and Animal Grantmakers reports.
""")


if __name__ == "__main__":
    main()
