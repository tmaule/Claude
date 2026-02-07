#!/usr/bin/env python3
"""
Generate a stacked bar chart of weighted philanthropic spending by category.
"""

import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Load the analysis results
with open("charity_analysis_results.json", "r") as f:
    data = json.load(f)

results = data["data"]
years = list(range(2015, 2025))

# Extract weighted spending data
gh_weighted = [results['global_health']['weighted'][str(y)] for y in years]
aw_weighted = [results['animal_welfare']['weighted'][str(y)] for y in years]
xr_weighted = [results['existential_risk']['weighted'][str(y)] for y in years]

# Create DataFrame for seaborn
df = pd.DataFrame({
    'Year': years,
    'Global Health & Development': gh_weighted,
    'Animal Welfare': aw_weighted,
    'Existential Risk': xr_weighted
})

# Set up seaborn style
sns.set_theme(style="whitegrid", palette="deep")
plt.figure(figsize=(14, 8))

# Create stacked bar chart
colors = ['#2ecc71', '#e74c3c', '#3498db']  # Green, Red, Blue

# Plot stacked bars
bottom_gh = np.zeros(len(years))
bottom_aw = np.array(gh_weighted)
bottom_xr = np.array(gh_weighted) + np.array(aw_weighted)

bars1 = plt.bar(years, gh_weighted, label='Global Health & Development',
                color=colors[0], edgecolor='white', linewidth=0.7)
bars2 = plt.bar(years, aw_weighted, bottom=bottom_aw, label='Animal Welfare',
                color=colors[1], edgecolor='white', linewidth=0.7)
bars3 = plt.bar(years, xr_weighted, bottom=bottom_xr, label='Existential Risk',
                color=colors[2], edgecolor='white', linewidth=0.7)

# Customize the chart
plt.xlabel('Year', fontsize=13, fontweight='bold')
plt.ylabel('Effectiveness-Weighted Spending (Millions USD)', fontsize=13, fontweight='bold')
plt.title('Effectiveness-Weighted Philanthropic Spending by Category (2015-2024)',
          fontsize=16, fontweight='bold', pad=20)

# Format y-axis
plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}M'))

# Set x-ticks
plt.xticks(years, fontsize=11)
plt.yticks(fontsize=11)

# Add legend
plt.legend(loc='upper left', fontsize=11, framealpha=0.95)

# Add total labels on top of each bar
totals = [gh_weighted[i] + aw_weighted[i] + xr_weighted[i] for i in range(len(years))]
for i, (year, total) in enumerate(zip(years, totals)):
    plt.text(year, total + 30, f'${total:,.0f}M', ha='center', va='bottom',
             fontsize=9, fontweight='bold', color='#2c3e50')

# Adjust layout
plt.tight_layout()

# Save the chart
plt.savefig('chart_weighted_spend_stacked.png', dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.close()

print("Chart saved as: chart_weighted_spend_stacked.png")
