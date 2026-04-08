"""Integration 4 — KPI Dashboard: Amman Digital Market Analytics

Extract data from PostgreSQL, compute KPIs, run statistical tests,
and create visualizations for the executive summary.

Usage:
    python analysis.py
"""
import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sqlalchemy import create_engine


def connect_db():
    """Create a SQLAlchemy engine connected to the amman_market database.

    Returns:
        engine: SQLAlchemy engine instance

    Notes:
        Use DATABASE_URL environment variable if set, otherwise default to:
        postgresql://postgres:postgres@localhost:5432/amman_market
    """
    
    
    database_url = os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/amman_market"
    )
    engine = create_engine(database_url)
    return engine


def extract_data(engine):
    """Extract all required tables from the database into DataFrames.

    Args:
        engine: SQLAlchemy engine connected to amman_market

    Returns:
        dict: mapping of table names to DataFrames
              (e.g., {"customers": df, "products": df, "orders": df, "order_items": df})
    """

    
    data_dict = {}
    data_dict["customers"] = pd.read_sql("SELECT * FROM customers", engine)
    data_dict["products"] = pd.read_sql("SELECT * FROM products", engine)
    # Exclude cancelled orders
    data_dict["orders"] = pd.read_sql(
        "SELECT * FROM orders WHERE status != 'cancelled'", engine
    )
    # Exclude suspicious quantities > 100
    data_dict["order_items"] = pd.read_sql(
        "SELECT * FROM order_items WHERE quantity <= 100", engine
    )
    return data_dict


def compute_kpis(data_dict):
    """Compute the 5 KPIs defined in kpi_framework.md.

    Args:
        data_dict: dict of DataFrames from extract_data()

    Returns:
        dict: mapping of KPI names to their computed values (or DataFrames
              for time-series / cohort KPIs)

    Notes:
        At least 2 KPIs should be time-based and 1 should be cohort-based.
    """
    
    customers = data_dict["customers"]
    products = data_dict["products"]
    orders = data_dict["orders"]
    order_items = data_dict["order_items"]

    # Merge tables
    orders_items_merged = order_items.merge(
        orders, on="order_id", how="left"
    ).merge(products, on="product_id", how="left")
    
    orders_items_merged["total_price"] = orders_items_merged["quantity"] * orders_items_merged["unit_price"]

    kpis = {}

    # KPI 1: Total Revenue
    kpis["Total Revenue"] = orders_items_merged["total_price"].sum()

    # KPI 2: Average Order Value
    order_totals = orders_items_merged.groupby("order_id")["total_price"].sum()
    kpis["Average Order Value"] = order_totals.mean()

    # KPI 3: Monthly Revenue (time-based)
    orders_items_merged["order_month"] = pd.to_datetime(orders_items_merged["order_date"]).dt.to_period("M")
    monthly_revenue = orders_items_merged.groupby("order_month")["total_price"].sum().reset_index()
    kpis["Monthly Revenue"] = monthly_revenue

    # KPI 4: Revenue by City (cohort-based)
    revenue_by_city = orders_items_merged.merge(customers, on="customer_id", how="left") \
        .groupby("city")["total_price"].sum().reset_index()
    kpis["Revenue by City"] = revenue_by_city

    # KPI 5: Top 5 Product Categories by Revenue
    revenue_by_category = orders_items_merged.groupby("category")["total_price"].sum().reset_index()
    revenue_by_category = revenue_by_category.sort_values(by="total_price", ascending=False).head(5)
    kpis["Top 5 Categories"] = revenue_by_category
    
    # Ensure 'category' is string and keep detailed merged DataFrame for boxplot
    orders_items_merged["category"] = orders_items_merged["category"].astype(str)
    kpis["Order Items by Category"] = orders_items_merged
    return kpis


