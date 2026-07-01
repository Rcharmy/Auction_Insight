"""
Core simulation engine — bid generation, auction resolution, and KPI computation.

This module provides the fundamental building blocks for Monte Carlo simulation
of ad auctions, supporting:
- Log-normal, uniform, and exponential bid distributions
- 1st-price and 2nd-price auction mechanics
- Identity resolution filtering
- Floor price enforcement
- Comprehensive KPI computation (fill rate, efficiency, bid spread, depth)
"""

import math
import random
import statistics
from dataclasses import dataclass, field
from typing import List, Tuple, Dict

# Seed for reproducibility across runs
random.seed(42)


# ─── Data Models ───────────────────────────────────────────────────────────


@dataclass
class AuctionConfig:
    """Configuration for an auction simulation scenario.

    Attributes:
        name: Human-readable scenario identifier.
        auction_type: Auction pricing model — ``"first_price"`` or ``"second_price"``.
        num_bidders: Number of eligible bidders participating in each auction.
        floor_price: Minimum acceptable bid. Bids below this threshold are rejected.
        bid_distribution: Statistical distribution of bid values — one of
            ``"log_normal"``, ``"uniform"``, or ``"exponential"``.
        bid_params: Distribution parameters as a tuple. For log-normal: ``(mu, sigma)``;
            for uniform: ``(low, high)``; for exponential: ``(scale,)``.
        identity_resolution_rate: Fraction of bidders (0.0 to 1.0) whose identity
            is successfully resolved before the auction.
    """

    name: str
    auction_type: str
    num_bidders: int
    floor_price: float
    bid_distribution: str
    bid_params: Tuple[float, ...]
    identity_resolution_rate: float


@dataclass
class AuctionResult:
    """Result of a single auction simulation.

    Attributes:
        config_name: Name of the scenario configuration used.
        bids: All generated bid values (before filtering).
        highest_bid: Highest bid value (0 if no bids above floor).
        second_highest_bid: Second-highest bid value (0 if fewer than 2 bids).
        win_price: Price paid by the winner (depends on auction type).
        floor_price: Floor price applied to this auction.
        filled: Whether the auction resulted in a successful placement.
        auction_efficiency: Revenue / theoretical maximum (0–100%).
        bid_spread: Standard deviation of bid values (measure of dispersion).
        bid_depth: Number of bids that met or exceeded the floor price.
    """

    config_name: str
    bids: List[float]
    highest_bid: float
    second_highest_bid: float
    win_price: float
    floor_price: float
    filled: bool
    auction_efficiency: float
    bid_spread: float
    bid_depth: int


# ─── Bid Distribution Samplers ─────────────────────────────────────────────


def sample_log_normal(mu: float, sigma: float) -> float:
    """Sample from a log-normal distribution using the Box-Muller transform.

    Args:
        mu: Mean of the underlying normal distribution.
        sigma: Standard deviation of the underlying normal distribution.

    Returns:
        A positive float sampled from log-normal(mu, sigma).
    """
    u1 = random.random()
    u2 = random.random()
    z = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
    return math.exp(mu + sigma * z)


def sample_exponential(scale: float) -> float:
    """Sample from an exponential distribution via inverse transform.

    Args:
        scale: The scale parameter (mean = scale).

    Returns:
        A positive float sampled from exponential(1/scale).
    """
    return -scale * math.log(1.0 - random.random())


def generate_bids(
    num_bidders: int, dist: str, params: Tuple[float, ...]
) -> List[float]:
    """Generate bid values from the specified distribution.

    Args:
        num_bidders: Number of bids to generate.
        dist: Distribution name (``"log_normal"``, ``"uniform"``, ``"exponential"``).
        params: Distribution-specific parameters (see :class:`AuctionConfig`).

    Returns:
        A list of ``num_bidders`` bid values.

    Raises:
        ValueError: If ``dist`` is not a recognised distribution name.
    """
    bids = []
    for _ in range(num_bidders):
        if dist == "log_normal":
            bids.append(sample_log_normal(params[0], params[1]))
        elif dist == "uniform":
            bids.append(random.uniform(params[0], params[1]))
        elif dist == "exponential":
            bids.append(sample_exponential(params[0]))
        else:
            raise ValueError(f"Unknown distribution: '{dist}'. "
                             f"Expected 'log_normal', 'uniform', or 'exponential'.")
    return bids


# ─── Auction Resolution ────────────────────────────────────────────────────


