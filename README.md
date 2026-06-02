# Nassau Candy Distributor - Route Efficiency Analysis

## Project Overview
This project focuses on optimizing logistics and distribution operations for Nassau Candy Distributor. By building a Python data pipeline, we analyzed 10,194 historical fulfillment transactions to evaluate shipping lead times, isolate regional infrastructure constraints, and benchmark delivery methods.

## Data Pipeline & Methodology
Using **Python and Pandas**, the following operations were executed:
1. **Feature Engineering:** Calculated explicit `Shipping Lead Time` as `Ship Date` minus `Order Date`.
2. **Factory Mapping:** Associated item classifications back to five physical production facilities based on administrative business rules.
3. **Route Structuring:** Automated the generation of `Origin Factory -> Destination State` transit vectors.
4. **Statistical Aggregation:** Calculated mean delivery durations, transaction volumes, and performance margins across regions and ship modes.

## Key Insights
* **Network Baseline:** The global average shipping lead time is 1,320.84 days.
* **Geographic Bottlenecks:** Distribution corridors serving New Jersey, New Hampshire, and Connecticut exhibit severe infrastructure friction, with turnaround times stretching to 1,641–1,642 days.
* **The Shipping Paradox:** Standard Class ground shipping yields the fastest turnaround velocity across the network (1,314.33 days), whereas premium First Class methods consistently underperform (1,338.28 days), pointing to internal hub consolidation backlogs rather than carrier transit delays.
