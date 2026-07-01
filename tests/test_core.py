#!/usr/bin/env python3
"""Basic tests for the AuctionInsight simulation engine."""

import unittest
from auctioninsight.core import AuctionConfig, run_auction, run_simulations, compute_kpis


class TestAuctionConfig(unittest.TestCase):
    """Test AuctionConfig data model."""

    def test_default_config(self):
        config = AuctionConfig(
            name="test",
            auction_type="second_price",
            num_bidders=5,
            floor_price=0.50,
            bid_distribution="log_normal",
            bid_params=(0.0, 0.8),
            identity_resolution_rate=0.60,
        )
        self.assertEqual(config.name, "test")
        self.assertEqual(config.num_bidders, 5)
        self.assertEqual(config.floor_price, 0.50)


class TestAuctionSimulation(unittest.TestCase):
    """Test individual auction simulations."""

    def setUp(self):
        self.config = AuctionConfig(
            name="test",
            auction_type="second_price",
            num_bidders=5,
            floor_price=0.50,
            bid_distribution="log_normal",
            bid_params=(0.0, 0.8),
            identity_resolution_rate=1.0,  # 100% for deterministic identity
        )

    def test_auction_returns_result(self):
        result = run_auction(self.config)
        self.assertIsNotNone(result)
        self.assertEqual(result.config_name, "test")

    def test_bids_are_positive(self):
        result = run_auction(self.config)
        for bid in result.bids:
            self.assertGreater(bid, 0)

    def test_first_price_higher_win_price(self):
        first_price = AuctionConfig(
            name="fp", auction_type="first_price", num_bidders=5,
            floor_price=0.50, bid_distribution="log_normal",
            bid_params=(0.0, 0.8), identity_resolution_rate=1.0,
        )
        second_price = AuctionConfig(
            name="sp", auction_type="second_price", num_bidders=5,
            floor_price=0.50, bid_distribution="log_normal",
            bid_params=(0.0, 0.8), identity_resolution_rate=1.0,
        )
        # Run many auctions and compare averages
        fp_results = [run_auction(first_price) for _ in range(1000)]
        sp_results = [run_auction(second_price) for _ in range(1000)]

        fp_avg = sum(r.win_price for r in fp_results) / len(fp_results)
        sp_avg = sum(r.win_price for r in sp_results) / len(sp_results)

        self.assertGreater(fp_avg, sp_avg)


class TestBatchSimulation(unittest.TestCase):
    """Test batch simulation and KPI computation."""

    def test_simulation_returns_all_configs(self):
        configs = [
            AuctionConfig("a", "second_price", 5, 0.50, "log_normal", (0.0, 0.8), 0.6),
            AuctionConfig("b", "first_price", 5, 0.50, "log_normal", (0.0, 0.8), 0.6),
        ]
        results = run_simulations(configs, num_runs=100)
        self.assertIn("a", results)
        self.assertIn("b", results)
        self.assertEqual(len(results["a"]), 100)
        self.assertEqual(len(results["b"]), 100)

    def test_kpi_computation(self):
        configs = [
            AuctionConfig("a", "second_price", 5, 0.50, "log_normal", (0.0, 0.8), 0.6),
        ]
        results = run_simulations(configs, num_runs=100)
        analysis = compute_kpis(results)

        self.assertIn("a", analysis)
        self.assertIn("fill_rate_pct", analysis["a"])
        self.assertIn("avg_auction_efficiency_pct", analysis["a"])
        self.assertIn("revenue_per_request", analysis["a"])

        # Fill rate should be between 0 and 100
        self.assertGreaterEqual(analysis["a"]["fill_rate_pct"], 0)
        self.assertLessEqual(analysis["a"]["fill_rate_pct"], 100)


class TestBidGeneration(unittest.TestCase):
    """Test bid distribution samplers."""

    def test_log_normal_bids_positive(self):
        from auctioninsight.core import generate_bids
        bids = generate_bids(100, "log_normal", (0.0, 0.8))
        self.assertEqual(len(bids), 100)
        for b in bids:
            self.assertGreater(b, 0)

    def test_uniform_bids_in_range(self):
        from auctioninsight.core import generate_bids
        bids = generate_bids(100, "uniform", (0.0, 5.0))
        for b in bids:
            self.assertGreaterEqual(b, 0.0)
            self.assertLessEqual(b, 5.0)

    def test_exponential_bids_positive(self):
        from auctioninsight.core import generate_bids
        bids = generate_bids(100, "exponential", (1.0,))
        for b in bids:
            self.assertGreater(b, 0)

    def test_unknown_distribution(self):
        from auctioninsight.core import generate_bids
        with self.assertRaises(ValueError):
            generate_bids(10, "unknown", ())


if __name__ == "__main__":
    unittest.main()