def run_auction(config: AuctionConfig) -> AuctionResult:
    """Execute a single auction simulation.

    The simulation pipeline:
        1. Generate raw bids from the configured distribution.
        2. Apply identity resolution filtering (stochastic).
        3. Filter out bids below the floor price.
        4. Determine winner and win price based on auction type.
        5. Compute efficiency, spread, and depth metrics.

    Args:
        config: The :class:`AuctionConfig` specifying auction parameters.

    Returns:
        An :class:`AuctionResult` with the outcome of this auction.
    """
    # Step 1: Generate raw bids
    raw_bids = generate_bids(
        config.num_bidders, config.bid_distribution, config.bid_params
    )

    # Step 2: Apply identity resolution filter
    bids = [b for b in raw_bids if random.random() < config.identity_resolution_rate]

    # Step 3: Filter by floor price and sort descending
    bids_above_floor = sorted(
        [b for b in bids if b >= config.floor_price], reverse=True
    )

    # Handle no-fill case
    if not bids_above_floor:
        spread = statistics.stdev(bids) if len(bids) > 1 else 0.0
        return AuctionResult(
            config_name=config.name,
            bids=bids,
            highest_bid=0,
            second_highest_bid=0,
            win_price=0,
            floor_price=config.floor_price,
            filled=False,
            auction_efficiency=0,
            bid_spread=spread,
            bid_depth=0,
        )

    highest = bids_above_floor[0]
    second = bids_above_floor[1] if len(bids_above_floor) > 1 else 0

    # Step 4: Determine win price by auction type
    if config.auction_type == "first_price":
        # Winner pays their own bid (truthful bidding assumption)
        win_price = highest
        efficiency = 100.0
    else:
        # Winner pays second-highest bid (Vickrey auction)
        win_price = second if second > 0 else highest
        efficiency = (win_price / highest * 100) if highest > 0 else 100.0

    # Step 5: Compute metrics
    spread = statistics.stdev(bids) if len(bids) > 1 else 0.0

    return AuctionResult(
        config_name=config.name,
        bids=bids,
        highest_bid=highest,
        second_highest_bid=second,
        win_price=win_price,
        floor_price=config.floor_price,
        filled=True,
        auction_efficiency=min(efficiency, 100.0),
        bid_spread=spread,
        bid_depth=len(bids_above_floor),
    )


# ─── Batch Simulation ──────────────────────────────────────────────────────


def run_simulations(
    configs: List[AuctionConfig], num_runs: int = 10000
) -> Dict[str, List[AuctionResult]]:
    """Run multiple auction simulations for each configuration.

    Args:
        configs: A list of :class:`AuctionConfig` instances to simulate.
        num_runs: Number of independent auction runs per configuration.

    Returns:
        A dictionary mapping configuration names to lists of :class:`AuctionResult`.
    """
    results: Dict[str, List[AuctionResult]] = {}
    for config in configs:
        results[config.name] = [run_auction(config) for _ in range(num_runs)]
    return results


# ─── KPI Computation ───────────────────────────────────────────────────────


def compute_kpis(results: Dict[str, List[AuctionResult]]) -> Dict:
    """Compute aggregate KPI statistics from simulation results.

    Computes the following KPIs per scenario:
        - **Fill Rate**: Percentage of auctions resulting in a successful placement.
        - **Auction Efficiency**: Mean revenue / theoretical maximum (%).
        - **Avg / Median / P90 Win Price**: Distribution of clearing prices.
        - **Avg Bid Spread**: Mean standard deviation of bid values.
        - **Avg Bid Depth**: Mean number of competitive bids per auction.
        - **Revenue per Request**: Mean win price across all requests.

    Args:
        results: Output from :func:`run_simulations`.

    Returns:
        A dict mapping scenario names to dicts of computed KPI values.
    """
    analysis = {}
    for cname, cresults in results.items():
        filled = [r for r in cresults if r.filled]
        fill_rate = len(filled) / len(cresults) * 100.0

        effs = [r.auction_efficiency for r in filled]
        wps = [r.win_price for r in filled]
        spreads = [r.bid_spread for r in cresults]
        depths = [r.bid_depth for r in cresults]
        n_bids_actual = [len(r.bids) for r in cresults]

        sorted_wps = sorted(wps) if wps else [0.0]
        p90_idx = min(int(len(sorted_wps) * 0.9), len(sorted_wps) - 1)

        analysis[cname] = {
            "num_simulations": len(cresults),
            "fill_rate_pct": round(fill_rate, 2),
            "avg_auction_efficiency_pct": (
                round(statistics.mean(effs), 2) if effs else 0
            ),
            "std_auction_efficiency_pct": (
                round(statistics.stdev(effs), 2) if len(effs) > 1 else 0
            ),
            "avg_win_price": (
                round(statistics.mean(wps), 4) if wps else 0
            ),
            "median_win_price": (
                round(statistics.median(wps), 4) if wps else 0
            ),
            "p90_win_price": (
                round(sorted_wps[p90_idx], 4) if wps else 0
            ),
            "avg_bid_spread": round(statistics.mean(spreads), 4),
            "avg_bid_depth": round(statistics.mean(depths), 2),
            "avg_num_bids_per_auction": round(
                statistics.mean(n_bids_actual), 2
            ),
            "revenue_per_request": (
                round(statistics.mean(wps), 4) if wps else 0
            ),
        }
    return analysis