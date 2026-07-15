import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Page Configuration
st.set_page_config(page_title="Eagle Sons Gujrat - Management System", layout="wide")

# --- DATA STORAGE PATHS (CSV Files) ---
LEDGER_FILE = "ledger_data.csv"
EXPENSES_FILE = "expenses_data.csv"
STOCK_FILE = "stock_data.csv"

# Functions to Load and Save Data
def load_data(file_path, default_cols, is_stock=False):
    if os.path.exists(file_path):
        try:
            return pd.read_csv(file_path)
        except Exception:
            pass
    if is_stock:
        return pd.DataFrame([
            {'Item Name': 'Activator', 'Current Stock': 10.0, 'Unit': 'Liters'},
            {'Item Name': 'Clear Coat', 'Current Stock': 15.0, 'Unit': 'Liters'},
            {'Item Name': 'Thinner', 'Current Stock': 20.0, 'Unit': 'Liters'},
            {'Item Name': 'Hydro Film', 'Current Stock': 50.0, 'Unit': 'Meters'}
        ])
    return pd.DataFrame(columns=default_cols)

def save_data(df, file_path):
    df.to_csv(file_path, index=False)

# --- LOGIN SYSTEM ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Eagle Sons Gujrat - Secure Login")
    st.write("Please enter your credentials to access the management system.")
    
    with st.form("login_form"):
        username = st.text_input("Username", value="asad")
        password = st.text_input("Password", type="password")
        login_btn = st.form_submit_button("Login")
        
        if login_btn:
            if username == "asad" and password == "eagle123":
                st.session_state.logged_in = True
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Incorrect Username or Password!")
else:
    # --- MAIN APPLICATION ---
    st.title("🦅 Eagle Sons Gujrat - Management System")
    st.write("Hydro Dipping & Wood Coating Business Ledger & Stock")
    
    # Sidebar Logout Button
    if st.sidebar.button("🔒 Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # Load Data from CSV files (Persistent Storage)
    if 'parties_ledger' not in st.session_state:
        st.session_state.parties_ledger = load_data(LEDGER_FILE, ['Date', 'Party Name', 'Product/Job Description', 'Total Bill', 'Amount Received', 'Balance'])

    if 'expenses' not in st.session_state:
        st.session_state.expenses = load_data(EXPENSES_FILE, ['Date', 'Expense Category', 'Description', 'Amount'])

    if 'stock' not in st.session_state:
        st.session_state.stock = load_data(STOCK_FILE, [], is_stock=True)

    # Sidebar Navigation
    menu = ["Dashboard", "Billing/Invoices", "Ledger", "Expenses", "Stock Management"]
    choice = st.sidebar.selectbox("Navigation Menu", menu)

    # 1. Dashboard
    if choice == "Dashboard":
        st.header("📊 Business Overview / Summary")
        
        total_billed = st.session_state.parties_ledger['Total Bill'].astype(float).sum() if not st.session_state.parties_ledger.empty else 0.0
        total_received = st.session_state.parties_ledger['Amount Received'].astype(float).sum() if not st.session_state.parties_ledger.empty else 0.0
        pending_receivables = total_billed - total_received
        total_expenses = st.session_state.expenses['Amount'].astype(float).sum() if not st.session_state.expenses.empty else 0.0
        net_profit = total_received - total_expenses
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Billed", f"Rs. {total_billed:,.2f}")
        col2.metric("Total Received", f"Rs. {total_received:,.2f}")
        col3.metric("Pending Receivables", f"Rs. {pending_receivables:,.2f}")
        col4.metric("Total Expenses", f"Rs. {total_expenses:,.2f}")
        
        st.subheader(f"💵 Cash in Hand / Net Profit: Rs. {net_profit:,.2f}")

    # 2. Billing/Invoices
    elif choice == "Billing/Invoices":
        st.header("🧾 Create New Invoice / Bill")
        with st.form("invoice_form"):
            date = st.date_input("Date", datetime.now())
            party_name = st.text_input("Party Name")
            job_desc = st.text_input("Job Description (Hydro Dipping / Wood Coating)")
            total_bill = st.number_input("Total Bill Amount", min_value=0.0, format="%.2f")
            amt_received = st.number_input("Amount Received Now", min_value=0.0, format="%.2f")
            submit = st.form_submit_button("Save Invoice")
            
            if submit and party_name:
                balance = total_bill - amt_received
                new_row = {'Date': date.strftime('%Y-%m-%d'), 'Party Name': party_name, 'Product/Job Description': job_desc, 'Total Bill': total_bill, 'Amount Received': amt_received, 'Balance': balance}
                st.session_state.parties_ledger = pd.concat([st.session_state.parties_ledger, pd.DataFrame([new_row])], ignore_index=True)
                
                # Save to CSV File
                save_data(st.session_state.parties_ledger, LEDGER_FILE)
                st.success("Invoice Saved Successfully!")

    # 3. Ledger
    elif choice == "Ledger":
        st.header("📖 Parties Ledger Accounts")
        if st.session_state.parties_ledger.empty:
            st.info("No ledger records found.")
        else:
            st.dataframe(st.session_state.parties_ledger, use_container_width=True)

    # 4. Expenses
    elif choice == "Expenses":
        st.header("📉 Expense Management")
        with st.form("expense_form"):
            exp_date = st.date_input("Date", datetime.now())
            category = st.selectbox("Category", ["Materials/Chemicals", "Labor/Wages", "Factory Rent & Utilities", "Miscellaneous"])
            desc = st.text_input("Expense Description")
            amount = st.number_input("Amount Paid", min_value=0.0, format="%.2f")
            exp_submit = st.form_submit_button("Save Expense")
            
            if exp_submit and amount > 0:
                new_exp = {'Date': exp_date.strftime('%Y-%m-%d'), 'Expense Category': category, 'Description': desc, 'Amount': amount}
                st.session_state.expenses = pd.concat([st.session_state.expenses, pd.DataFrame([new_exp])], ignore_index=True)
                
                # Save to CSV File
                save_data(st.session_state.expenses, EXPENSES_FILE)
                st.success("Expense Recorded Successfully!")
                
        st.subheader("Recent Expenses Log")
        if not st.session_state.expenses.empty:
            st.dataframe(st.session_state.expenses, use_container_width=True)

    # 5. Stock Management
    elif choice == "Stock Management":
        st.header("📦 Factory Stock / Inventory Management")
        
        # Section 1: Create/Add completely new components
        st.subheader("🆕 Add New Custom Item / Component")
        with st.form("new_item_form"):
            c1, c2, c3 = st.columns([2, 1, 1])
            new_item_name = c1.text_input("Item Name (e.g., Carbon Fiber Film, Red Paint)")
            new_item_unit = c2.selectbox("Unit", ["Liters", "Meters", "Kg", "Nos/Pcs"])
            initial_stock = c3.number_input("Starting Quantity", min_value=0.0, step=1.0)
            create_btn = st.form_submit_button("➕ Add This Item To System")
            
            if create_btn and new_item_name:
                if new_item_name.lower() in st.session_state.stock['Item Name'].str.lower().tolist():
                    st.error("This item already exists in inventory!")
                else:
                    new_item_row = {'Item Name': new_item_name, 'Current Stock': initial_stock, 'Unit': new_item_unit}
                    st.session_state.stock = pd.concat([st.session_state.stock, pd.DataFrame([new_item_row])], ignore_index=True)
                    
                    # Save to CSV File
                    save_data(st.session_state.stock, STOCK_FILE)
                    st.success(f"Successfully added '{new_item_name}' to the inventory list!")
                    st.rerun()

        st.write("---")
        
        # Show Current Stock Table
        st.subheader("📊 Current Stock Status")
        st.dataframe(st.session_state.stock, use_container_width=True, hide_index=True)
        
        st.write("---")
        col1, col2 = st.columns(2)
        
        # Form to Update / Add Stock
        with col1:
            st.subheader("📥 Add / Restock Quantity")
            with st.form("add_stock_form"):
                add_item = st.selectbox("Select Item to Restock", st.session_state.stock['Item Name'].tolist())
                add_qty = st.number_input("Quantity to Add", min_value=0.0, step=1.0)
                add_btn = st.form_submit_button("Update Stock")
                
                if add_btn and add_qty > 0:
                    st.session_state.stock.loc[st.session_state.stock['Item Name'] == add_item, 'Current Stock'] += add_qty
                    
                    # Save to CSV File
                    save_data(st.session_state.stock, STOCK_FILE)
                    st.success(f"{add_qty} added to {add_item}!")
                    st.rerun()

        # Form to Consume Stock
        with col2:
            st.subheader("📤 Use / Consume Stock")
            with st.form("use_stock_form"):
                use_item = st.selectbox("Select Item Used", st.session_state.stock['Item Name'].tolist())
                use_qty = st.number_input("Quantity Used", min_value=0.0, step=1.0)
                use_btn = st.form_submit_button("Record Consumption")
                
                if use_btn and use_qty > 0:
                    current_available = st.session_state.stock.loc[st.session_state.stock['Item Name'] == use_item, 'Current Stock'].values[0]
                    if use_qty <= current_available:
                        st.session_state.stock.loc[st.session_state.stock['Item Name'] == use_item, 'Current Stock'] -= use_qty
                        
                        # Save to CSV File
                        save_data(st.session_state.stock, STOCK_FILE)
                        st.success(f"{use_qty} deducted from {use_item}!")
                        st.rerun()
                    else:
                        st.error("Not enough stock available!")
