import streamlit as st
import pandas as pd
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="Eagle Sons Gujrat - Ledger System", layout="wide")

st.title("🦅 Eagle Sons Gujrat - Ledger & Expense Management")
st.write("Hydro Dipping & Wood Coating Business Ledger")

# Initialize Data Streams using Streamlit Session State so data persists during session
if 'parties_ledger' not in st.session_state:
    st.session_state.parties_ledger = pd.DataFrame(columns=['Date', 'Party Name', 'Product/Job Description', 'Total Bill', 'Amount Received', 'Balance'])

if 'expenses' not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=['Date', 'Expense Category', 'Description', 'Amount'])

# --- SIDEBAR: NAVIGATION ---
menu = st.sidebar.selectbox("سیکشن منتخب کریں", ["ڈیش بورڈ / سمری", "پارٹی لیجر (کھاتہ)", "اخراجات (Expenses)"])

# ----------------- SECTION 1: DASHBOARD -----------------
if menu == "ڈیش بورڈ / سمری":
    st.header("📊 بزنس اوور ویو / سمری")
    
    total_billed = st.session_state.parties_ledger['Total Bill'].sum()
    total_received = st.session_state.parties_ledger['Amount Received'].sum()
    total_receivable_pending = st.session_state.parties_ledger['Balance'].sum()
    total_expenses = st.session_state.expenses['Amount'].sum()
    net_profit = total_received - total_expenses

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("کل بل (Total Billed)", f"Rs. {total_billed:,.2f}")
    col2.metric("کل وصولی (Total Received)", f"Rs. {total_received:,.2f}")
    col3.metric("باقی واجبات (Pending Receivables)", f"Rs. {total_receivable_pending:,.2f}", delta_color="inverse")
    col4.metric("کل اخراجات (Total Expenses)", f"Rs. {total_expenses:,.2f}")
    
    st.subheader(f"💵 موجودہ کیش ان ہینڈ / نیٹ پرافٹ: Rs. {net_profit:,.2f}")

# ----------------- SECTION 2: PARTY LEDGER -----------------
elif menu == "پارٹی لیجر (کھاتہ)":
    st.header("👤 پارٹی کھاتہ اور ریسیویبلز")
    
    # Form to add new transaction
    with st.form("ledger_form", clear_on_submit=True):
        st.subheader("نیا کھاتہ / اینٹری ڈالیں")
        col1, col2, col3 = st.columns(3)
        with col1:
            party_name = st.text_input("پارٹی کا نام (Party Name)")
            job_desc = st.text_input("پروڈکٹ / کام کی تفصیل (Job Description)")
        with col2:
            total_bill = st.number_input("کل بل رقم (Total Bill)", min_value=0.0, step=500.0)
        with col3:
            amount_received = st.number_input("وصول شدہ رقم (Amount Received)", min_value=0.0, step=500.0)
            date_entry = st.date_input("تاریخ", datetime.now())
            
        submit_ledger = st.form_submit_button("کھاتے میں لاگ کریں")
        
        if submit_ledger and party_name:
            balance = total_bill - amount_received
            new_entry = {
                'Date': date_entry.strftime('%Y-%m-%d'),
                'Party Name': party_name,
                'Product/Job Description': job_desc,
                'Total Bill': total_bill,
                'Amount Received': amount_received,
                'Balance': balance
            }
            st.session_state.parties_ledger = pd.concat([st.session_state.parties_ledger, pd.DataFrame([new_entry])], ignore_index=True)
            st.success(f"{party_name} کا ریکارڈ کامیابی سے شامل ہو گیا ہے!")

    # Display Ledger Table
    st.subheader("📋 موجودہ لیجر ریکارڈ")
    if not st.session_state.parties_ledger.empty:
        st.dataframe(st.session_state.parties_ledger, use_container_width=True)
        
        # Filter by Party
        unique_parties = st.session_state.parties_ledger['Party Name'].unique()
        selected_party = st.selectbox("کسی خاص پارٹی کا لیجر دیکھیں:", ["سب"] + list(unique_parties))
        
        if selected_party != "سب":
            filtered_df = st.session_state.parties_ledger[st.session_state.parties_ledger['Party Name'] == selected_party]
            st.write(f"### {selected_party} کا ذاتی کھاتہ")
            st.dataframe(filtered_df, use_container_width=True)
            st.write(f"**کل باقی رقم (Total Payable Balance):** Rs. {filtered_df['Balance'].sum():,.2f}")
    else:
        st.info("ابھی تک کوئی لیجر اینٹری موجود نہیں ہے۔")

# ----------------- SECTION 3: EXPENSES -----------------
elif menu == "اخراجات (Expenses)":
    st.header("📉 فیکٹری و پروڈکٹ اخراجات")
    
    with st.form("expense_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            exp_cat = st.selectbox("خراچ کی قسم (Category)", ["کیمیکل و مٹیریل", "مزدوری / دیہاڑی", "بجلی و یوٹیلیٹی", "متفرق اخراجات"])
            exp_desc = st.text_input("تفصیل (Description)")
        with col2:
            exp_amount = st.number_input("رقم (Amount)", min_value=0.0, step=100.0)
            exp_date = st.date_input("تاریخ", datetime.now())
            
        submit_expense = st.form_submit_button("خرچہ درج کریں")
        
        if submit_expense and exp_amount > 0:
            new_expense = {
                'Date': exp_date.strftime('%Y-%m-%d'),
                'Expense Category': exp_cat,
                'Description': exp_desc,
                'Amount': exp_amount
            }
            st.session_state.expenses = pd.concat([st.session_state.expenses, pd.DataFrame([new_expense])], ignore_index=True)
            st.success("خرچہ کامیابی سے درج کر لیا گیا ہے!")

    st.subheader("📋 کل اخراجات کی لسٹ")
    if not st.session_state.expenses.empty:
        st.dataframe(st.session_state.expenses, use_container_width=True)
        st.write(f"**ٹوٹل اخراجات:** Rs. {st.session_state.expenses['Amount'].sum():,.2f}")
    else:
        st.info("ابھی تک کوئی خرچہ درج نہیں کیا گیا۔")
