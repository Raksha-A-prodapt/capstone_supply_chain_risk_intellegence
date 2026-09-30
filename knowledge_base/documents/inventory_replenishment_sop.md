# Inventory Replenishment & Stock-Out Mitigation SOP (SOP-INV-002)

## 1. Safety Stock and Reorder Calculation
Deterministic safety stock is determined using the 95% service level factor (Z = 1.65):
`Safety Stock = Z * sqrt((Avg Lead Time * Demand Variance^2) + (Avg Daily Demand^2 * Lead Time Variance^2))`

The Reorder Point (ROP) is governed by:
`ROP = (Daily Demand * Expected Lead Time) + Safety Stock`

Recommended Reorder Quantity (ROQ) is computed deterministically as:
`ROQ = max(0, (Expected Demand During Lead Time + Safety Stock) - Current Inventory)`

## 2. Stock-Out Risk Classifications
- **Critical Stock-Out Risk**: Current inventory coverage is 5.0 days or fewer (Days of Supply <= 5.0). Action: Emergency reorder PO issued within 4 hours; initiate stock transfers from sister distribution hubs.
- **High Stock-Out Risk**: Current inventory level is strictly below the computed Reorder Point (ROP) or Days of Supply <= Lead Time. Action: Expedite outstanding supplier POs and restrict non-critical customer allocations.
- **Moderate Stock-Out Risk**: Current inventory is within 7 days above ROP. Action: Monitor daily consumption trends.
- **Low Risk**: Inventory comfortably exceeds ROP with coverage exceeding 20 business days.
