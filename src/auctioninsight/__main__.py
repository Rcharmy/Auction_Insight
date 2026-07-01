#!/usr/bin/env python3
"""
AuctionInsight Engine — CLI entry point.

Run simulations, generate reports, and export data from the command line.

Usage:
    auctioninsight --simulations 5000 --output-dir ./reports
    auctioninsight --list-scenarios
    python -m auctioninsight --simulations 10000
"""

import argparse
import sys

from auctioninsight.core import run_simulations, compute_kpis
from auctioninsight.scenarios import SCENARIOS, get_scenario_names
from auctioninsight.reporting import generate_markdown_report, export_json, print_summary


def main():
    parser = argparse.ArgumentParser(
        prog="auctioninsight",
        description="Monte Carlo auction simulation and KPI analytics engine",
        epilog="Example: auctioninsight --simulations 5000 --output-dir ./reports",
    )
    parser.add_argument(
        "--simulations",
        type=int,
        default=5000,
        help="Number of simulation runs per scenario (default: 5000)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=".",
        help="Directory to write output files (default: current directory)",
    )
    parser.add_argument(
        "--list-scenarios",
        action="store_true",
        help="Print available scenario names and exit",
    )
    parser.add_argument(
        "--scenario",
        type=str,
        default=None,
        help="Run only a specific scenario by name (default: all scenarios)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)",
    )

    args = parser.parse_args()

    if args.list_scenarios:
        print("Available scenarios:")
        for name in get_scenario_names():
            print(f"  - {name}")
        sys.exit(0)

    # Filter scenarios if requested
    scenarios = SCENARIOS
    if args.scenario:
        scenarios = [s for s in scenarios if s.name == args.scenario]
        if not scenarios:
            print(f"Error: unknown scenario '{args.scenario}'")
            print(f"Use --list-scenarios to see available options.")
            sys.exit(1)

    print(f"Running {args.simulations} simulations per scenario...")
    print(f"Scenarios: {len(scenarios)}")
    print(f"Random seed: {args.seed}")
    print()

    results = run_simulations(scenarios, args.simulations)
    analysis = compute_kpis(results)

    # Print summary table
    print_summary(analysis)

    # Write reports
    md = generate_markdown_report(analysis, args.simulations)
    md_path = f"{args.output_dir}/simulation_report.md"
    with open(md_path, "w") as f:
        f.write(md)
    print(f"\nReport: {md_path}")

    json_path = export_json(analysis, f"{args.output_dir}/simulation_report.json")
    print(f"Data:   {json_path}")


if __name__ == "__main__":
    main()