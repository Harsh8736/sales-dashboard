# Sales Dashboard

An automated ETL pipeline + Power BI dashboard built on the Superstore dataset.

## Architecture

```
Raw CSV (Superstore)
        │
        ▼
[ etl/pipeline.py ]  ◄── GitHub Actions cron (daily 2AM UTC)
  Extract → Transform → Load
        │
        ▼
[ data/sales.db ]  (SQLite)
  ├── dim_customers
  ├── dim_products
  ├── fact_orders
  └── SQL Views:
        ├── vw_revenue_by_region
        ├── vw_mom_growth
        ├── vw_top_products
        └── vw_customer_segments
        │
        ▼
[ etl/validate.py ]
  Schema → Null check → Row count → Sanity check
        │
        ▼
[ Power BI Desktop ]
  Connected to sales.db via ODBC
  5 interactive visuals → exported to PDF / shared
```

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Add the data
Download the Superstore CSV and save it as `data/superstore.csv`.  
(Search "Superstore dataset CSV" on Kaggle — free download.)

### 3. Run the pipeline
```bash
python etl/pipeline.py
```

### 4. Validate the data
```bash
python etl/validate.py
```

### 5. Open Power BI
See `powerbi/dashboard_guide.md` for full connection instructions.

## Project Structure

```
sales-dashboard/
├── .github/
│   └── workflows/
│       └── daily_etl.yml       # GitHub Actions — daily cron job
├── etl/
│   ├── pipeline.py             # Extract → Transform → Load
│   └── validate.py             # Post-load data quality checks
├── data/
│   └── superstore.csv          # Source dataset (not committed to git)
├── logs/                       # Auto-generated pipeline & validation logs
├── powerbi/
│   └── dashboard_guide.md      # Power BI connection & setup instructions
├── requirements.txt
├── .gitignore
└── README.md
```

## Automation

The pipeline runs automatically every day at **2:00 AM UTC** via GitHub Actions.  
You can also trigger it manually from the Actions tab in your GitHub repository.

## Tables & Views

| Name | Type | Description |
|------|------|-------------|
| `fact_orders` | Table | All orders with sales, profit, dates |
| `dim_customers` | Table | Customer names and segments |
| `dim_products` | Table | Product names, categories |
| `dim_geography` | Table | City, state, region, country |
| `vw_revenue_by_region` | View | Total sales & profit per region |
| `vw_mom_growth` | View | Monthly sales trend |
| `vw_top_products` | View | Top 50 products by revenue |
| `vw_customer_segments` | View | Sales breakdown by customer segment |
