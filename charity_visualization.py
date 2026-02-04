#!/usr/bin/env python3
"""
Visualization script for charity philanthropy analysis.
Generates charts showing spending trends over time.
"""

import json
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

# Load the analysis results
with open("charity_analysis_results.json", "r") as f:
    data = json.load(f)

results = data["data"]
years = list(range(2015, 2025))

# Set up the style
plt.style.use('seaborn-v0_8-whitegrid')
colors = {
    'global_health': '#2ecc71',
    'animal_welfare': '#e74c3c',
    'existential_risk': '#3498db',
    'global_health_weighted': '#27ae60',
    'animal_welfare_weighted': '#c0392b',
    'existential_risk_weighted': '#2980b9',
}

# -----------------------------------------------------------------------------
# Figure 1: Total Spending by Category
# -----------------------------------------------------------------------------
fig1, ax1 = plt.subplots(figsize=(12, 7))

gh_total = [results['global_health']['total'][str(y)] for y in years]
aw_total = [results['animal_welfare']['total'][str(y)] for y in years]
xr_total = [results['existential_risk']['total'][str(y)] for y in years]

ax1.plot(years, gh_total, 'o-', linewidth=2, markersize=8,
         color=colors['global_health'], label='Global Health & Development')
ax1.plot(years, aw_total, 's-', linewidth=2, markersize=8,
         color=colors['animal_welfare'], label='Animal Welfare')
ax1.plot(years, xr_total, '^-', linewidth=2, markersize=8,
         color=colors['existential_risk'], label='Existential Risk')

ax1.set_xlabel('Year', fontsize=12)
ax1.set_ylabel('Total Spending (Millions USD)', fontsize=12)
ax1.set_title('Total Philanthropic Spending by Category (2015-2024)', fontsize=14, fontweight='bold')
ax1.legend(loc='upper left', fontsize=10)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'${x:,.0f}M'))
ax1.set_xticks(years)

plt.tight_layout()
plt.savefig('chart1_total_spending.png', dpi=150, bbox_inches='tight')
plt.close()

# -----------------------------------------------------------------------------
# Figure 2: Effectiveness-Weighted Spending by Category
# -----------------------------------------------------------------------------
fig2, ax2 = plt.subplots(figsize=(12, 7))

gh_weighted = [results['global_health']['weighted'][str(y)] for y in years]
aw_weighted = [results['animal_welfare']['weighted'][str(y)] for y in years]
xr_weighted = [results['existential_risk']['weighted'][str(y)] for y in years]

ax2.plot(years, gh_weighted, 'o-', linewidth=2, markersize=8,
         color=colors['global_health'], label='Global Health & Development')
ax2.plot(years, aw_weighted, 's-', linewidth=2, markersize=8,
         color=colors['animal_welfare'], label='Animal Welfare')
ax2.plot(years, xr_weighted, '^-', linewidth=2, markersize=8,
         color=colors['existential_risk'], label='Existential Risk')

ax2.set_xlabel('Year', fontsize=12)
ax2.set_ylabel('Weighted Spending (Millions USD)', fontsize=12)
ax2.set_title('Effectiveness-Weighted Philanthropic Spending by Category (2015-2024)', fontsize=14, fontweight='bold')
ax2.legend(loc='upper left', fontsize=10)
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'${x:,.0f}M'))
ax2.set_xticks(years)

plt.tight_layout()
plt.savefig('chart2_weighted_spending.png', dpi=150, bbox_inches='tight')
plt.close()

# -----------------------------------------------------------------------------
# Figure 3: Effectiveness Percentage by Category
# -----------------------------------------------------------------------------
fig3, ax3 = plt.subplots(figsize=(12, 7))

gh_eff = [gh_weighted[i] / gh_total[i] * 100 if gh_total[i] > 0 else 0 for i in range(len(years))]
aw_eff = [aw_weighted[i] / aw_total[i] * 100 if aw_total[i] > 0 else 0 for i in range(len(years))]
xr_eff = [xr_weighted[i] / xr_total[i] * 100 if xr_total[i] > 0 else 0 for i in range(len(years))]

ax3.plot(years, gh_eff, 'o-', linewidth=2, markersize=8,
         color=colors['global_health'], label='Global Health & Development')
