import streamlit as st
import pandas as pd
from datetime import date, datetime
import io

st.set_page_config(page_title="Milk Supply Management 🥛", layout="wide")

st.title("🥛 Milk Supply Management App")
st.write("Manage daily milk supply, calculate monthly totals & generate reports.")

# ------------------------------
# Initialize Session State
# ------------------------------
if "customers" not in st.session_state:
    st.session_state.customers = {}  # {customer_name: rate}

if "records" not in st.session_state:
    st.session_state.records = pd.DataFrame(
        columns=["Date", "Customer", "Quantity (Litre)", "Rate", "Amount"]
    )

# ------------------------------
# Section 1: Customer Management
# ------------------------------
st.sidebar.header("👤 Customer Management")

add_name = st.sidebar.text_input("Customer Name")
add_rate = st.sidebar.number_input("Rate per Litre (₹)", min_value=0.0, step=0.5)

if st.sidebar.button("Add / Update Customer"):
    if add_name:
        st.session_state.customers[add_name] = add_rate
        st.sidebar.success(f"Saved {add_name} at ₹{add_rate}/Litre.")
    else:
        st.sidebar.warning("Please enter a customer name.")

if st.sidebar.button("View All Customers"):
    if st.session_state.customers:
        st.sidebar.write(pd.DataFrame.from_dict(st.session_state.customers, orient="index", columns=["Rate (₹/L)"]))
    else:
        st.sidebar.info("No customers added yet.")

# ------------------------------
# Section 2: Daily Entry
# ------------------------------
st.header("📅 Daily Milk Entry")

if not st.session_state.customers:
    st.warning("Please add customers first from the sidebar.")
else:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        entry_date = st.date_input("Date", date.today())
    with col2:
        customer = st.selectbox("Select Customer", list(st.session_state.customers.keys()))
    with col3:
        quantity = st.number_input("Quantity (in Litres)", min_value=0.0, step=0.1)
    with col4:
        rate = st.session_state.customers[customer]

    if st.button("Add Entry"):
        amount = quantity * rate
        new_row = pd.DataFrame(
            [[entry_date, customer, quantity, rate, amount]],
            columns=["Date", "Customer", "Quantity (Litre)", "Rate", "Amount"],
        )
        st.session_state.records = pd.concat([st.session_state.records, new_row], ignore_index=True)
        st.success(f"Added record for {customer} on {entry_date} ✅")

# ------------------------------
# Section 3: View All Records
# ------------------------------
st.subheader("📋 All Records")
st.dataframe(st.session_state.records, use_container_width=True)

# ------------------------------
# Section 4: Monthly Summary
# ------------------------------
if not st.session_state.records.empty:
    st.subheader("📆 Monthly Summary")
    st.session_state.records["Month"] = pd.to_datetime(st.session_state.records["Date"]).dt.to_period("M")
    current_month = datetime.now().strftime("%Y-%m")
    monthly_data = st.session_state.records[
        st.session_state.records["Month"] == current_month
    ]

    summary = (
        monthly_data.groupby("Customer")
        .agg({"Quantity (Litre)": "sum", "Amount": "sum"})
        .reset_index()
    )

    st.table(summary.style.format({"Quantity (Litre)": "{:.2f}", "Amount": "₹{:.2f}"}))

    # ------------------------------
    # Section 5: Download Report
    # ------------------------------
    st.subheader("⬇️ Download Monthly Report")
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        st.session_state.records.to_excel(writer, index=False, sheet_name="All Records")
        summary.to_excel(writer, index=False, sheet_name="Monthly Summary")
        writer.close()

    st.download_button(
        label="📤 Download Excel Report",
        data=buffer,
        file_name=f"milk_report_{current_month}.xlsx",
        mime="application/vnd.ms-excel",
    )

else:
    st.info("No records yet! Add daily entries above to view summary.")