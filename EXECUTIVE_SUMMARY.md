# Executive Summary — Amman Digital Market Analytics

## Top Findings

1. Seasonal Revenue Momentum: The market shows significant monthly fluctuations, with a total revenue peak of 48,701.50 JOD over the analyzed period. Specifically, June 2025 showed a massive growth spike (>150%), indicating a strong seasonal trend that is critical for operational planning. (Reference: output/monthly_revenue.png)

2. Category-Driven Spending (Validated): Through a One-way ANOVA test, I confirmed that the product category has a statistically significant impact on order values (p-value: 0.0000). Categories like Books and Electronics are not just high-sellers, but they fundamentally drive different spending behaviors. (Reference: output/average_order_value_category.png)
 
3. Regional Volume vs. Spending Behavior: While Amman is the clear leader in total revenue volume, my statistical analysis revealed a surprising insight: the average spending per customer in Irbid is nearly identical to Amman (Cohen’s d: 0.0002). This means the revenue gap is purely a matter of customer volume, not individual purchasing power. (Reference: output/revenue_by_city.png)

## Supporting Data

- **Finding 1:** Refer to the Monthly Revenue Performance chart (output/monthly_revenue.png). It shows the trend of cleaned revenue over time, highlighting the significant growth peaks.

- **Finding 2:** Refer to the AOV by Product Category chart (output/average_order_value_category.png) and the Revenue Variance per Category boxplot (output/revenue_boxplot.png). These visuals, combined with the ANOVA results, prove that category selection is a key driver of order value.

- **Finding 3:** Refer to the Regional Revenue Contribution bar chart (output/revenue_by_city.png). This plot supports the finding that while Amman leads in volume, the spending behavior across cities is remarkably consistent, as confirmed by the Welch’s T-test.
## Recommendations

1. Seasonal Operations Scaling: Based on the high revenue peaks identified in June, I recommend scaling up logistics and inventory levels at least 30 days prior to these periods. Since my analysis showed a 150% growth spike, failing to prepare for this seasonality would lead to significant missed revenue. 

2.Customer Acquisition in Irbid: Since the Welch’s T-test confirmed that customers in Irbid spend almost the same amount per order as those in Amman (Cohen’s d: 0.0002), the focus should be on increasing the number of users in Irbid. The purchasing power is there; we just need more order volume from that city.

3.Category-Specific Bundling: Given the statistically significant differences in spending across categories (confirmed by the ANOVA test), we should create "premium bundles" for high-AOV categories like Books and Electronics. Targeting these specific segments will maximize the total revenue since their spending behavior is proven to be higher.