ax3.plot(years, aw_eff, 's-', linewidth=2, markersize=8,
         color=colors['animal_welfare'], label='Animal Welfare')
ax3.plot(years, xr_eff, '^-', linewidth=2, markersize=8,
         color=colors['existential_risk'], label='Existential Risk')

ax3.set_xlabel('Year', fontsize=12)
ax3.set_ylabel('Effectiveness Percentage (%)', fontsize=12)
ax3.set_title('Effectiveness Ratio by Category (Weighted / Total Spend)', fontsize=14, fontweight='bold')
ax3.legend(loc='center right', fontsize=10)
ax3.set_ylim(0, 100)
ax3.set_xticks(years)
ax3.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'{x:.0f}%'))

plt.tight_layout()
plt.savefig('chart3_effectiveness_ratio.png', dpi=150, bbox_inches='tight')
plt.close()

# -----------------------------------------------------------------------------
# Figure 4: Effective Philanthropy Only (excluding traditional)
# -----------------------------------------------------------------------------
fig4, ax4 = plt.subplots(figsize=(12, 7))

# Recalculate effective-only figures
givewell_mm = {2015: 110.1, 2016: 88.6, 2017: 117.5, 2018: 141.0, 2019: 152.0,
               2020: 244.0, 2021: 500.0, 2022: 600.0, 2023: 197.0, 2024: 397.0}
other_ea_gh = {2015: 10, 2016: 15, 2017: 20, 2018: 25, 2019: 30,
               2020: 40, 2021: 50, 2022: 55, 2023: 60, 2024: 65}

open_phil_aw = {2015: 0, 2016: 14.4, 2017: 28.1, 2018: 28.0, 2019: 39.9,
                2020: 25.2, 2021: 23.6, 2022: 35.0, 2023: 40.0, 2024: 45.0}
ea_animal = {2015: 0, 2016: 0, 2017: 0.5, 2018: 1.0, 2019: 1.5,
             2020: 2.0, 2021: 3.0, 2022: 4.0, 2023: 3.5, 2024: 4.0}
ace = {2015: 2.0, 2016: 3.0, 2017: 4.0, 2018: 5.0, 2019: 6.5,
       2020: 8.0, 2021: 10.0, 2022: 11.0, 2023: 12.0, 2024: 12.3}

eff_gh = [givewell_mm[y] + other_ea_gh[y] for y in years]
eff_aw = [open_phil_aw[y] + ea_animal[y] + ace[y] * 0.5 for y in years]
eff_xr = xr_total  # Already effective

ax4.stackplot(years, eff_gh, eff_aw, eff_xr,
              labels=['Global Health (EA-aligned)', 'Animal Welfare (Effective)', 'Existential Risk'],
              colors=[colors['global_health'], colors['animal_welfare'], colors['existential_risk']],
              alpha=0.8)

ax4.set_xlabel('Year', fontsize=12)
ax4.set_ylabel('Spending (Millions USD)', fontsize=12)
ax4.set_title('Effective Philanthropy Only (Excluding Traditional Sources)', fontsize=14, fontweight='bold')
ax4.legend(loc='upper left', fontsize=10)
ax4.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'${x:,.0f}M'))
ax4.set_xticks(years)

plt.tight_layout()
plt.savefig('chart4_effective_only_stacked.png', dpi=150, bbox_inches='tight')
plt.close()

# -----------------------------------------------------------------------------
# Figure 5: Existential Risk Breakdown
# -----------------------------------------------------------------------------
fig5, ax5 = plt.subplots(figsize=(12, 7))

op_ai = {2015: 1.2, 2016: 6.6, 2017: 43.2, 2018: 4.2, 2019: 8.2,
         2020: 15.6, 2021: 81.7, 2022: 58.0, 2023: 58.0, 2024: 75.0}
op_bio = {2015: 0.3, 2016: 5.3, 2017: 28.8, 2018: 9.9, 2019: 21.6,
          2020: 15.0, 2021: 9.3, 2022: 25.0, 2023: 35.0, 2024: 40.0}
sff = {2015: 0, 2016: 0, 2017: 0, 2018: 0, 2019: 2.0,
       2020: 5.0, 2021: 10.0, 2022: 15.0, 2023: 21.3, 2024: 19.9}
