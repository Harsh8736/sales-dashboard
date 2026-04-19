"""
ETL Pipeline — Superstore Sales Dashboard
Reads superstore.csv -> transforms -> loads into sales.db (SQLite)

Dependencies: pandas only  (pip install pandas)
Run: python etl/pipeline.py
"""

import logging
import os
import sqlite3
import sys
from datetime import datetime

import pandas as pd

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    handlers=[
        logging.FileHandler("logs/pipeline.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)


def extract(path="data/superstore.csv"):
    log.info(f"Extracting from {path}")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"'{path}' not found.\n"
            "Download the Superstore CSV from Kaggle and save it as data/superstore.csv"
        )
    df = pd.read_csv(path, encoding="latin1")
    df.columns = (
        df.columns.str.strip().str.lower()
        .str.replace(r"[\s\-/]", "_", regex=True)
    )
    log.info(f"Extracted {len(df):,} rows, {len(df.columns)} columns")
    return df


def transform(df):
    log.info("Transforming data")
    for col in ["order_date", "ship_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], dayfirst=False, errors="coerce")

    if "order_date" in df.columns:
        df["year"]       = df["order_date"].dt.year.astype("Int64")
        df["month"]      = df["order_date"].dt.month.astype("Int64")
        df["year_month"] = df["order_date"].dt.to_period("M").astype(str)
        df["order_date"] = df["order_date"].dt.strftime("%Y-%m-%d")
    if "ship_date" in df.columns:
        df["ship_date"]  = df["ship_date"].dt.strftime("%Y-%m-%d")

    for col in ["sales", "quantity", "discount", "profit"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    cust_cols = [c for c in ["customer_id","customer_name","segment"] if c in df.columns]
    dim_customers = df[cust_cols].drop_duplicates().reset_index(drop=True)

    prod_cols = [c for c in ["product_id","product_name","category","sub_category"] if c in df.columns]
    dim_products = df[prod_cols].drop_duplicates().reset_index(drop=True)

    geo_cols = [c for c in ["postal_code","city","state","region","country"] if c in df.columns]
    dim_geography = df[geo_cols].drop_duplicates().reset_index(drop=True)

    log.info(f"Transformed -> customers:{len(dim_customers):,}  products:{len(dim_products):,}  orders:{len(df):,}")
    return df, dim_customers, dim_products, dim_geography


def load(fact_orders, dim_customers, dim_products, dim_geography, db_path="data/sales.db"):
    log.info(f"Loading into {db_path}")
    os.makedirs("data", exist_ok=True)
    con = sqlite3.connect(db_path)

    fact_orders.to_sql("fact_orders",     con, if_exists="replace", index=False)
    dim_customers.to_sql("dim_customers", con, if_exists="replace", index=False)
    dim_products.to_sql("dim_products",   con, if_exists="replace", index=False)
    dim_geography.to_sql("dim_geography", con, if_exists="replace", index=False)
    log.info("Tables written")

    views = {
        "vw_revenue_by_region": """
            SELECT region,
                ROUND(SUM(sales),2) AS total_sales,
                ROUND(SUM(profit),2) AS total_profit,
                COUNT(DISTINCT order_id) AS order_count
            FROM fact_orders GROUP BY region ORDER BY total_sales DESC""",

        "vw_mom_growth": """
            SELECT year_month,
                ROUND(SUM(sales),2) AS monthly_sales,
                ROUND(SUM(profit),2) AS monthly_profit,
                COUNT(DISTINCT order_id) AS orders
            FROM fact_orders GROUP BY year_month ORDER BY year_month""",

        "vw_top_products": """
            SELECT f.product_name, p.category, p.sub_category,
                ROUND(SUM(f.sales),2) AS total_sales,
                ROUND(SUM(f.profit),2) AS total_profit,
                SUM(f.quantity) AS units_sold
            FROM fact_orders f LEFT JOIN dim_products p USING(product_name)
            GROUP BY f.product_name ORDER BY total_sales DESC LIMIT 50""",

        "vw_customer_segments": """
            SELECT segment,
                COUNT(DISTINCT customer_id) AS customer_count,
                ROUND(SUM(sales),2) AS total_sales,
                ROUND(AVG(sales),2) AS avg_order_value,
                ROUND(SUM(profit),2) AS total_profit
            FROM fact_orders GROUP BY segment""",
    }

    cur = con.cursor()
    for name, sql in views.items():
        cur.execute(f"DROP VIEW IF EXISTS {name}")
        cur.execute(f"CREATE VIEW {name} AS {sql}")
        log.info(f"  View created: {name}")
    con.commit()
    con.close()
    log.info("Load complete")


def run():
    start = datetime.now()
    log.info("=" * 60)
    log.info("Pipeline started")
    try:
        df = extract()
        fact_orders, dim_customers, dim_products, dim_geography = transform(df)
        load(fact_orders, dim_customers, dim_products, dim_geography)
        con = sqlite3.connect("data/sales.db")
        for v in ["vw_revenue_by_region","vw_top_products"]:
            n = con.execute(f"SELECT COUNT(*) FROM {v}").fetchone()[0]
            log.info(f"  {v}: {n} rows")
        con.close()
        log.info(f"Pipeline done in {(datetime.now()-start).total_seconds():.1f}s")
    except Exception as e:
        log.error(f"FAILED: {e}")
        raise

if __name__ == "__main__":
    run()
