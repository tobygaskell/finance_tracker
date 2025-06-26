"""Streamlit page for inputting and editing Toby's and Abby's outgoings."""

import streamlit as st

import utils

data = utils.load_finances()

# Load initial data
if "toby_df" not in st.session_state:
    st.session_state["toby_df"] = data[data["person"] == "Toby"].reset_index(drop=True)

if "abby_df" not in st.session_state:
    st.session_state["abby_df"] = data[data["person"] == "Abby"].reset_index(drop=True)

left, right = st.columns(2)

# Display data editor for Toby
left.write("Toby's Outgoings")
c = left.container()
toby_df_current = st.session_state["toby_df"]

toby_df_new = left.data_editor(
    toby_df_current,
    hide_index=True,
    use_container_width=True,
    column_order=["outgoing", "amount"],
    column_config={
        "amount": st.column_config.NumberColumn("Amount", format="£%d"),
    },
    num_rows="dynamic",
    height=600,
)

# If save is pressed, update the session state
if left.button("Save", key="save_toby", use_container_width=True):
    st.session_state["toby_df"] = toby_df_new
    toby_df_current = toby_df_new  # Use updated value immediately
    utils.append_sql(toby_df_current, "finances", "Toby")

# Display the current total (updated immediately)
c.caption("Total: £{:,}".format(int(toby_df_current["amount"].sum())))

right.write("abby's Outgoings")
c = right.container()
abby_df_current = st.session_state["abby_df"]

abby_df_new = right.data_editor(
    abby_df_current,
    hide_index=True,
    use_container_width=True,
    column_order=["outgoing", "amount"],
    column_config={
        "amount": st.column_config.NumberColumn("Amount", format="£%d"),
    },
    num_rows="dynamic",
    height=600,
)

# If save is pressed, update the session state
if right.button("Save", key="save_abby", use_container_width=True):
    st.session_state["abby_df"] = abby_df_new
    abby_df_current = abby_df_new  # Use updated value immediately
    utils.append_sql(abby_df_current, "finances", "Abby")

# Display the current total (updated immediately)
c.caption("Total: £{:,}".format(int(abby_df_current["amount"].sum())))
