---
title: "TODO REQUEST"
source: Notion
synced_date: 2026-04-05
---

# TODO REQUEST

## Purchase Order Model Proposal

### Current Model Issue

Current model focuses on sea/air shipping, doesn't handle split shipments.

### New PO Model

All customer requests = Purchase Order

1 PO can have multiple bookings

Each nghiệp vụ = Purchase Order Process (POP) with independent tracking

### Example

5 kiện hàng door-to-door = 1 PO with 2 bookings and 8 POPs

**Breakdown:**
- 1 Trucking process
- 1 Shipping process
- 1 Customs process
- 1 Trucking return process

### Notes

- BFSOne booking note support
