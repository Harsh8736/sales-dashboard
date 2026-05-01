import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="📊",
    layout="wide"
)

@st.cache_data
def load_data():
    conn = sqlite3.connect("data/sales.db")
    revenue     = pd.read_sql("SELECT * FROM vw_revenue_by_region", conn)
    top_products = pd.read_sql("SELECT * FROM vw_top_products", conn)
    mom_growth  = pd.read_sql("SELECT * FROM vw_mom_growth", conn)
    segments    = pd.read_sql("SELECT * FROM vw_customer_segments", conn)
    conn.close()
    return revenue, top_products, mom_growth, segments

revenue, top_products, mom_growth, segments = load_data()

st.title("📊 Sales Dashboard")
st.caption("Powered by Superstore data · Automated ETL pipeline · Docker + CI/CD")

st.divider()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Sales",    f"${revenue['total_sales'].sum():,.0f}")
col2.metric("Total Profit",   f"${revenue['total_profit'].sum():,.0f}")
col3.metric("Total Orders",   f"{revenue['order_count'].sum():,}")
col4.metric("Regions",        f"{len(revenue)}")

st.divider()

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Revenue by Region")
    fig = px.bar(
        revenue.sort_values("total_sales", ascending=True),
        x="total_sales", y="region",
        orientation="h",
        color="total_profit",
        color_continuous_scale="teal",
        labels={"total_sales": "Total Sales ($)", "region": "Region"}
    )
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("Customer Segments")
    fig2 = px.pie(
        segments,
        values="total_sales",
        names="segment",
        color_discrete_sequence=px.colors.sequential.Teal
    )
    fig2.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("Monthly Sales Trend")
fig3 = px.line(
    mom_growth,
    x="year_month",
    y="monthly_sales",
    markers=True,
    labels={"year_month": "Month", "monthly_sales": "Sales ($)"}
)
fig3.update_traces(line_color="#1D9E75", line_width=2)
fig3.update_layout(margin=dict(l=0, r=0, t=0, b=0))
st.plotly_chart(fig3, use_container_width=True)

st.subheader("Top 10 Products by Sales")
fig4 = px.bar(
    top_products.head(10).sort_values("total_sales", ascending=True),
    x="total_sales",
    y="product_name",
    orientation="h",
    color="category",
    labels={"total_sales": "Total Sales ($)", "product_name": "Product"}
)
fig4.update_layout(margin=dict(l=0, r=0, t=0, b=0))
st.plotly_chart(fig4, use_container_width=True)

st.divider()
st.caption("Built by Harsh · ETL pipeline automated with Docker + GitHub Actions CI/CD")