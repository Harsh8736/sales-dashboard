"""
Validate — Post-load data quality checks
Run after pipeline.py: python etl/validate.py
"""
import logging, os, sys, sqlite3
from datetime import datetime

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    handlers=[logging.FileHandler("logs/validate.log"), logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)
DB_PATH = "data/sales.db"

CHECKS = [
    ("fact_orders has rows",           "SELECT COUNT(*) FROM fact_orders",                           lambda n: n > 0),
    ("No null sales",                  "SELECT COUNT(*) FROM fact_orders WHERE sales IS NULL",        lambda n: n == 0),
    ("No null order_date",             "SELECT COUNT(*) FROM fact_orders WHERE order_date IS NULL",   lambda n: n == 0),
    ("dim_customers has rows",         "SELECT COUNT(*) FROM dim_customers",                          lambda n: n > 0),
    ("dim_products has rows",          "SELECT COUNT(*) FROM dim_products",                           lambda n: n > 0),
    ("vw_revenue_by_region has rows",  "SELECT COUNT(*) FROM vw_revenue_by_region",                  lambda n: n > 0),
    ("vw_mom_growth has rows",         "SELECT COUNT(*) FROM vw_mom_growth",                          lambda n: n > 0),
    ("vw_top_products has rows",       "SELECT COUNT(*) FROM vw_top_products",                        lambda n: n > 0),
    ("vw_customer_segments has rows",  "SELECT COUNT(*) FROM vw_customer_segments",                   lambda n: n > 0),
    ("Total sales positive",           "SELECT SUM(sales) FROM fact_orders",                          lambda n: n and n > 0),
    ("Row count >= 1000",              "SELECT COUNT(*) FROM fact_orders",                            lambda n: n >= 1000),
]

def run():
    if not os.path.exists(DB_PATH):
        log.error(f"DB not found at {DB_PATH}. Run pipeline.py first.")
        sys.exit(1)
    con = sqlite3.connect(DB_PATH)
    passed = failed = 0
    log.info("=" * 60)
    log.info("Validation started")
    for desc, sql, check in CHECKS:
        try:
            val = con.execute(sql).fetchone()[0]
            ok = check(val)
            log.info(f"  {'PASS' if ok else 'FAIL'}  {desc}  (={val})")
            if ok: passed += 1
            else:  failed += 1
        except Exception as e:
            log.error(f"  ERROR  {desc}: {e}")
            failed += 1
    con.close()
    log.info(f"Validation: {passed} passed, {failed} failed")
    if failed: sys.exit(1)

if __name__ == "__main__":
    run()
