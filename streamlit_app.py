import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import sys

# Add current directory to path so services can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.database import get_connection, init_db
from services.auth_service import login, get_all_users, get_login_activity, signup, update_user, delete_user
from services.exporter import generate_enterprise_report
from services.ai_engine import predict_future_balance, get_spending_insights, analyze_fraud
from utils import COLORS

# --- Configuration & Setup ---
st.set_page_config(
    page_title="Nexus Bank Analytics",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Database
init_db()

# --- Session State Management ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'demo_mode' not in st.session_state:
    st.session_state.demo_mode = False

def do_login(username, password):
    success, result = login(username, password, device_info="Streamlit Web", ip_address="127.0.0.1")
    if success:
        st.session_state.logged_in = True
        st.session_state.user = result
        st.session_state.demo_mode = False
        st.rerun()
    else:
        st.error(result)

def do_demo_login():
    st.session_state.logged_in = True
    st.session_state.demo_mode = True
    st.session_state.user = {
        "id": 0,
        "username": "demo_viewer",
        "role": "VIEWER",
        "full_name": "Public Demo User"
    }
    st.rerun()

def do_logout():
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.demo_mode = False
    st.rerun()

# --- Data Fetching ---
@st.cache_data(ttl=60)
def load_transactions():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM transactions ORDER BY date DESC", conn)
    conn.close()
    return df

# --- UI Components ---
def login_page():
    st.markdown("<h1 style='text-align: center; color: #0EA5E9;'>Nexus Bank Analytics</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Secure Login Portal</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.container(border=True):
            st.subheader("Login")
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Secure Login", use_container_width=True, type="primary"):
                    if username and password:
                        do_login(username, password)
                    else:
                        st.warning("Please enter username and password.")
            with c2:
                if st.button("Demo Mode (Public Access)", use_container_width=True):
                    do_demo_login()
                    
            st.markdown("---")
            st.caption("Admin defaults: admin / admin123")

def render_sidebar():
    with st.sidebar:
        st.markdown(f"## 🏦 Nexus Bank")
        st.markdown(f"**Welcome, {st.session_state.user['full_name']}**")
        st.caption(f"Role: {st.session_state.user['role']}")
        st.markdown("---")
        
        pages = ["Overview", "Transactions", "AI Insights", "Reports", "Analytics"]
        if st.session_state.user['role'] == 'ADMIN':
            pages.append("Admin Panel")
            
        selected_page = st.radio("Navigation", pages, label_visibility="collapsed")
        
        st.markdown("---")
        if st.button("Logout", use_container_width=True):
            do_logout()
            
        return selected_page

def page_overview(df):
    st.title("Dashboard Overview")
    
    if df.empty:
        st.info("No transaction data available yet.")
        return
        
    # KPIs
    current_balance = df['balance'].iloc[0] if not df.empty else 0
    total_inflow = df[df['type'] == 'Deposit']['amount'].sum()
    total_outflow = df[df['type'] == 'Withdrawal']['amount'].sum()
    fraud_count = len(analyze_fraud(df))
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Liquid Balance", f"₹{current_balance:,.2f}")
    with col2:
        st.metric("Total Inflow", f"₹{total_inflow:,.2f}", delta_color="normal")
    with col3:
        st.metric("Total Outflow", f"₹{total_outflow:,.2f}", delta="-", delta_color="inverse")
    with col4:
        st.metric("Active Alerts", fraud_count, delta="Fraud Flags", delta_color="inverse")

    st.markdown("### Balance History")
    # Balance trend line chart
    df_chart = df.copy()
    df_chart['date'] = pd.to_datetime(df_chart['date'])
    df_chart = df_chart.sort_values('date')
    
    fig = px.line(
        df_chart, 
        x='date', 
        y='balance', 
        title="Balance Over Time",
        color_discrete_sequence=[COLORS['accent']]
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=COLORS['text'])
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Recent Transactions")
    recent = df.head(5)[['date', 'acc_no', 'type', 'amount', 'balance', 'status']]
    st.dataframe(recent, use_container_width=True, hide_index=True)

def page_transactions(df):
    st.title("Transaction Ledger")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        search_query = st.text_input("Search Account No. or Bank")
    with col2:
        type_filter = st.selectbox("Transaction Type", ["All", "Deposit", "Withdrawal"])
    with col3:
        banks = ["All"] + list(df['bank'].unique()) if not df.empty else ["All"]
        bank_filter = st.selectbox("Filter by Bank", banks)

    filtered_df = df.copy()
    
    if search_query:
        filtered_df = filtered_df[
            filtered_df['acc_no'].str.contains(search_query, case=False) |
            filtered_df['bank'].str.contains(search_query, case=False)
        ]
    if type_filter != "All":
        filtered_df = filtered_df[filtered_df['type'] == type_filter]
    if bank_filter != "All":
        filtered_df = filtered_df[filtered_df['bank'] == bank_filter]

    st.markdown(f"**Showing {len(filtered_df)} records**")

    # Highlighting fraud rows in red
    def highlight_fraud(row):
        if row['amount'] > 15000 and row['type'] == 'Withdrawal':
             return ['background-color: rgba(239, 68, 68, 0.2)'] * len(row)
        return [''] * len(row)

    if not filtered_df.empty:
        st.dataframe(
            filtered_df.style.apply(highlight_fraud, axis=1),
            use_container_width=True,
            height=500,
            hide_index=True
        )
    else:
        st.info("No transactions match the current filters.")

def page_ai_insights(df):
    st.title("AI Intelligence Engine")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Fraud Detection Analysis")
        fraud_indices = analyze_fraud(df)
        if fraud_indices:
            fraud_df = df.loc[fraud_indices]
            st.error(f"⚠️ {len(fraud_indices)} High-Risk Transactions Detected!")
            st.dataframe(fraud_df[['date', 'acc_no', 'amount', 'bank', 'type']], use_container_width=True, hide_index=True)
        else:
            st.success("✅ No suspicious activity detected. All transactions appear normal.")
            
        st.markdown("---")
        st.subheader("Spending Insights")
        insight = get_spending_insights(df)
        st.info(f"💡 {insight}")

    with col2:
        with st.container(border=True):
            st.subheader("Predictive Analytics")
            forecast = predict_future_balance(df)
            st.metric("30-Day Liquid Forecast", f"₹{forecast:,.2f}")
            st.caption("Based on historical transaction patterns and average run rate.")

def page_reports(df):
    st.title("Enterprise Reports")
    st.write("Generate and download comprehensive banking reports.")
    
    col1, col2, col3 = st.columns(3)
    
    def generate_and_download(format_type):
        with st.spinner(f"Generating {format_type} report..."):
            success, filename = generate_enterprise_report(format=format_type)
            if success and os.path.exists(filename):
                st.success(f"Successfully generated {format_type}!")
                with open(filename, "rb") as f:
                    st.download_button(
                        label=f"⬇️ Download {format_type}",
                        data=f,
                        file_name=os.path.basename(filename),
                        mime="application/octet-stream"
                    )
            else:
                st.error(f"Failed to generate {format_type} report. Check logs.")

    with col1:
        with st.container(border=True):
            st.markdown("### PDF Report")
            st.caption("Rich executive summary with AI insights.")
            if st.button("Generate PDF", use_container_width=True):
                generate_and_download("PDF")

    with col2:
        with st.container(border=True):
            st.markdown("### CSV Export")
            st.caption("Raw data extract for system integration.")
            if st.button("Generate CSV", use_container_width=True):
                generate_and_download("CSV")

    with col3:
        with st.container(border=True):
            st.markdown("### Excel Report")
            st.caption("Formatted spreadsheet for analysts.")
            if st.button("Generate Excel", use_container_width=True):
                generate_and_download("Excel")

def page_analytics(df):
    st.title("Advanced Analytics")
    
    if df.empty:
        st.warning("Insufficient data for analytics.")
        return
        
    col1, col2 = st.columns(2)
    
    with col1:
        # Inflow vs Outflow Donut
        type_summary = df.groupby('type')['amount'].sum().reset_index()
        fig_donut = px.pie(
            type_summary, 
            values='amount', 
            names='type', 
            hole=0.5,
            title="Volume Distribution by Type",
            color='type',
            color_discrete_map={'Deposit': COLORS['success'], 'Withdrawal': COLORS['danger']}
        )
        fig_donut.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(color=COLORS['text']))
        st.plotly_chart(fig_donut, use_container_width=True)

    with col2:
        # Bank Distribution Bar Chart
        bank_summary = df.groupby('bank')['amount'].sum().reset_index()
        fig_bar = px.bar(
            bank_summary, 
            x='bank', 
            y='amount', 
            title="Total Transaction Volume by Bank",
            color='amount',
            color_continuous_scale="Blues"
        )
        fig_bar.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(color=COLORS['text']))
        st.plotly_chart(fig_bar, use_container_width=True)

