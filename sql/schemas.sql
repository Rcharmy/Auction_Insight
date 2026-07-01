-- ============================================================================
-- AuctionInsight — SQL Schemas for Auction Analytics
-- ============================================================================
-- This file defines the database schema for logging auction events,
-- bid requests, and identity resolution data. These schemas are designed
-- for BigQuery / Snowflake / Redshift and support the computation of
-- Fill Rate, Identity Recognition Rate (IRR), and Auction Efficiency KPIs.
-- ============================================================================


-- ─── 1. Auction Events (canonical auction lifecycle) ─────────────────────

CREATE TABLE IF NOT EXISTS auction_events (
    timestamp           TIMESTAMP       NOT NULL,
    placement_id        STRING          NOT NULL,
    auction_id          STRING          NOT NULL,
    user_id             STRING,
    identity_provider   STRING,
    win_price           FLOAT64         NOT NULL DEFAULT 0.0,
    bid_count           INT64           NOT NULL DEFAULT 0,
    highest_bid         FLOAT64,
    second_highest_bid  FLOAT64         DEFAULT 0.0,
    floor_price         FLOAT64,
    auction_type        STRING          NOT NULL,       -- 'first_price' | 'second_price' | 'uniform'
    device_type         STRING,                          -- 'desktop' | 'mobile' | 'ctv' | 'tablet'
    geo                 STRING,                          -- ISO country code
    ad_format           STRING,                          -- 'display' | 'video' | 'native' | 'audio'
    latency_ms          INT64,
    ssp_id              STRING,
    publisher_id        STRING,
    timeout_indicator   BOOLEAN         DEFAULT FALSE,
    passback_triggered  BOOLEAN         DEFAULT FALSE,
    deal_id             STRING
)
PARTITION BY DATE(timestamp)
CLUSTER BY placement_id, publisher_id;


-- ─── 2. Bid Requests (per-DSP tracking) ─────────────────────────────────

CREATE TABLE IF NOT EXISTS bid_requests (
    timestamp           TIMESTAMP       NOT NULL,
    bid_request_id      STRING          NOT NULL,
    auction_id          STRING          NOT NULL,
    dsp_id              STRING          NOT NULL,
    user_id_available   BOOLEAN         NOT NULL DEFAULT FALSE,
    identity_provider   STRING,
    floor_price         FLOAT64,
    timeout_ms          INT64,
    response_time_ms    INT64,
    bid_price           FLOAT64,
    bid_status          STRING          NOT NULL,       -- 'bid' | 'nobid' | 'timeout' | 'error'
    deal_id             STRING
)
PARTITION BY DATE(timestamp)
CLUSTER BY dsp_id, auction_id;


-- ─── 3. Identity Resolution (identity pipeline) ──────────────────────────

CREATE TABLE IF NOT EXISTS identity_resolution (
    timestamp           TIMESTAMP       NOT NULL,
    user_id_raw         STRING          NOT NULL,
    user_id_resolved    STRING,
    identity_provider   STRING          NOT NULL,
    resolution_method   STRING          NOT NULL,       -- 'cookie_sync' | 'server_side' | 'first_party' | 'api'
    resolution_success  BOOLEAN         NOT NULL DEFAULT FALSE,
    latency_ms          INT64,
    error_code          STRING
)
PARTITION BY DATE(timestamp)
CLUSTER BY identity_provider, resolution_success;