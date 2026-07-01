"""
PySpark KPI Computation Templates for AuctionInsight.

These templates process auction event data at scale using PySpark,
computing the core KPIs: Fill Rate, Identity Recognition Rate (IRR),
Auction Efficiency, and Revenue per Request.

Usage:
    spark-submit pyspark/kpi_computation.py \
        --input-path s3://data-lake/auction_events/ \
        --output-path s3://analytics/kpi_summary/
"""

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import (
    col, count, sum, when, avg, stddev, date_format, round as spark_round
)
from pyspark.sql.window import Window
import argparse


def create_spark_session(app_name: str = "AuctionInsight-KPI") -> SparkSession:
    """Create and configure a Spark session for auction analytics."""
    return (
        SparkSession.builder
        .appName(app_name)
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
        .config("spark.sql.sources.partitionOverwriteMode", "dynamic")
        .getOrCreate()
    )


# ─── 1. Fill Rate ──────────────────────────────────────────────────────────

def compute_fill_rate(events: DataFrame) -> DataFrame:
    """Compute Fill Rate per day per placement.

    Fill Rate = (Successful placements) / (Total ad requests) × 100

    Args:
        events: DataFrame with columns ``timestamp``, ``placement_id``, ``win_price``.

    Returns:
        DataFrame with ``day``, ``placement_id``, ``fill_rate_pct``.
    """
    return (
        events
        .withColumn("day", date_format("timestamp", "yyyy-MM-dd"))
        .groupBy("day", "placement_id")
        .agg(
            count("*").alias("total_requests"),
            sum(when(col("win_price") > 0, 1).otherwise(0)).alias("filled"),
        )
        .withColumn(
            "fill_rate_pct",
            spark_round(col("filled") / col("total_requests") * 100, 2)
        )
        .orderBy("day", ascending=False)
    )


# ─── 2. Identity Recognition Rate (IRR) ───────────────────────────────────

def compute_irr(bid_requests: DataFrame) -> DataFrame:
    """Compute Identity Recognition Rate per day per identity provider.

    IRR = (Bid requests with resolved identity) / (Total bid requests) × 100

    Args:
        bid_requests: DataFrame with columns ``timestamp``,
            ``identity_provider``, ``user_id_available``.

    Returns:
        DataFrame with ``day``, ``identity_provider``, ``irr_pct``.
    """
    return (
        bid_requests
        .withColumn("day", date_format("timestamp", "yyyy-MM-dd"))
        .groupBy("day", "identity_provider")
        .agg(
            count("*").alias("total_requests"),
            sum(when(col("user_id_available"), 1).otherwise(0)).alias("resolved"),
        )
        .withColumn(
            "irr_pct",
            spark_round(col("resolved") / col("total_requests") * 100, 2)
        )
        .orderBy("day", ascending=False)
    )


# ─── 3. Auction Efficiency ─────────────────────────────────────────────────

def compute_auction_efficiency(events: DataFrame) -> DataFrame:
    """Compute Auction Efficiency per day per placement.

    Efficiency = (Revenue) / (Theoretical maximum) × 100
    For 2nd-price auctions: max = second_highest_bid.

    Args:
        events: DataFrame with columns ``timestamp``, ``placement_id``,
            ``win_price``, ``second_highest_bid``.

    Returns:
        DataFrame with ``day``, ``placement_id``, ``auction_efficiency_pct``.
    """
    return (
        events
        .filter(col("second_highest_bid") > 0)
        .withColumn("day", date_format("timestamp", "yyyy-MM-dd"))
        .groupBy("day", "placement_id")
        .agg(
            count("*").alias("auctions"),
            spark_round(avg("win_price"), 4).alias("avg_win_price"),
            spark_round(avg("second_highest_bid"), 4).alias("avg_second_bid"),
            spark_round(
                avg(col("win_price") / col("second_highest_bid")) * 100, 2
            ).alias("auction_efficiency_pct"),
        )
        .orderBy("day", ascending=False)
    )


# ─── 4. Revenue per Request ────────────────────────────────────────────────

def compute_revenue_per_request(events: DataFrame) -> DataFrame:
    """Compute Revenue per Request per day per placement.

    Args:
        events: DataFrame with columns ``timestamp``, ``placement_id``,
            ``win_price``.

    Returns:
        DataFrame with ``day``, ``placement_id``, ``revenue_per_request``.
    """
    return (
        events
        .withColumn("day", date_format("timestamp", "yyyy-MM-dd"))
        .groupBy("day", "placement_id")
        .agg(
            spark_round(avg("win_price"), 4).alias("revenue_per_request")
        )
        .orderBy("day", ascending=False)
    )


