# Amazon Intelligence Subscription — Volume 1
# AuctionInsight — Weekly Supply & Auction Efficiency Intelligence Deck
# Week 26, 2026-06-29

## Executive Summary

**Amazon DSP fill rates improved 4.2% week-over-week** following identity resolution upgrades. Auction efficiency is stable at 93%, with notable gains in Sponsored Brands campaigns.

| KPI | Current | WoW Change | Status |
|-----|---------|------------|--------|
| Fill Rate | 88.3% | +4.2% | 🟢 Improving |
| Auction Efficiency | 93.1% | +0.7% | 🟢 Stable |
| Avg Win Price | $1.82 | +$0.09 | 🟢 Improving |
| Identity Recognition | 72.6% | +5.3% | 🟢 Improving |
| AMC Attribution Rate | 87.2% | +12.0% | 🟢 Improving |

---

## Key Insights

### 1. Identity Resolution Upgrade Driving Fill Rate Gains
The recent identity resolution infrastructure upgrade has increased the Identity Recognition Rate from 67.3% to 72.6% (+5.3pp). This directly correlates with a 4.2pp improvement in Fill Rate (84.1% → 88.3%), consistent with our Monte Carlo simulation projections.

### 2. Auction Efficiency Remains Strong
At 93.1%, auction efficiency is within the "Excellent" benchmark range (>95% target). The slight gap is attributable to increased bidder depth (now averaging 4.2 bids/auction vs 3.8 last week), which naturally reduces efficiency in 2nd-price auctions but increases absolute revenue.

### 3. AMC Attribution Accuracy Improving
Amazon Marketing Cloud query optimization has yielded a 12% improvement in attribution accuracy for upper-funnel DSP campaigns. This enables more precise ROAS measurement and budget allocation.

---

## Recommended Actions

| Priority | Action | Expected Impact |
|----------|--------|-----------------|
| P0 | Continue identity resolution rollout to remaining DSP integrations | 5-8% additional fill rate improvement |
| P1 | Implement dynamic floor pricing for high-depth placements | 3-5% revenue uplift |
| P2 | Run AMC-based audience analysis for Sponsored Brands | Improved ROAS targeting |

---

## KPI Detail

### Fill Rate by Campaign Type

| Campaign Type | Fill Rate | WoW Change |
|---------------|-----------|------------|
| Sponsored Products | 91.2% | +2.1% |
| Sponsored Brands | 87.4% | +5.8% |
| Sponsored Display | 85.3% | +3.4% |
| DSP (Display) | 89.1% | +4.9% |

### Identity Recognition by Provider

| Provider | IRR | WoW Change |
|----------|-----|------------|
| Amazon Ads ID | 78.4% | +6.2% |
| Third-Party Cookie | 65.1% | +3.8% |
| Server-Side Sync | 74.3% | +5.1% |

---

## Methodology

- **Data Sources:** Amazon DSP API, Amazon Marketing Cloud (AMC) queries, Amazon Marketing Stream (AMS) event feed
- **Attribution Window:** 14-day click, 14-day view
- **Computation:** KPI definitions per AuctionInsight KPI Standards v1.0
- **Simulation Reference:** Monte Carlo simulation (40,000 runs across 8 scenarios) — see auctioninsight-engine

---

*Volume 1 | AuctionInsight — Amazon Intelligence Subscription*
*Contact: team@auctioninsight.io*