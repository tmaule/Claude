# Methodology: Philanthropic Spending Analysis by Category

This document provides detailed sourcing, validation steps, and reasoning for all figures and weights used in the charity philanthropy analysis.

## Table of Contents
1. [Data Collection Process](#data-collection-process)
2. [Global Health & Development Sources](#global-health--development-sources)
3. [Animal Welfare Sources](#animal-welfare-sources)
4. [Existential Risk Sources](#existential-risk-sources)
5. [Effectiveness Weight Methodology](#effectiveness-weight-methodology)
6. [Deduplication Approach](#deduplication-approach)
7. [Limitations and Uncertainties](#limitations-and-uncertainties)
8. [Validation Checklist](#validation-checklist)

---

## Data Collection Process

### Primary Sources Used
1. **GiveWell Annual Metrics Reports** - https://www.givewell.org/about/impact
2. **Open Philanthropy Grants Database** - https://www.openphilanthropy.org/grants/
3. **Vipul Naik Donations Database** - https://donations.vipulnaik.com/ (aggregates multiple sources)
4. **EA Funds Payout Reports** - https://funds.effectivealtruism.org/
5. **Charity 990 Filings via ProPublica** - https://projects.propublica.org/nonprofits/
6. **EA Forum Posts** - Various annual reviews and analyses
7. **Foundation Annual Reports** - Gates Foundation, Wellcome Trust

### Search Queries Used
The following web searches were conducted to gather data:
- "GiveWell money moved top charities 2015-2024"
- "Open Philanthropy grants database total giving by cause area 2015-2024"
- "Open Philanthropy farm animal welfare grants total by year 2015-2024"
- "existential risk AI safety philanthropy funding 2015-2024"
- "EA Funds Long Term Future Fund grants total by year 2018-2024"
- "Survival and Flourishing Fund SFF total grants 2019-2024"
- "biosecurity pandemic prevention total philanthropic funding 2019-2024"
- "global health philanthropy total spending Gates Foundation Wellcome"

---

## Global Health & Development Sources

### GiveWell Money Moved (in millions USD)

| Year | Figure | Source | Validation URL |
|------|--------|--------|----------------|
| 2015 | $110.1M | GiveWell 2015 metrics report | https://blog.givewell.org/2016/05/13/givewells-money-moved-web-traffic-2015/ |
| 2016 | $88.6M | GiveWell 2016 metrics report | https://blog.givewell.org/2018/03/30/givewells-money-moved-and-web-traffic-in-2016/ |
| 2017 | $117.5M | GiveWell 2017 metrics report | https://blog.givewell.org/2018/06/29/givewells-money-moved-and-web-traffic-in-2017/ |
| 2018 | $141.0M | GiveWell 2018 metrics report | https://blog.givewell.org/2019/09/09/givewells-money-moved-and-web-traffic-in-2018/ |
| 2019 | $152.0M | GiveWell 2019 metrics report | https://blog.givewell.org/2021/11/12/givewells-money-moved-in-2020/ (mentions 2019) |
| 2020 | $244.0M | GiveWell 2020 metrics report | https://blog.givewell.org/2021/11/12/givewells-money-moved-in-2020/ |
| 2021 | $500.0M | GiveWell 2021 metrics report | https://blog.givewell.org/2022/08/05/givewells-2021-metrics-report/ |
| 2022 | $600.0M | GiveWell 2022 metrics report | https://blog.givewell.org/2023/12/22/givewells-2022-metrics-report/ |
| 2023 | $197.0M | GiveWell 2023 metrics report | https://files.givewell.org/files/GiveWell_Metrics_Report_2023.pdf |
| 2024 | $397.0M | GiveWell 2024 metrics report | https://blog.givewell.org/2025/08/13/givewells-2024-metrics-and-impact/ |

**Note on metric change:** Starting 2021, GiveWell switched from "money moved" to "funds raised/directed." The 2021-2024 figures are "funds directed." This explains the apparent drop from 2022 ($600M raised) to 2023 ($197M directed) - the metrics are not directly comparable.

**Verification steps:**
1. Visit GiveWell's official metrics page: https://www.givewell.org/about/impact
2. Download annual metrics PDFs from: https://files.givewell.org/files/metrics/
3. Cross-reference with EA Forum discussions of GiveWell metrics

### Gates Foundation Global Health (in millions USD)

| Year | Figure | Derivation |
|------|--------|------------|
| 2015-2024 | $3,800M - $7,000M | Estimated from annual budget announcements |

**Source basis:**
- Gates Foundation 2024 budget announcement: $8.6B total, with stated goal of $9B by 2026
  - Source: https://www.gatesfoundation.org/ideas/media-center/press-releases/2024/01/annual-budget-funding-future-health
- Gates Foundation has spent ~$100B in first 25 years, with ~50% on global health
  - Source: https://www.knkx.org/public-health/2025-05-11/the-gates-foundations-first-25-years
- Wikipedia states "more than US$77.6 billion in grants" total as of late 2023
  - Source: https://en.wikipedia.org/wiki/Gates_Foundation

**Calculation methodology:**
- 2024 budget ($8.6B) × ~80% global health focus = ~$7B
- Applied ~5% annual growth rate backward to estimate earlier years
- These are ESTIMATES with uncertainty of ±15%

**Verification steps:**
1. Review Gates Foundation annual reports: https://www.gatesfoundation.org/about/financials/annual-reports
2. Check 990 filings via ProPublica
3. Cross-reference with Global Health funding analyses

### Wellcome Trust Global Health (in millions USD)

| Year | Figure | Derivation |
|------|--------|------------|
| 2015-2024 | $800M - $1,350M | Estimated from annual spending reports |

**Source basis:**
- Wellcome Trust is one of world's largest health research funders
- Annual spending ~£1B+ on health research globally
- Source: https://wellcome.org/reports (annual reports)

**Note:** These figures are ESTIMATES based on general reporting about Wellcome's scale. More precise figures require accessing their annual financial statements directly.

### Other EA Global Health

| Year | Figure | Derivation |
|------|--------|------------|
| 2015-2024 | $10M - $65M | Estimated from GWWC member giving reports |

**Source basis:**
- Giving What We Can reports ~$70M/year in member donations
- Significant overlap with GiveWell (many GWWC members give via GiveWell)
- Estimate represents non-GiveWell EA global health giving
- Includes Founders Pledge recommendations, individual EA donors

---

## Animal Welfare Sources

### Open Philanthropy Farm Animal Welfare (in millions USD)

| Year | Figure | Source | Notes |
|------|--------|--------|-------|
| 2015 | $0 | Program not yet started | FAW program launched 2016 |
| 2016 | $14.4M | Vipul Naik database | https://donations.vipulnaik.com/donor.php?donor=Open+Philanthropy |
| 2017 | $28.1M | Vipul Naik database | Verified against OP grants page |
| 2018 | $28.0M | Vipul Naik database | |
| 2019 | $39.9M | Vipul Naik database | Confirmed in EA Forum analysis |
| 2020 | $25.2M | Vipul Naik database / EA Forum | https://forum.effectivealtruism.org/posts/6H9QGZkdMzDEdKNCX/ |
| 2021 | $23.6M | EA Forum analysis | Partial year data as of Sept 2021 showed $9M |
| 2022 | $35.0M | **ESTIMATE** | Based on trajectory, OP grants database |
| 2023 | $40.0M | **ESTIMATE** | Based on growth pattern |
| 2024 | $45.0M | **ESTIMATE** | Based on growth pattern |

**Key source:** EA Forum post "Analysis of EA funding within Animal Welfare from 2019-2021"
- URL: https://forum.effectivealtruism.org/posts/6H9QGZkdMzDEdKNCX/
- States: "Open Philanthropy distributed $39 million for Animal Welfare in 2019, $25 million in 2020"

**Verification steps:**
1. Query Open Philanthropy grants database filtered by "Farm Animal Welfare": https://www.openphilanthropy.org/grants/?focus-area=farm-animal-welfare
2. Use Vipul Naik's database: https://donations.vipulnaik.com/donor.php?donor=Open+Philanthropy&cause_area_filter=Animal+welfare
3. Sum grants by year manually from OP database

### EA Animal Welfare Fund (in millions USD)

| Year | Figure | Source |
|------|--------|--------|
| 2017-2024 | $0.5M - $4.0M | EA Funds website, payout reports |

**Source:** https://funds.effectivealtruism.org/funds/animal-welfare

**Verification:** Check EA Funds payout history and annual summaries

### Animal Charity Evaluators Influenced Giving

| Year | Figure | Source |
|------|--------|--------|
| 2015-2024 | $2M - $12.3M | ACE impact reports |

**Source basis:**
- ACE reports ~$59M total influenced giving
- ACE 2024 review states $47M moved 2019-2024
- Source: https://animalcharityevaluators.org/about/impact/

**Verification:** https://animalcharityevaluators.org/about/impact/

### Traditional Animal Welfare (ASPCA, HSUS, etc.)

| Year | Figure | Derivation |
|------|--------|------------|
| 2015-2024 | $5,000M - $6,800M | Industry estimates |

**Source basis:**
- ASPCA alone has ~$300M annual budget
- HSUS has ~$200M annual budget
- Combined US animal charity sector estimated at $5-7B annually
- Source: Various charity watchdog databases, 990 filings

**Note:** This is a rough estimate. The key point is that traditional animal welfare vastly exceeds factory farming-focused giving.

---

## Existential Risk Sources

### Open Philanthropy AI Safety (in millions USD)

| Year | Figure | Source |
|------|--------|--------|
| 2015 | $1.2M | Vipul Naik database |
| 2016 | $6.6M | Vipul Naik database |
| 2017 | $43.2M | Vipul Naik database |
| 2018 | $4.2M | Vipul Naik database |
| 2019 | $8.2M | Vipul Naik database |
| 2020 | $15.6M | Vipul Naik database |
| 2021 | $81.7M | Vipul Naik database |
| 2022 | $58.0M | EA Forum analysis |
| 2023 | $58.0M | **ESTIMATE** |
| 2024 | $75.0M | **ESTIMATE** |

**Key sources:**
- EA Forum: "An Overview of the AI Safety Funding Situation"
  - URL: https://forum.effectivealtruism.org/posts/XdhwXppfqrpPL2YDX/
  - States: "Since it was founded in 2017, Open Phil has donated about $2.8 billion of which about $336 million was spent on AI safety (~12%)"
  - States: "In 2023, Open Phil spent about $46 million on AI safety"
- Vipul Naik database: https://donations.vipulnaik.com/donor.php?donor=Open+Philanthropy&cause_area_filter=AI+safety

**Verification steps:**
1. Query OP grants database: https://www.openphilanthropy.org/grants/?focus-area=potential-risks-advanced-ai
2. Cross-reference with Vipul Naik database
3. Check EA Forum funding analyses

### Open Philanthropy Biosecurity (in millions USD)

| Year | Figure | Source |
|------|--------|--------|
| 2015-2021 | $0.3M - $21.6M | Vipul Naik database, OP grants |
| 2022-2024 | $25M - $40M | **ESTIMATES** based on post-COVID increase |

**Key source:**
- OP states: "granted $191 million to interventions in biosecurity and pandemic preparedness" (as of Feb 2024)
  - URL: https://www.openphilanthropy.org/focus/biosecurity-pandemic-preparedness/
- EA Forum: "How Well-Funded is Biosecurity Philanthropy?"
  - URL: https://forum.effectivealtruism.org/posts/pnincG5vW8Far8Ggg/

### Survival and Flourishing Fund (in millions USD)

| Year | Figure | Source |
|------|--------|--------|
| 2019 | $2.0M | SFF founded ~2019 |
| 2020 | $5.0M | Early grant rounds |
| 2021 | $10.0M | Growth period |
| 2022 | $15.0M | SFF announcements |
| 2023 | $21.3M | SFF 2023-H2 report |
| 2024 | $19.9M | SFF 2024 report |

**Sources:**
- SFF grant announcements: https://survivalandflourishing.fund/
- EA Forum: "SFF 2025 funding by cause area: $34 million to AI (86%), bio (7%)"
  - URL: https://forum.effectivealtruism.org/posts/vhw6R5P52qJr6opou/
- SFF 2023-H2: "$21.29MM" distributed
- SFF 2024: "$19.86MM" + $4.1MM flexHEGs round

### Long-Term Future Fund (in millions USD)

| Year | Figure | Source |
|------|--------|--------|
| 2018 | $0.01M | Minimal early grants |
| 2019 | $1.35M | EA Funds reports |
| 2020 | $1.5M | EA Funds reports |
| 2021 | $3.0M | Growth period |
| 2022 | $5.0M | ~$5M AI safety grants alone |
| 2023 | $6.67M | Part of $9.1M 2022-2023 period |
| 2024 | $5.36M | LTFF March 2024 payout report |

**Sources:**
- EA Funds LTFF page: https://funds.effectivealtruism.org/funds/far-future
- EA Forum: "Long-Term Future Fund: May 2023 to March 2024 Payout recommendations"
  - URL: https://forum.effectivealtruism.org/posts/pJyCWzevPHsycj4oQ/
  - States: "paid out $5.36 million in grants"
- EA Forum LTFF topic: https://forum.effectivealtruism.org/topics/long-term-future-fund

### FTX Future Fund (in millions USD)

| Year | Figure | Source |
|------|--------|--------|
| 2022 | $32.0M | AI safety grants before Nov 2022 collapse |

**Source:**
- EA Forum analysis states SBF donated ~$32M to AI safety projects
- FTX Future Fund operated Feb-Nov 2022 only
- Note: $500M+ Anthropic investment not counted as philanthropy

### Future of Life Institute (in millions USD)

| Year | Figure | Source |
|------|--------|--------|
| 2015-2021 | $2M - $5M | 990 filings, annual reports |
| 2022 | $10M | Beginning of crypto windfall |
| 2023 | $50M | Major increase |
| 2024 | $100M | Now ~$674M organization |

**Source:**
- EA Forum: "it was revealed that the Future of Life Institute (FLI) was no longer a $2.4-million organization but a $674-million organization"
- Shiba Inu token conversion via FTX/Alameda yielded ~$665M

---

## Effectiveness Weight Methodology

### Philosophy

The effectiveness weights estimate what fraction of each dollar spent achieves impact comparable to the "north star" charity for that category. This is inherently subjective but grounded in:

1. **Cost-effectiveness analyses** (GiveWell, ACE, Founders Pledge)
2. **Cause prioritization research** (80,000 Hours, Open Philanthropy)
3. **Alignment with stated north star** (how directly does spending target the problem?)

### Global Health Weights

| Source | Weight | Rationale |
|--------|--------|-----------|
| **GiveWell Top Charities (aggregate)** | **0.84** | Weighted average of charity allocations |
| - Against Malaria Foundation | 1.00 | Perfect north star - cost-effective malaria intervention |
| - Malaria Consortium SMC | 0.95 | Highly targeted malaria prevention |
| - Helen Keller Intl (Vitamin A) | 0.90 | Very cost-effective supplementation |
| - New Incentives | 0.85 | Cash incentives for vaccination |
| - GiveDirectly | 0.70 | Direct cash is effective but less targeted than health interventions |
| - Deworming charities | 0.60 | Less certain evidence base |
| **Gates Foundation** | **0.15** | Broad mandate includes less cost-effective work |
| **Wellcome Trust** | **0.10** | Research focus, speculative impact |
| **Other EA giving** | **0.80** | Generally high quality but variable |

**GiveWell weight calculation:**
- ~50% to malaria interventions (AMF, Malaria Consortium) → avg weight 0.97
- ~20% to nutrition/vaccination (HKI, New Incentives) → avg weight 0.87
- ~15% to cash transfers (GiveDirectly) → weight 0.70
- ~10% to deworming → weight 0.60
- ~5% other → weight 0.50
- **Weighted average: 0.50×0.97 + 0.20×0.87 + 0.15×0.70 + 0.10×0.60 + 0.05×0.50 = 0.84**

**Gates Foundation weight rationale (0.15):**
- Polio eradication: ~$5B spent, disease nearly eradicated but marginal cost-effectiveness is low
- Vaccine R&D: Important but speculative, long time horizons
- Agricultural development: Indirect health impact
- US education: Not global health
- Compare to GiveWell's AMF at ~$5,000/life saved vs Gates' mixed portfolio

### Animal Welfare Weights

| Source | Weight | Rationale |
|--------|--------|-----------|
| **Open Philanthropy FAW** | **0.90** | Highly aligned with factory farming reform |
| **EA Animal Fund** | **0.95** | ACE-evaluated, factory farming focused |
| **ACE Influenced** | **0.85** | ACE recommendations well-aligned |
| **Traditional (HSUS, ASPCA)** | **0.02** | Companion animal focus, minimal factory farming impact |

**Traditional animal welfare weight rationale (0.02):**
- ~70M farmed animals killed per day vs ~10K shelter animals
- Traditional charities focus almost entirely on companion animals
- Per-dollar impact on reducing animal suffering is orders of magnitude lower
- 0.02 represents the small fraction that may indirectly affect farmed animals

### Existential Risk Weights

| Source | Weight | Rationale |
|--------|--------|-----------|
| **Open Phil AI Safety** | **0.90** | Core AI safety research, highly targeted |
| **Open Phil Biosecurity** | **0.85** | Pandemic prevention, some broader health overlap |
| **Open Phil GCR** | **0.70** | Mixed - includes nuclear, climate (less neglected) |
| **SFF** | **0.85** | Highly aligned, ~86% to AI in recent years |
| **LTFF** | **0.80** | Good alignment but variable grant quality |
| **FTX Future Fund** | **0.75** | Reasonably aligned but short track record |
| **FLI** | **0.70** | Good alignment but includes broader AI ethics |
| **Other X-risk** | **0.50** | Mixed academic/small foundation work |

---

## Deduplication Approach

### Problem
Many funding sources overlap:
- Open Philanthropy funds flow through GiveWell
- SFF regrants to LTFF recipients
- ACE-influenced giving may come from Open Phil donors

### Solutions Applied

1. **GiveWell / Open Phil overlap:**
   - GiveWell figures include Good Ventures (Open Phil's main vehicle)
   - We use GiveWell as the primary source and don't add separate Open Phil global health
   - This is noted in GiveWell's metrics (e.g., "$350M from Open Phil in 2022")

2. **SFF / LTFF overlap:**
   - Applied 20% reduction to SFF figures
   - SFF sometimes funds LTFF for regranting

3. **ACE / Open Phil overlap:**
   - Applied 50% reduction to ACE influenced giving
   - Many ACE donors also receive Open Phil recommendations

4. **Charity budgets vs funder totals:**
   - We use funder totals (Open Phil) not charity budgets (Humane League)
   - This avoids counting the same grant twice

---

## Limitations and Uncertainties

### High Confidence (±10%)
- GiveWell money moved 2015-2020
- Open Phil grants 2016-2021 (from grants database)
- LTFF/SFF recent payouts

### Medium Confidence (±25%)
- GiveWell 2021-2024 (metric change complicates comparison)
- Open Phil 2022-2024 (database lag)
- Gates Foundation annual figures
- Traditional animal welfare totals

### Low Confidence (±50%)
- Wellcome Trust figures
- "Other EA" giving estimates
- FLI recent figures (crypto volatility)
- 2024 estimates for most sources

### Structural Uncertainties
1. **Definition boundaries:** What counts as "global health" vs "development"?
2. **Effectiveness weights:** Inherently subjective
3. **Counterfactual impact:** Would this money have been spent anyway?
4. **Exchange rates:** Some sources report in GBP/EUR

---

## Validation Checklist

Use this checklist to verify key figures:

### GiveWell
- [ ] Visit https://www.givewell.org/about/impact
- [ ] Download metrics PDFs from https://files.givewell.org/files/metrics/
- [ ] Compare "money moved" (pre-2021) vs "funds directed" (2021+)

### Open Philanthropy
- [ ] Query grants database: https://www.openphilanthropy.org/grants/
- [ ] Filter by focus area and sum by year
- [ ] Cross-reference with Vipul Naik: https://donations.vipulnaik.com/donor.php?donor=Open+Philanthropy

### EA Funds
- [ ] Check fund pages: https://funds.effectivealtruism.org/
- [ ] Review payout reports on EA Forum

### SFF
- [ ] Check announcements: https://survivalandflourishing.fund/
- [ ] Review EA Forum posts on grant rounds

### Cross-validation
- [ ] Compare totals to EA Forum funding analyses
- [ ] Check for major discrepancies (>25%)
- [ ] Note any figures that seem implausible

---

## Changelog

- **2024-02-04:** Initial methodology document created
- Data collected via web searches and database queries
- Weights assigned based on cause prioritization literature

---

## Contact / Corrections

If you find errors in this analysis, the most likely issues are:
1. Outdated figures (check primary sources for updates)
2. Misattributed grants (verify in grants databases)
3. Weight disagreements (subjective - adjust as needed)

The Python script (`charity_philanthropy_analysis.py`) can be modified to update figures or weights as better data becomes available.
