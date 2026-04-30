import pytest
import sqlite3
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from etl.pipeline import run_pipeline

def test_csv_loads():
    df = pd.read_csv("data/superstore.csv", encoding="latin1")
    assert len(df) > 0

def test_csv_has_expected_columns():
    df = pd.read_csv("data/superstore.csv", encoding="latin1")
    assert "Sales" in df.columns

def test_no_null_sales():
    df = pd.read_csv("data/superstore.csv", encoding="latin1")
    assert df["Sales"].isnull().sum() == 0

def test_sales_are_positive():
    df = pd.read_csv("data/superstore.csv", encoding="latin1")
    assert (df["Sales"] >= 0).all()

def test_database_created():
    run_pipeline()
    assert os.path.exists("data/sales.db")

def test_database_has_rows():
    conn = sqlite3.connect("data/sales.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM sales")
    count = cursor.fetchone()[0]
    conn.close()
    assert count > 0

def test_row_count_matches():
    df = pd.read_csv("data/superstore.csv", encoding="latin1")
    conn = sqlite3.connect("data/sales.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM sales")
    count = cursor.fetchone()[0]
    conn.close()
    assert count == len(df)