#!/usr/bin/env python3
"""
Example: Run a full simulation and print results.
"""

from auctioninsight.core import run_simulations, compute_kpis
from auctioninsight.scenarios import SCENARIOS
from auctioninsight.reporting import generate_markdown_report, print_summary

# Run 5,000 simulations per scenario
results = run_simulations(SCENARIOS, num_runs=5000)
analysis = compute_kpis(results)

# Print a summary table
print_summary(analysis)

# Generate a Markdown report
report = generate_markdown_report(analysis, num_simulations=5000)
print("\n--- Markdown Report ---")
print(report[:500] + "\n...")