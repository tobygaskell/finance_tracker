"""Streamlit page for displaying financial outputs, savings calculations, and house purchase planning."""

import streamlit as st

import utils

if "spending_money" not in st.session_state:
    st.session_state["spending_money"] = 1400

if "prev_spending_money" not in st.session_state:
    st.session_state["prev_spending_money"] = st.session_state["spending_money"]

toby_df, toby_outgoings, toby_income, abby_df, abby_outgoings, abby_income = utils.calculate()

total_toby_outgoings = sum(toby_outgoings.values())
toby_savings = toby_income - total_toby_outgoings

total_abby_outgoings = sum(abby_outgoings.values())
abby_savings = abby_income - total_abby_outgoings

left_to_save = float(toby_savings + abby_savings)


c = st.sidebar.container()
house_price = st.sidebar.number_input(
    "House Price",
    value=750000,
    step=1000,
    help="Enter the house price you are looking to buy",
    icon=":material/home:",
    label_visibility="collapsed",
)

c.write(f"House Price: £{house_price:,.0f}")

c = st.sidebar.container()
savings = st.sidebar.number_input(
    "Amount Saved per Month",
    value=left_to_save,
    help="Enter the amount you save each month towards your house deposit",
    icon=":material/savings:",
    label_visibility="collapsed",
)

c.write(f"Savings per Month: £{savings:,.0f}")

c = st.sidebar.container()
time = st.sidebar.number_input(
    "Time to Save (Months)",
    value=12,
    step=1,
    help="Enter the number of months you plan to save for your house deposit",
    icon=":material/timer:",
    label_visibility="collapsed",
)

c.write(f"Time to Save: {time} months")

c = st.sidebar.container()
equity = st.sidebar.number_input(
    "Equity in Property",
    value=67750,
    step=1000,
    help="Enter the equity you have in your current property (if applicable)",
    icon=":material/account_balance:",
    label_visibility="collapsed",
)

c.write(f"Equity in Property: £{equity:,.0f}")

c = st.sidebar.container()
new_spending_money = st.sidebar.number_input(
    "Spending Money",
    value=1800,
    step=100,
    help="Enter the amount you spend each month on non-essential items",
    icon=":material/currency_pound:",
    label_visibility="collapsed",
)

c.write(
    f"Spending Money: £{st.session_state['spending_money']:,.0f} "
    f"({round(st.session_state['spending_money'] / 30)} per day)",
)

has_changed = new_spending_money != st.session_state["spending_money"]

# Update session state
st.session_state["prev_spending_money"] = st.session_state["spending_money"]
st.session_state["spending_money"] = new_spending_money

if has_changed:
    st.rerun()

st.sidebar.write("Hide Income")
hide = st.sidebar.toggle(
    "Show Income",
    key="show_income",
    help="Toggle to show or hide income details",
    label_visibility="collapsed",
)

toby_df, toby_outgoings, toby_income, abby_df, abby_outgoings, abby_income = utils.calculate()

left, middle, right = st.columns(3)

stamp_duty = utils.calculate_stamp_duty(house_price)

deposit = round(house_price / 10)

total_required = round(stamp_duty + deposit)

left.metric("Stamp Duty", value=f"£{stamp_duty:,}", border=True)

middle.metric("Deposit Amount", value=f"£{deposit:,}", border=True)

right.metric("Total Amount Required", value=f"£{total_required:,}", border=True)

saved = savings * time

total_saved = saved + equity

left.metric(f"Saved ({time} Months)", value=f"£{saved:,}", border=True)

middle.metric("Equity in Property", value=f"£{equity:,}", border=True)

right.metric("Total Amount Saved", value=f"£{total_saved:,}", border=True)


st.sidebar.write("---")

if total_saved >= total_required:
    st.sidebar.success("Congratulations! You have enough savings to buy your house.")
else:
    st.sidebar.error("You do not have enough savings to buy your house yet. Keep saving!")

st.write("---")


left, middle, right = st.columns(3)
left.write("Toby's Financials")

if not hide:
    middle.caption(f"Income: £{toby_income:,}")
    right.caption("Outgoings: £{:,}".format(int(toby_df["amount"].sum())))
else:
    middle.caption("Income: Hidden")
    right.caption("Outgoings: Hidden")


left, right = st.columns([toby_income, abby_income - toby_income])

with left:
    toby_savings = utils.display_salary(toby_income, toby_outgoings)

st.write("---")

left, middle, right = st.columns(3)

left.write("Abby's Financials")

if not hide:
    middle.caption(f"Income: £{abby_income:,}")
    right.caption("Outgoings: £{:,}".format(int(abby_df["amount"].sum())))
else:
    middle.caption("Income: Hidden")
    right.caption("Outgoings: Hidden")


abby_savings = utils.display_salary(abby_income, abby_outgoings)