# ─── 5. Bid Depth Distribution ─────────────────────────────────────────────

def compute_bid_depth_distribution(bid_requests: DataFrame) -> DataFrame:
    """Compute the distribution of competitive bid counts per auction.

    Args:
        bid_requests: DataFrame with columns ``auction_id``, ``bid_price``,
            ``bid_status``.

    Returns:
        DataFrame with ``bid_depth``, ``pct_of_auctions``.
    """
    depth_counts = (
        bid_requests
        .filter((col("bid_price") > 0) & (col("bid_status") == "bid"))
        .groupBy("auction_id")
        .agg(count("*").alias("bid_depth"))
    )

    total_auctions = depth_counts.count()

    return (
        depth_counts
        .groupBy("bid_depth")
        .agg(
            spark_round(
                count("*") / total_auctions * 100, 2
            ).alias("pct_of_auctions")
        )
        .orderBy("bid_depth")
    )


# ─── 6. Identity Resolution Pipeline Success ──────────────────────────────

def compute_identity_success_rate(identity_resolution: DataFrame) -> DataFrame:
    """Track identity resolution pipeline effectiveness.

    Args:
        identity_resolution: DataFrame with columns ``timestamp``,
            ``identity_provider``, ``resolution_method``, ``resolution_success``,
            ``latency_ms``.

    Returns:
        DataFrame with daily success rates and latency by provider/method.
    """
    return (
        identity_resolution
        .withColumn("day", date_format("timestamp", "yyyy-MM-dd"))
        .groupBy("day", "identity_provider", "resolution_method")
        .agg(
            count("*").alias("attempts"),
            sum(when(col("resolution_success"), 1).otherwise(0)).alias("successes"),
            spark_round(avg("latency_ms"), 1).alias("avg_latency_ms"),
        )
        .withColumn(
            "success_rate_pct",
            spark_round(col("successes") / col("attempts") * 100, 2)
        )
        .orderBy(col("day").desc(), col("success_rate_pct").desc())
    )


# ─── Main Pipeline ─────────────────────────────────────────────────────────

def run_pipeline(
    spark: SparkSession,
    events_path: str,
    bid_requests_path: str,
    identity_path: str,
    output_path: str,
):
    """Run the full KPI computation pipeline.

    Args:
        spark: Active SparkSession.
        events_path: Path to auction_events parquet data.
        bid_requests_path: Path to bid_requests parquet data.
        identity_path: Path to identity_resolution parquet data.
        output_path: Path for output KPI summaries.
    """
    events = spark.read.parquet(events_path)
    bid_reqs = spark.read.parquet(bid_requests_path)
    identity = spark.read.parquet(identity_path)

    # Compute all KPIs
    fill_rate = compute_fill_rate(events)
    irr = compute_irr(bid_reqs)
    efficiency = compute_auction_efficiency(events)
    rev_per_req = compute_revenue_per_request(events)
    bid_depth = compute_bid_depth_distribution(bid_reqs)
    identity_success = compute_identity_success_rate(identity)

    # Write outputs
    fill_rate.coalesce(1).write.mode("overwrite").csv(
        f"{output_path}/fill_rate", header=True
    )
    irr.coalesce(1).write.mode("overwrite").csv(
        f"{output_path}/identity_recognition_rate", header=True
    )
    efficiency.coalesce(1).write.mode("overwrite").csv(
        f"{output_path}/auction_efficiency", header=True
    )
    rev_per_req.coalesce(1).write.mode("overwrite").csv(
        f"{output_path}/revenue_per_request", header=True
    )
    bid_depth.coalesce(1).write.mode("overwrite").csv(
        f"{output_path}/bid_depth_distribution", header=True
    )
    identity_success.coalesce(1).write.mode("overwrite").csv(
        f"{output_path}/identity_success_rate", header=True
    )

    print(f"KPI pipeline complete. Output written to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="AuctionInsight KPI Computation Pipeline (PySpark)"
    )
    parser.add_argument("--input-path", required=True, help="Path to auction data")
    parser.add_argument("--output-path", required=True, help="Path for KPI output")
    parser.add_argument("--bid-requests-path", help="Path to bid request data")
    parser.add_argument("--identity-path", help="Path to identity resolution data")
    args = parser.parse_args()

    spark = create_spark_session()
    run_pipeline(
        spark,
        args.input_path,
        args.bid_requests_path or f"{args.input_path}/bid_requests",
        args.identity_path or f"{args.input_path}/identity_resolution",
        args.output_path,
    )
    spark.stop()