fli = {2015: 5.0, 2016: 3.0, 2017: 2.0, 2018: 2.0, 2019: 3.0,
       2020: 4.0, 2021: 5.0, 2022: 10.0, 2023: 50.0, 2024: 100.0}
other_xr = {2015: 2.0, 2016: 3.6, 2017: 8.1, 2018: 17.7, 2019: 7.6,
            2020: 9.5, 2021: 13.0, 2022: 49.0, 2023: 21.4, 2024: 24.4}

ai_data = [op_ai[y] for y in years]
bio_data = [op_bio[y] for y in years]
sff_data = [sff[y] * 0.8 for y in years]  # 80% to avoid overlap
fli_data = [fli[y] for y in years]
other_data = [other_xr[y] for y in years]

ax5.stackplot(years, ai_data, bio_data, sff_data, fli_data, other_data,
              labels=['Open Phil AI Safety', 'Open Phil Biosecurity', 'Survival & Flourishing',
                      'Future of Life Institute', 'Other (LTFF, FTX, GCR)'],
              colors=['#3498db', '#9b59b6', '#1abc9c', '#e67e22', '#95a5a6'],
              alpha=0.8)

ax5.set_xlabel('Year', fontsize=12)
ax5.set_ylabel('Spending (Millions USD)', fontsize=12)
ax5.set_title('Existential Risk Funding Breakdown by Source (2015-2024)', fontsize=14, fontweight='bold')
ax5.legend(loc='upper left', fontsize=10)
ax5.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'${x:,.0f}M'))
ax5.set_xticks(years)

plt.tight_layout()
plt.savefig('chart5_xrisk_breakdown.png', dpi=150, bbox_inches='tight')
plt.close()

# -----------------------------------------------------------------------------
# Figure 6: Summary Bar Chart - Decade Totals
# -----------------------------------------------------------------------------
fig6, (ax6a, ax6b) = plt.subplots(1, 2, figsize=(14, 6))

categories = ['Global Health', 'Animal Welfare', 'Existential Risk']
totals = [sum(gh_total), sum(aw_total), sum(xr_total)]
weighted = [sum(gh_weighted), sum(aw_weighted), sum(xr_weighted)]

x = np.arange(len(categories))
width = 0.35

bars1 = ax6a.bar(x - width/2, totals, width, label='Total Spend', color='#bdc3c7')
bars2 = ax6a.bar(x + width/2, weighted, width, label='Weighted Spend', color='#2c3e50')

ax6a.set_xlabel('Category', fontsize=12)
ax6a.set_ylabel('10-Year Total (Millions USD)', fontsize=12)
ax6a.set_title('Decade Total: All Philanthropy', fontsize=14, fontweight='bold')
ax6a.set_xticks(x)
ax6a.set_xticklabels(categories)
ax6a.legend()
ax6a.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'${x/1000:,.0f}B'))

# Effective only comparison
eff_totals = [sum(eff_gh), sum(eff_aw), sum([float(xr_total[i]) for i in range(len(years))])]
eff_weighted = [sum(eff_gh) * 0.84, sum(eff_aw) * 0.90, sum(xr_weighted)]

bars3 = ax6b.bar(x - width/2, eff_totals, width, label='Total Spend',
                  color=[colors['global_health'], colors['animal_welfare'], colors['existential_risk']])
bars4 = ax6b.bar(x + width/2, eff_weighted, width, label='Weighted Spend', alpha=0.7,
                  color=[colors['global_health_weighted'], colors['animal_welfare_weighted'], colors['existential_risk_weighted']])

ax6b.set_xlabel('Category', fontsize=12)
ax6b.set_ylabel('10-Year Total (Millions USD)', fontsize=12)
ax6b.set_title('Decade Total: Effective Philanthropy Only', fontsize=14, fontweight='bold')
ax6b.set_xticks(x)
ax6b.set_xticklabels(categories)
ax6b.legend()
ax6b.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'${x:,.0f}M'))

plt.tight_layout()
plt.savefig('chart6_decade_totals.png', dpi=150, bbox_inches='tight')
plt.close()

print("Charts generated successfully:")
print("  - chart1_total_spending.png")
print("  - chart2_weighted_spending.png")
print("  - chart3_effectiveness_ratio.png")
print("  - chart4_effective_only_stacked.png")
print("  - chart5_xrisk_breakdown.png")
print("  - chart6_decade_totals.png")
