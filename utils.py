"""Utility functions for finance tracking, database operations, and data visualization."""

import logging
import os

import mysql.connector
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sqlalchemy import create_engine

logger = logging.getLogger(__name__)


def calculate_stamp_duty(price):
    """Calculate Stamp Duty Land Tax (SDLT) for a given property price.

    Rates (as of June 2025):
    - 0% on the first £125,000
    - 2% on the next £125,000 (125,001 to 250,000)
    - 5% on the next £675,000 (250,001 to 925,000)
    - 10% on the next £575,000 (925,001 to 1.5 million)
    - 12% on the remaining amount (above 1.5 million)
    """
    bands = [(125000, 0.00), (125000, 0.02), (675000, 0.05), (575000, 0.10), (float("inf"), 0.12)]

    duty = 0
    remaining = price

    for band_limit, rate in bands:
        if remaining <= 0:
            break
        taxable = min(remaining, band_limit)
        duty += taxable * rate
        remaining -= taxable

    return round(duty)


def display_salary(salary, outgoings):
    """Display a stacked bar chart of salary allocation and return the remaining savings."""
    total_outgoings = sum(outgoings.values())
    savings = salary - total_outgoings
    segments = outgoings.copy()
    segments["Remaining"] = savings
    sorted_segments = dict(sorted(segments.items(), key=lambda item: item[1], reverse=True))
    fig = go.Figure()

    colors = [
        "#D8D3C3",
        "#C9D6D5",
        "#E3D5CA",
        "#D6E2E9",
        "#F0E5CF",
        "#B8B8AA",
        "#EAD2AC",
        "#C5C9A4",
        "#E8DFF5",
        "#F6F1D1",
    ]

    for i, (label, amount) in enumerate(sorted_segments.items()):
        fig.add_trace(
            go.Bar(
                y=["Monthly Budget"],
                x=[amount],
                name=label,
                orientation="h",
                marker={"color": colors[i % len(colors)]},
                hovertemplate=f"{label}: £{amount:,.0f}<extra></extra>",
            ),
        )

    # Reduce space and hide axis/grid
    fig.update_layout(
        barmode="stack",
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        height=100,
        xaxis={"showgrid": False, "visible": False},
        yaxis={"showgrid": False, "visible": False},
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": "#F9F7F2"},
        showlegend=False,
    )

    # Display in Streamlit
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    return savings


def connect_sql():
    """Get a connection to the MySQL database and return the cursor and connection."""
    sql_user = os.environ["SQL_USER"]
    sql_pass = os.environ["SQL_PASSWORD"]
    sql_host = os.environ["SQL_HOST"]
    sql_db = os.environ["SQL_DB"]

    config = {"user": sql_user, "password": sql_pass, "host": sql_host, "database": sql_db}

    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()

    return cursor, conn


def run_sql_query(query, commit=False, params=()):
    """Execute a SQL query using a database connection and return the results as a DataFrame."""
    csr, conn = connect_sql()

    with csr as cur:
        cur.execute(query, params)
        if commit:
            conn.commit()
        try:
            data = pd.DataFrame.from_records(iter(cur), columns=[x[0] for x in cur.description])
        except BaseException:
            logger.exception("Something went wrong")
            data = pd.DataFrame()

    return data


def append_sql(data, table, person):
    """Delete existing finance records for a person and append new data to the specified table."""
    query = """
            DELETE FROM personal.finances
            WHERE person = %s
            """
    params = (person,)

    run_sql_query(query, True, params)

    try:
        sql_user = os.environ["SQL_USER"]
        sql_pass = os.environ["SQL_PASSWORD"]
        sql_host = os.environ["SQL_HOST"]
        sql_db = os.environ["SQL_DB"]

        c = f"mysql+mysqlconnector://{sql_user}:{sql_pass}@{sql_host}/{sql_db}"

        engine = create_engine(c)

        data.to_sql(table, engine, if_exists="append", index=False)

        engine.dispose()

    except Exception:
        logger.exception("Something went wrong")
        return False
    else:
        return True


def load_finances():
    """Load all finance records from the database, ordered by person and amount descending."""
    query = """
            SELECT *
            FROM personal.finances
            ORDER BY person, amount DESC
            """
    return run_sql_query(query)


def calculate():
    """Calculate and return financial data and outgoings for Toby and Abby."""
    data = load_finances()
    toby_df = data[data["person"] == "Toby"].reset_index(drop=True)
    toby_outgoings = dict(zip(toby_df["outgoing"], toby_df["amount"], strict=False))
    toby_outgoings["Spending Money"] = float(st.session_state["spending_money"])
    toby_income = 4600

    abby_df = data[data["person"] == "Abby"].reset_index(drop=True)
    abby_outgoings = dict(zip(abby_df["outgoing"], abby_df["amount"], strict=False))
    abby_outgoings["Spending Money"] = float(st.session_state["spending_money"])
    abby_income = 5719

    return toby_df, toby_outgoings, toby_income, abby_df, abby_outgoings, abby_income
