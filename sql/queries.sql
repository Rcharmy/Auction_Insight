-- ============================================================================
-- AuctionInsight — KPI Computation Queries
-- ============================================================================
-- These queries operationalise the core KPIs defined in the AuctionInsight
-- KPI Standards document. They assume the schemas from schemas.sql are in
-- place. All monetary values are in the same unit (micros or cents).
-- ============================================================================


-- ─── Fill Rate ─────────────────────────────────────────────────────────────
-- Definition: % of ad requests that result in a successful ad placement.

SELECT
    DATE(timestamp) AS day,
    placement_id,
    COUNT(*) AS total_requests,
    SUM(CASE WHEN win_price > 0 THEN 1 ELSE 0 END) AS filled,
    ROUND(
        100.0 * SUM(CASE WHEN win_price > 0 THEN 1 ELSE 0 END) / COUNT(*), 2
    ) AS fill_rate_pct
FROM auction_events
GROUP BY DATE(timestamp), placement_id
ORDER BY day DESC;


-- ─── Identity Recognition Rate (IRR) ──────────────────────────────────────
-- Definition: % of bid requests where the user identity is resolved.

SELECT
    DATE(timestamp) AS day,
    identity_provider,
    COUNT(*) AS total_requests,
    SUM(CASE WHEN user_id_available THEN 1 ELSE 0 END) AS resolved,
    ROUND(
        100.0 * SUM(CASE WHEN user_id_available THEN 1 ELSE 0 END) / COUNT(*), 2
    ) AS irr_pct
FROM bid_requests
GROUP BY DATE(timestamp), identity_provider
ORDER BY day DESC;


-- ─── Auction Efficiency (2nd-price model) ─────────────────────────────────
-- Definition: Revenue captured relative to theoretical maximum.

SELECT
    DATE(timestamp) AS day,
    placement_id,
    COUNT(*) AS auctions,
    ROUND(AVG(win_price), 4) AS avg_win_price,
    ROUND(AVG(second_highest_bid), 4) AS avg_second_bid,
    ROUND(
        100.0 * AVG(win_price) / NULLIF(AVG(second_highest_bid), 0), 2
    ) AS auction_efficiency_pct
FROM auction_events
WHERE second_highest_bid > 0
GROUP BY DATE(timestamp), placement_id
ORDER BY day DESC;


-- ─── Bid Depth Distribution ───────────────────────────────────────────────
-- Distribution of competitive bid counts per auction.

SELECT
    bid_depth,
    COUNT(*) * 100.0 / SUM(COUNT(*)) OVER () AS pct_of_auctions
FROM (
    SELECT COUNT(*) AS bid_depth
    FROM bid_requests
    WHERE bid_price > 0 AND bid_status = 'bid'
    GROUP BY auction_id
)
GROUP BY bid_depth
ORDER BY bid_depth;


-- ─── Bid Spread Analysis ──────────────────────────────────────────────────
-- Standard deviation of bid values per placement.

SELECT
    ae.placement_id,
    ROUND(AVG(br_spread.bid_stddev), 4) AS avg_bid_spread
FROM (
    SELECT
        auction_id,
        STDDEV(bid_price) AS bid_stddev
    FROM bid_requests
    WHERE bid_price > 0 AND bid_status = 'bid'
    GROUP BY auction_id
) br_spread
JOIN auction_events ae ON br_spread.auction_id = ae.auction_id
GROUP BY ae.placement_id;


-- ─── Identity Resolution Success Rate (from pipeline) ─────────────────────
-- Tracks the effectiveness of the identity resolution pipeline.

SELECT
    DATE(timestamp) AS day,
    identity_provider,
    resolution_method,
    COUNT(*) AS attempts,
    SUM(CASE WHEN resolution_success THEN 1 ELSE 0 END) AS successes,
    ROUND(
        100.0 * SUM(CASE WHEN resolution_success THEN 1 ELSE 0 END) / COUNT(*), 2
    ) AS success_rate_pct,
    ROUND(AVG(latency_ms), 1) AS avg_latency_ms
FROM identity_resolution
GROUP BY DATE(timestamp), identity_provider, resolution_method
ORDER BY day DESC, success_rate_pct DESC;


-- ─── Revenue per Request (overall KPI) ────────────────────────────────────
-- Mean revenue generated per ad request.

SELECT
    DATE(timestamp) AS day,
    placement_id,
    ROUND(AVG(win_price), 4) AS revenue_per_request
FROM auction_events
GROUP BY DATE(timestamp), placement_id
ORDER BY day DESC, revenue_per_request DESC;