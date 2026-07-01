# AuctionInsight Engine

**AI-driven Monte Carlo simulation and analytics platform for the Amazon Advertising ecosystem.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PySpark](https://img.shields.io/badge/PySpark-3.5-orange.svg)](https://spark.apache.org/)

---

## Overview

AuctionInsight Engine is an **AI-driven AdTech simulation and intelligence platform** purpose-built for the Amazon Advertising ecosystem. It bridges the gap between engineering roadmaps and revenue performance by enabling data-driven analysis of auction dynamics through Monte Carlo simulation, statistical modeling, and scalable KPI computation.

### What it does

- **Simulates Amazon ad auctions** using Monte Carlo methods (1st-price and 2nd-price models with identity resolution, floor pricing, and bid distributions)
- **Computes Amazon-specific KPIs**: Fill Rate, Auction Efficiency, Identity Recognition Rate (IRR), AMC Impact, Bid Spread, Bid Depth
- **Models real-world Amazon variables**: DSP bid distributions (log-normal, exponential, uniform), identity resolution rates (30-85%), floor prices ($0.50-$1.00), bidder depth (5-10)
- **Generates Amazon Intelligence reports**: Weekly intelligence decks, deep-dive auction analysis, and machine-readable JSON data exports for AMC dashboard integration
- **Scales with PySpark**: Production-grade KPI computation pipeline for processing billions of auction events at scale

### Key findings (from 40,000 simulations across 8 scenarios)

| Insight | Result |
|---------|--------|
| 1st-price vs 2nd-price | 1st-price generates ~73% more revenue per request |
| Bidder depth impact | 5 → 10 bidders pushes fill rate from 96.6% → 99.96% |
| Identity resolution | 30% → 85% resolution yields 32% fill rate improvement |
| Floor price trade-off | Higher floors improve efficiency but reduce fill rate |

---

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/auctioninsight/auctioninsight-engine.git
cd auctioninsight-engine

# Install in development mode
pip install -e .
```

### Run a simulation

```bash
# Run 5,000 simulations per scenario (8 scenarios = 40,000 total)
auctioninsight --simulations 5000 --output-dir ./reports
```

### List available scenarios

```bash
auctioninsight --list-scenarios
```

### Run a single scenario

```bash
auctioninsight --simulations 10000 --scenario Baseline_2ndPrice_5Bidders
```

### Python API

```python
from auctioninsight.core import run_simulations, compute_kpis
from auctioninsight.scenarios import SCENARIOS

# Run simulations
results = run_simulations(SCENARIOS, num_runs=5000)
analysis = compute_kpis(results)

# View results
for name, kpis in analysis.items():
    print(f"{name}: Fill Rate = {kpis['fill_rate_pct']}%")
```

---

## Project Structure

```
auctioninsight-engine/
├── src/
│   └── auctioninsight/
│       ├── __init__.py       # Package metadata
│       ├── __main__.py       # CLI entry point
│       ├── core.py           # Simulation engine (bid gen, auction resolution, KPI computation)
│       ├── scenarios.py      # Pre-defined auction scenarios (8 configurations)
│       └── reporting.py      # Markdown/JSON report generation
├── sql/
│   ├── schemas.sql           # Database schemas for auction event logging (Amazon DSP, AMC, AMS)
│   └── queries.sql           # KPI computation SQL queries (Fill Rate, IRR, Efficiency)
├── pyspark/
│   └── kpi_computation.py    # PySpark pipeline for at-scale KPI computation
├── data/
│   ├── simulation_report.json   # Sample simulation output (8 scenarios × 13 metrics)
│   └── simulation_report.md     # Formatted simulation report with key findings
├── decks/
│   └── weekly_intelligence_w26.md  # Amazon Intelligence Subscription — Volume 1
├── docs/
│   └── framework.md             # Full auction analytics framework documentation
├── examples/
│   └── run_simulation.py        # Minimal usage example
├── tests/
│   └── test_core.py             # 10 unit tests
├── .github/workflows/
│   └── simulation.yml           # CI/CD pipeline (weekly automated simulations)
├── pyproject.toml               # Python project configuration
├── LICENSE                      # MIT license
└── README.md                    # This file
```

---

## Simulation Methodology

### Pipeline

```
Input Parameters → Bid Generation → Identity Filtering → Floor Filtering → Auction Resolution → KPI Aggregation
     ↓                   ↓                   ↓                   ↓                   ↓                ↓
  Config            Distribution         Stochastic           Hard floor          1st/2nd-price    Statistics
```

### Auction Models

| Type | Winner Pays | Characteristics |
|------|-------------|-----------------|
| **Second-Price (Vickrey)** | Second-highest bid | Legacy OpenRTB standard; winner's surplus grows with more bidders |
| **First-Price** | Their own bid | Modern programmatic standard; captures full bidder valuation |

### Bid Distributions

| Distribution | Parameters | Use Case |
|-------------|-----------|----------|
| **Log-normal** | μ=0, σ=0.8 | Standard ad auctions (right-skewed) |
| **Exponential** | scale=1.0 | Remnant / low-value inventory |
| **Uniform** | [low, high] | Controlled experiments |

### Configurable Parameters

| Parameter | Range | Description |
|-----------|-------|-------------|
| Num Bidders | 5 – 10 | Eligible bidders per auction |
| Floor Price | $0.50 – $1.00 | Minimum accepted bid |
| Identity Resolution | 30% – 85% | % of bidders with resolved identity |
| Auction Type | 1st / 2nd-price | Pricing mechanism |
| Bid Distribution | Log-normal / Exponential / Uniform | Distribution of bid values |

---

## Core KPIs

| KPI | Definition | Benchmark (Excellent) |
|-----|-----------|:---------------------:|
| **Fill Rate** | % of ad requests resulting in successful placement | > 85% |
| **Identity Recognition Rate** | % of bid requests with resolved user identity | > 70% |
| **Auction Efficiency** | Revenue captured / theoretical maximum | > 95% |
| **Bid Depth** | Average number of competitive bids per auction | 4+ |
| **Revenue per Request** | Mean win price across all requests | — |

See [`sql/queries.sql`](sql/queries.sql) for production-grade SQL implementations of each KPI.

---

## Data Pipeline Integration

This engine is designed to work alongside a production data pipeline. See [`sql/schemas.sql`](sql/schemas.sql) for the recommended database schema covering:

- `auction_events` — Canonical auction lifecycle table
- `bid_requests` — Per-DSP bid tracking
- `identity_resolution` — Identity resolution pipeline tracking

The full data logging specification is documented in the companion
[Data Logging Requirements](https://github.com/auctioninsight/auctioninsight-engine/docs/logging.md) guide.

---

## PySpark KPI Pipeline

For production-scale processing of billions of auction events, the engine includes a **PySpark KPI computation pipeline** at [`pyspark/kpi_computation.py`](pyspark/kpi_computation.py).

### Pipeline stages

| Stage | Function | Description |
|-------|----------|-------------|
| Fill Rate | `compute_fill_rate()` | % of ad requests resulting in successful placements |
| Identity Recognition | `compute_irr()` | % of bid requests with resolved Amazon Ads ID |
| Auction Efficiency | `compute_auction_efficiency()` | Revenue captured vs theoretical maximum |
| Revenue per Request | `compute_revenue_per_request()` | Mean win price across all requests |
| Bid Depth Distribution | `compute_bid_depth_distribution()` | Distribution of competitive bid counts |
| Identity Success Rate | `compute_identity_success_rate()` | Resolution pipeline effectiveness by provider |

### Running the pipeline

```bash
spark-submit pyspark/kpi_computation.py \
    --input-path s3://data-lake/auction_events/ \
    --output-path s3://analytics/kpi_summary/
```

---

## CI/CD Integration

The simulation framework can be integrated into your CI/CD pipeline:

```yaml
# .github/workflows/simulation.yml
name: Auction Simulation
on:
  schedule:
    - cron: '0 6 * * 1'  # Weekly Monday morning
jobs:
  simulate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run auction simulations
        run: auctioninsight --simulations 5000 --output-dir ./reports
      - name: Archive results
        uses: actions/upload-artifact@v3
        with:
          name: simulation-report
          path: reports/*
```

---

## Development

### Running tests

```bash
python -m pytest tests/ -v
# or
python -m unittest tests/test_core.py -v
```

### Code style

```bash
pip install black
black src/ tests/
```

---

## License

[MIT](LICENSE) © 2026 AuctionInsight

---

## About AuctionInsight

AuctionInsight provides high-level analytics and strategic intelligence for the Amazon Advertising ecosystem. We bridge the gap between engineering roadmaps and revenue performance for brands and agencies navigating Amazon's complex auction dynamics — including Amazon DSP, Sponsored Ads, Amazon Marketing Cloud (AMC), and Amazon Marketing Stream (AMS).

[auctioninsight.io](https://auctioninsight.io)