def page_admin():
    st.title("Admin Control Panel")
    
    tab1, tab2 = st.tabs(["User Management", "System Audit Logs"])
    
    with tab1:
        st.subheader("System Users")
        users = get_all_users()
        user_df = pd.DataFrame(users, columns=['ID', 'Username', 'Full Name', 'Email', 'Role', 'Status', 'Created At', 'Last Login'])
        st.dataframe(user_df, use_container_width=True, hide_index=True)
        
        st.markdown("### Add New User")
        with st.form("new_user_form"):
            c1, c2 = st.columns(2)
            new_user = c1.text_input("Username")
            new_pass = c1.text_input("Password", type="password")
            new_name = c2.text_input("Full Name")
            new_role = c2.selectbox("Role", ["ANALYST", "ADMIN", "VIEWER"])
            submitted = st.form_submit_button("Create User")
            
            if submitted:
                if new_user and new_pass and new_name:
                    success, msg = signup(new_user, new_pass, new_name, role=new_role)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.warning("Please fill all fields.")
    
    with tab2:
        st.subheader("Login Activity")
        logs = get_login_activity(100)
        log_df = pd.DataFrame(logs, columns=['Log ID', 'Username', 'Timestamp', 'Status', 'IP', 'Device'])
        st.dataframe(log_df, use_container_width=True, hide_index=True)

# --- Main Application Loop ---
if not st.session_state.logged_in:
    login_page()
else:
    df_trans = load_transactions()
    selected = render_sidebar()
    
    if selected == "Overview":
        page_overview(df_trans)
    elif selected == "Transactions":
        page_transactions(df_trans)
    elif selected == "AI Insights":
        page_ai_insights(df_trans)
    elif selected == "Reports":
        page_reports(df_trans)
    elif selected == "Analytics":
        page_analytics(df_trans)
    elif selected == "Admin Panel":
        if st.session_state.user.get('role') == 'ADMIN':
            page_admin()
        else:
            st.error("Unauthorized access. Admin privileges required.")