def run_statistical_tests(data_dict):
    """Run hypothesis tests to validate patterns in the data.

    Args:
        data_dict: dict of DataFrames from extract_data()

    Returns:
        dict: mapping of test names to results (test statistic, p-value,
              interpretation)

    Notes:
        Run at least one test. Consider:
        - Does average order value differ across product categories?
        - Is there a significant trend in monthly revenue?
        - Do customer cities differ in purchasing behavior?
    """


    customers = data_dict["customers"]
    products = data_dict["products"]
    orders = data_dict["orders"]
    order_items = data_dict["order_items"]

    # Merge tables
    merged = order_items.merge(orders, on="order_id").merge(products, on="product_id")
    merged["total_price"] = merged["quantity"] * merged["unit_price"]

    # Group by order
    order_totals = merged.groupby(["order_id", "category"])["total_price"].sum().reset_index()

    # ANOVA: total_price by category
    categories = order_totals["category"].unique()
    groups = [order_totals[order_totals["category"]==c]["total_price"] for c in categories]
    f_stat, p_val = stats.f_oneway(*groups)

    results = {
        "ANOVA_TotalPrice_by_Category": {
            "F-statistic": f_stat,
            "p-value": p_val,
            "interpretation": "Significant difference" if p_val < 0.05 else "No significant difference"
        }
    }
    return results


def create_visualizations(kpi_results, stat_results):
    """Create publication-quality charts for all 5 KPIs.

    Args:
        kpi_results: dict from compute_kpis()
        stat_results: dict from run_statistical_tests()

    Returns:
        None

    Side effects:
        Saves at least 5 PNG files to the output/ directory.
        Each chart should have a descriptive title stating the finding,
        proper axis labels, and annotations where appropriate.
    """
   
    import matplotlib.pyplot as plt
    import seaborn as sns
    import os

    os.makedirs("output", exist_ok=True)
    sns.set_palette("colorblind")

    # 1️- Monthly Revenue Line Chart
    plt.figure(figsize=(10,5))
    monthly_revenue = kpi_results['Monthly Revenue'].copy()
    monthly_revenue['order_month'] = monthly_revenue['order_month'].astype(str)  # Convert to string
    sns.lineplot(
        x='order_month',
        y='total_price',
        data=monthly_revenue,
        marker='o'
    )
    plt.title("Monthly Revenue Trend")
    plt.xlabel("Month")
    plt.ylabel("Revenue (JOD)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("output/monthly_revenue.png")
    plt.close()

    # 2️- Revenue by City Pie Chart
    plt.figure(figsize=(6,6))
    plt.pie(
        kpi_results['Revenue by City']['total_price'],
        labels=kpi_results['Revenue by City']['city'],
        autopct='%1.1f%%',
        startangle=140
    )
    plt.title("Revenue Contribution by City")
    plt.savefig("output/revenue_by_city.png")
    plt.close()

    # 3️- Average Order Value Bar Chart
    plt.figure(figsize=(6,4))
    plt.bar(["Average Order Value"], [kpi_results['Average Order Value']])
    plt.ylabel("JOD")
    plt.title("Average Order Value per Order")
    plt.savefig("output/average_order_value.png")
    plt.close()

    # 4️- Top 5 Categories Horizontal Bar Chart
    plt.figure(figsize=(6,4))
    sns.barplot(
        x='total_price',
        y='category',
        data=kpi_results['Top 5 Categories']
    )
    plt.xlabel("Revenue (JOD)")
    plt.ylabel("Category")
    plt.title("Top 5 Product Categories by Revenue")
    plt.tight_layout()
    plt.savefig("output/top_5_categories.png")
    plt.close()

    # 5️- Revenue Distribution by Category Boxplot
    plt.figure(figsize=(8,4))
    sns.boxplot(
        x="category",
        y="total_price",
        data=kpi_results['Order Items by Category']  # detailed merged DataFrame
    )
    plt.xticks(rotation=45)
    plt.ylabel("Revenue (JOD)")
    plt.xlabel("Category")
    plt.title("Revenue Distribution by Category (ANOVA)")
    plt.tight_layout()
    plt.savefig("output/revenue_boxplot_by_category.png")
    plt.close()

def main():
    """Orchestrate the full analysis pipeline."""
    os.makedirs("output", exist_ok=True)

    # Connect
    engine = connect_db()

    # Extract
    data_dict = extract_data(engine)

    # Compute KPIs
    kpi_results = compute_kpis(data_dict)
    print("KPI Results:", kpi_results)

    # Run stats tests
    stat_results = run_statistical_tests(data_dict)
    print("Statistical Test Results:", stat_results)

    # Create visualizations
    create_visualizations(kpi_results, stat_results)

if __name__ == "__main__":
    main()
