"""
Pre-defined auction scenarios for benchmarking and analysis.

Each scenario represents a realistic configuration of auction parameters
that can be simulated and compared. Scenarios cover variations in:
- Auction type (1st-price vs 2nd-price)
- Bidder depth (5 vs 10 bidders)
- Floor prices ($0.50 vs $1.00)
- Identity resolution rates (30%, 60%, 85%)
- Bid distributions (log-normal vs exponential)
"""

from auctioninsight.core import AuctionConfig


# ─── Standard Scenarios ────────────────────────────────────────────────────

SCENARIOS = [
    AuctionConfig(
        name="Baseline_2ndPrice_5Bidders",
        auction_type="second_price",
        num_bidders=5,
        floor_price=0.50,
        bid_distribution="log_normal",
        bid_params=(0.0, 0.8),
        identity_resolution_rate=0.60,
    ),
    AuctionConfig(
        name="Baseline_1stPrice_5Bidders",
        auction_type="first_price",
        num_bidders=5,
        floor_price=0.50,
        bid_distribution="log_normal",
        bid_params=(0.0, 0.8),
        identity_resolution_rate=0.60,
    ),
    AuctionConfig(
        name="HighDepth_2ndPrice_10Bidders",
        auction_type="second_price",
        num_bidders=10,
        floor_price=0.50,
        bid_distribution="log_normal",
        bid_params=(0.0, 0.8),
        identity_resolution_rate=0.60,
    ),
    AuctionConfig(
        name="HighFloor_2ndPrice_5Bidders",
        auction_type="second_price",
        num_bidders=5,
        floor_price=1.00,
        bid_distribution="log_normal",
        bid_params=(0.0, 0.8),
        identity_resolution_rate=0.60,
    ),
    AuctionConfig(
        name="HighIdentity_2ndPrice_5Bidders",
        auction_type="second_price",
        num_bidders=5,
        floor_price=0.50,
        bid_distribution="log_normal",
        bid_params=(0.0, 0.8),
        identity_resolution_rate=0.85,
    ),
    AuctionConfig(
        name="LowIdentity_2ndPrice_5Bidders",
        auction_type="second_price",
        num_bidders=5,
        floor_price=0.50,
        bid_distribution="log_normal",
        bid_params=(0.0, 0.8),
        identity_resolution_rate=0.30,
    ),
    AuctionConfig(
        name="ExpBids_2ndPrice_5Bidders",
        auction_type="second_price",
        num_bidders=5,
        floor_price=0.50,
        bid_distribution="exponential",
        bid_params=(1.0,),
        identity_resolution_rate=0.60,
    ),
    AuctionConfig(
        name="HighDepth_1stPrice_10Bidders",
        auction_type="first_price",
        num_bidders=10,
        floor_price=0.50,
        bid_distribution="log_normal",
        bid_params=(0.0, 0.8),
        identity_resolution_rate=0.60,
    ),
]

SCENARIO_DESCRIPTIONS = {
    "Baseline_2ndPrice_5Bidders": (
        "Baseline: 2nd-price, 5 bidders, $0.50 floor, 60% identity"
    ),
    "Baseline_1stPrice_5Bidders": (
        "1st-Price: 5 bidders, $0.50 floor, 60% identity"
    ),
    "HighDepth_2ndPrice_10Bidders": (
        "High Depth: 2nd-price, 10 bidders, $0.50 floor, 60% identity"
    ),
    "HighFloor_2ndPrice_5Bidders": (
        "High Floor: 2nd-price, 5 bidders, $1.00 floor, 60% identity"
    ),
    "HighIdentity_2ndPrice_5Bidders": (
        "High Identity: 2nd-price, 5 bidders, $0.50 floor, 85% identity"
    ),
    "LowIdentity_2ndPrice_5Bidders": (
        "Low Identity: 2nd-price, 5 bidders, $0.50 floor, 30% identity"
    ),
    "ExpBids_2ndPrice_5Bidders": (
        "Exponential Bids: 2nd-price, 5 bidders, $0.50 floor"
    ),
    "HighDepth_1stPrice_10Bidders": (
        "High Depth + 1st-Price: 10 bidders, $0.50 floor, 60% identity"
    ),
}


def get_scenario(name: str) -> AuctionConfig:
    """Look up a scenario by name.

    Args:
        name: The scenario name (e.g., ``"Baseline_2ndPrice_5Bidders"``).

    Returns:
        The matching :class:`AuctionConfig`.

    Raises:
        KeyError: If no scenario with the given name exists.
    """
    for s in SCENARIOS:
        if s.name == name:
            return s
    raise KeyError(f"Unknown scenario: '{name}'")


def get_scenario_names() -> list[str]:
    """Return the list of available scenario names."""
    return [s.name for s in SCENARIOS]