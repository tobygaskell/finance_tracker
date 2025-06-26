"""Main entry point for the finance tracker Streamlit app.

This module sets up the page configuration and navigation for the finance tracker application.
"""

import streamlit as st

st.set_page_config(
    page_title="Streamlit Navigation Example",
    page_icon=":material/currency_pound:",
    layout="wide",
    menu_items=None,
)


pages = {
    "pages": [
        st.Page("pages/output.py", title="Budget Tracker", icon=":material/paid:"),
        st.Page("pages/input.py", title="Edit Outgoings", icon=":material/draw:"),
    ],
}

pg = st.navigation(
    pages,
    position="top",
)

pg.run()
