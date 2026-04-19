# Power BI Dashboard — Setup Guide

## What you'll build
5 interactive visuals connected live to `data/sales.db`:

| Visual | Type | Data source |
|--------|------|-------------|
| Revenue by Region | Bar / Map | `vw_revenue_by_region` |
| Month-over-Month Growth | Line chart | `vw_mom_growth` |
| Top 50 Products | Horizontal bar | `vw_top_products` |
| Customer Segments | Donut chart | `vw_customer_segments` |
| Orders Over Time | Area chart | `fact_orders` |

---

## Step 1 — Install the SQLite ODBC driver

Power BI connects to SQLite via ODBC.

1. Go to: https://www.ch-werner.de/sqliteodbc/
2. Download **sqliteodbc_w64.exe** (64-bit)
3. Run the installer (just click Next → Finish)

---

## Step 2 — Connect Power BI to sales.db

1. Open **Power BI Desktop**
2. Click **Get Data** → search `ODBC` → click **Connect**
3. In the DSN dropdown choose **SQLite3 Datasource**
4. Click **Advanced options** and enter the connection string:

```
Database=C:\YOUR\FULL\PATH\TO\sales-dashboard\data\sales.db
```

> ⚠️ Replace the path with the actual location on your computer.  
> Example: `Database=C:\Users\YourName\Desktop\sales-dashboard\data\sales.db`

5. Click **OK** → Power BI will show a Navigator pane

---

## Step 3 — Load the tables

In the Navigator, tick these tables/views:
- ✅ `fact_orders`
- ✅ `dim_customers`
- ✅ `dim_products`
- ✅ `vw_revenue_by_region`
- ✅ `vw_mom_growth`
- ✅ `vw_top_products`
- ✅ `vw_customer_segments`

Click **Load** (not Transform — the pipeline already cleaned the data).

---

## Step 4 — Build the 5 visuals

### Visual 1 — Revenue by Region (Clustered Bar)
- **Visualization**: Clustered bar chart
- **X-axis**: `vw_revenue_by_region[region]`
- **Y-axis**: `vw_revenue_by_region[total_sales]`
- Add `total_profit` as a second measure (different color)

### Visual 2 — Month-over-Month Revenue (Line Chart)
- **Visualization**: Line chart
- **X-axis**: `vw_mom_growth[year_month]`
- **Y-axis**: `vw_mom_growth[monthly_sales]`
- Optional: add `monthly_profit` as a second line

### Visual 3 — Top Products (Horizontal Bar)
- **Visualization**: Bar chart (horizontal)
- **Y-axis**: `vw_top_products[product_name]`
- **X-axis**: `vw_top_products[total_sales]`
- Sort descending by total_sales

### Visual 4 — Customer Segments (Donut)
- **Visualization**: Donut chart
- **Legend**: `vw_customer_segments[segment]`
- **Values**: `vw_customer_segments[total_sales]`

### Visual 5 — Orders Over Time (Area Chart)
- **Visualization**: Area chart
- **X-axis**: `fact_orders[order_date]` (set to Month hierarchy)
- **Y-axis**: Count of `order_id`

---

## Step 5 — Add slicers (filters)

Add these slicers to the top of your dashboard page:
- **Region** slicer → `fact_orders[region]`
- **Category** slicer → `fact_orders[category]`
- **Year** slicer → `fact_orders[year]`

---

## Step 6 — Export / Share

- **Export to PDF**: File → Export → Export to PDF
- **Publish to web**: File → Publish → Publish to Power BI (requires free Power BI account)
- **Schedule refresh**: Set up in Power BI Service after publishing

---

## Refreshing data

After the pipeline runs (manually or via GitHub Actions):
1. The `data/sales.db` file is updated
2. In Power BI Desktop: click **Refresh** in the Home ribbon
3. All visuals update automatically

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| ODBC driver not found | Re-install sqliteodbc_w64.exe from the link above |
| Path error on connect | Use full absolute path, no trailing slash |
| Blank visuals | Run `python etl/pipeline.py` first to generate the DB |
| Column not found | Column names are lowercase with underscores — check spelling |
