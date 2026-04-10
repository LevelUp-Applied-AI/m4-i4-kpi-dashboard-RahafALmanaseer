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
    return create_engine("postgresql+psycopg://postgres:postgres@localhost:5432/amman_market")

def extract_data(engine):
    
    orders = pd.read_sql("SELECT * FROM orders WHERE status != 'cancelled'", engine)
    items = pd.read_sql("SELECT * FROM order_items WHERE quantity <= 100", engine)
    products = pd.read_sql("SELECT * FROM products", engine)
    customers = pd.read_sql("SELECT * FROM customers", engine)
    
    df = items.merge(orders, on="order_id").merge(products, on="product_id").merge(customers, on="customer_id")
    df["total_price"] = df["quantity"] * df["unit_price"]
    df["order_date"] = pd.to_datetime(df["order_date"])
    return df

def compute_kpis(df):

    kpis = {}
    kpis['total_revenue'] = df['total_price'].sum()
    
    kpis['avg_order_value'] = df.groupby('order_id')['total_price'].sum().mean()
    return kpis

def run_statistical_tests(df):
    results = {}
    analysis_df = df.groupby(["order_id", "category", "city"])["total_price"].sum().reset_index()

    cats = analysis_df["category"].unique()
    groups = [analysis_df[analysis_df["category"] == cat]["total_price"] for cat in cats]
    f_stat, p_val = stats.f_oneway(*groups)
    
    ss_between = sum([len(g) * (g.mean() - analysis_df["total_price"].mean())**2 for g in groups])
    ss_total = sum((analysis_df["total_price"] - analysis_df["total_price"].mean())**2)
    
    results["ANOVA"] = {"f_stat": f_stat, "p": p_val, "eta": ss_between/ss_total}

    amman = analysis_df[analysis_df["city"] == "Amman"]["total_price"]
    irbid = analysis_df[analysis_df["city"] == "Irbid"]["total_price"]
    t_stat, p_t = stats.ttest_ind(amman, irbid, equal_var=False)
    
    pooled_std = np.sqrt((amman.std()**2 + irbid.std()**2) / 2)
    results["T-Test"] = {"p": p_t, "d": abs((amman.mean() - irbid.mean()) / pooled_std)}

    return results

def create_visualizations(df):
    os.makedirs("output", exist_ok=True)
    sns.set_theme(style="whitegrid")

    monthly_rev = df.set_index('order_date').resample('ME')['total_price'].sum()
    city_rev = df.groupby("city")["total_price"].sum().sort_values(ascending=False)
    cat_aov = df.groupby(["order_id", "category"])["total_price"].sum().reset_index()
    cat_aov_mean = cat_aov.groupby("category")["total_price"].mean().sort_values()
    growth = monthly_rev.pct_change() * 100

    # KPI 1: Monthly Revenue Performance
    plt.figure(figsize=(10, 5))
    plt.plot(monthly_rev.index.strftime('%Y-%m'), monthly_rev.values, marker='o', color='tab:blue')
    plt.title("KPI 1: Monthly Revenue Performance")
    plt.xticks(rotation=45); plt.tight_layout()
    plt.savefig("output/monthly_revenue.png"); plt.close()

    # KPI 2: Regional Revenue Contribution
    plt.figure(figsize=(8, 6))
    sns.barplot(x=city_rev.values, y=city_rev.index, hue=city_rev.index, legend=False, palette="viridis")
    plt.title("KPI 2: Regional Revenue Contribution")
    plt.tight_layout(); plt.savefig("output/revenue_by_city.png"); plt.close()

    # KPI 3: AOV by Product Category
    plt.figure(figsize=(10, 6))
    sns.barplot(x=cat_aov_mean.index, y=cat_aov_mean.values, hue=cat_aov_mean.index, legend=False, palette="viridis")
    plt.title("KPI 3: AOV by Product Category")
    plt.xticks(rotation=30); plt.tight_layout()
    plt.savefig("output/average_order_value_category.png"); plt.close()

    # KPI 4: Month-over-Month Growth Rate 
    plt.figure(figsize=(10, 5))
    plt.bar(growth.index.strftime('%Y-%m'), growth.fillna(0).values, color='skyblue')
    plt.title("KPI 4: Month-over-Month Growth Rate (%)")
    plt.xticks(rotation=45); plt.tight_layout()
    plt.savefig("output/monthly_growth.png"); plt.close()

    # KPI 5: Revenue Variance per Category
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='category', y='total_price', data=df, palette="Set3")
    plt.title("KPI 5: Revenue Variance per Category")
    plt.xticks(rotation=30); plt.tight_layout()
    plt.savefig("output/revenue_boxplot.png"); plt.close()

def main():
    try:
        engine = connect_db()
        df = extract_data(engine)
        kpis = compute_kpis(df)
        stats_out = run_statistical_tests(df)
        
        print(" SUMMARY STATISTICS ")
        print(f"Total Cleaned Revenue: {kpis['total_revenue']:.2f} JOD")
        
        print("\n--- STATISTICAL VALIDATION ---")
        print(f"ANOVA Category F-stat: {stats_out['ANOVA']['f_stat']:.4f}")
        print(f"ANOVA p-value: {stats_out['ANOVA']['p']:.4f}")
        print(f"T-Test City Cohen's d: {stats_out['T-Test']['d']:.4f}")

        create_visualizations(df)
        print("\nSuccess: 5 Individual KPI charts generated in /output.")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()