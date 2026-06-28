import streamlit as st
import pandas as pd
import numpy as np
import os
import sys

st.set_page_config(
    page_title="Attribo - Marketing Attribution Engine",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .main {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at 80% 10%, #1e1b4b 0%, #030712 70%) !important;
        color: #f3f4f6 !important;
    }
    
    .main {
        background-color: transparent !important;
        color: #f3f4f6 !important;
    }
    
    [data-testid="stHeader"] {
        background-color: transparent !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: rgba(11, 15, 25, 0.8) !important;
        backdrop-filter: blur(12px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    [data-testid="stSidebarNavHeader"], 
    div[data-testid="stSidebarNavItems"] > div > span {
        font-size: 0.7rem !important;
        font-weight: 700 !important;
        color: #8b5cf6 !important; 
        text-transform: uppercase !important;
        letter-spacing: 0.12em !important;
        padding: 24px 0 8px 16px !important;
        display: block;
    }
    
    [data-testid="stSidebarNavItems"] a, 
    div[data-testid="stSidebarNavItems"] ul li a {
        border-radius: 8px !important;
        margin: 4px 12px !important;
        padding: 10px 14px !important;
        color: #94a3b8 !important; 
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        text-decoration: none !important;
        display: flex !important;
        align-items: center !important;
    }
    
    [data-testid="stSidebarNavItems"] a:hover, 
    div[data-testid="stSidebarNavItems"] ul li a:hover {
        background: rgba(255, 255, 255, 0.03) !important;
        color: #fafafa !important; 
        padding-left: 18px !important;
    }
    
    [data-testid="stSidebarNavItems"] a[aria-current="page"], 
    div[data-testid="stSidebarNavItems"] ul li a[aria-current="page"] {
        background: rgba(139, 92, 246, 0.15) !important;
        color: #c084fc !important; 
        font-weight: 600 !important;
        border-left: 3px solid #8b5cf6 !important;
        padding-left: 14px !important;
    }
    
    [data-testid="stSidebar"] .stNumberInput, 
    [data-testid="stSidebar"] .stSlider {
        background: rgba(15, 23, 42, 0.4) !important;
        padding: 12px !important;
        border-radius: 8px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        margin-bottom: 12px !important;
    }
    
    /* Clean Premium Glass Metric Cards */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.4) 0%, rgba(30, 27, 75, 0.2) 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-top: 3px solid #8b5cf6 !important;
        border-radius: 12px !important;
        padding: 20px 16px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25) !important;
    }
    
    div[data-testid="stMetric"]:hover {
        border-color: rgba(139, 92, 246, 0.4) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 30px rgba(139, 92, 246, 0.18) !important;
    }
    
    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 2.1rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.03em !important;
        margin-top: 4px !important;
        text-shadow: 0 0 12px rgba(255, 255, 255, 0.1);
    }
    
    div[data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-weight: 650 !important;
        letter-spacing: -0.025em !important;
    }
    
    /* Matte Gradient buttons */
    div.stButton > button {
        background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 22px !important;
        font-size: 0.9rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 14px rgba(139, 92, 246, 0.3) !important;
    }
    
    div.stButton > button:hover {
        background: linear-gradient(135deg, #a78bfa 0%, #818cf8 100%) !important;
        box-shadow: 0 6px 20px rgba(139, 92, 246, 0.4) !important;
        transform: translateY(-1px) !important;
    }
    
    div.stButton > button:active {
        transform: translateY(1px) !important;
    }
 
    /* Style selectboxes and text inputs */
    .stTextInput input, .stSelectbox [data-baseweb="select"], .stMultiSelect [data-baseweb="select"], .stNumberInput input {
        background-color: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 8px !important;
        color: #f3f4f6 !important;
        padding: 4px 10px !important;
        font-size: 0.9rem !important;
        transition: all 0.2s ease !important;
    }
    .stTextInput input:focus, .stSelectbox [data-baseweb="select"]:focus, .stMultiSelect [data-baseweb="select"]:focus, .stNumberInput input:focus {
        border-color: #8b5cf6 !important;
        box-shadow: 0 0 10px rgba(139, 92, 246, 0.15) !important;
    }
    .stSelectbox [data-baseweb="select"]:hover, .stMultiSelect [data-baseweb="select"]:hover {
        border-color: rgba(139, 92, 246, 0.3) !important;
    }
    
    /* Alerts customization */
    div[data-testid="stAlert"] {
        background: rgba(15, 23, 42, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 10px !important;
        backdrop-filter: blur(6px) !important;
    }
    
    .highlight-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.4) 0%, rgba(15, 23, 42, 0.4) 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-left: 4px solid #8b5cf6 !important;
        border-radius: 12px !important;
        padding: 24px !important;
        margin: 24px 0 !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2) !important;
    }
    
    .highlight-card h3 {
        color: #c084fc !important;
        font-weight: 700 !important;
        margin-top: 0 !important;
        letter-spacing: -0.01em !important;
    }
    
    .sim-card {
        background: linear-gradient(135deg, rgba(244, 63, 94, 0.05) 0%, rgba(15, 23, 42, 0.4) 100%) !important;
        border: 1px solid rgba(244, 63, 94, 0.2) !important;
        border-left: 4px solid #f43f5e !important;
        border-radius: 12px !important;
        padding: 20px !important;
        margin: 20px 0 !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2) !important;
    }
    
    .sim-card p, .sim-card div {
        margin: 0 !important;
        font-weight: 500 !important;
    }
 
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.25);
    }
</style>
""", unsafe_allow_html=True)


def load_data():
    if not os.path.exists("attribution_results.csv") or not os.path.exists("user_journeys.csv"):
        import subprocess
        subprocess.run([sys.executable, "generate_data.py"])
        subprocess.run([sys.executable, "attribution_model.py"])
        
    df_results = pd.read_csv("attribution_results.csv")
    df_transition = pd.read_csv("transition_matrix.csv", index_col=0)
    df_raw = pd.read_csv("user_journeys.csv")
    return df_results, df_transition, df_raw

if "data_loaded" not in st.session_state or not st.session_state.data_loaded:
    try:
        df_results, df_transition, df_raw = load_data()
        st.session_state.df_results = df_results
        st.session_state.df_transition = df_transition
        st.session_state.df_raw = df_raw
        st.session_state.data_loaded = True
    except Exception as e:
        st.session_state.data_loaded = False
        st.error(f"Error loading project data: {e}")

st.sidebar.markdown("<h2 style='color: #a78bfa; font-weight: 700; font-size: 1.5rem; letter-spacing: -0.02em;'>Controls & Settings</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")

total_budget = st.sidebar.number_input(
    "Total Marketing Budget ($)",
    min_value=1000,
    max_value=1000000,
    value=50000,
    step=5000,
    help="Enter the total monthly budget to allocate across marketing channels."
)
st.session_state.total_budget = total_budget

average_order_value = st.sidebar.number_input(
    "Average Order Value ($)",
    min_value=10,
    max_value=10000,
    value=150,
    step=10,
    help="Enter the average purchase value to calculate revenue and ROAS metrics."
)
st.session_state.average_order_value = average_order_value

st.sidebar.markdown("### Current Budget Split (%)")
st.sidebar.caption("Define your current marketing budget split (often aligned to Last-Touch performance):")

if st.session_state.data_loaded:
    channels = st.session_state.df_results['Channel'].tolist()
    st.session_state.channels = channels
    current_shares = {}
    default_shares = [30, 25, 20, 10, 10, 5]

    for idx, ch in enumerate(channels):
        current_shares[ch] = st.sidebar.slider(
            f"{ch} (%)",
            min_value=0,
            max_value=100,
            value=default_shares[idx] if idx < len(default_shares) else 0,
            key=f"slider_{ch}"
        )
    st.session_state.current_shares = current_shares

    total_shares = sum(current_shares.values())
    if total_shares != 100:
        st.sidebar.warning(f"Current budget shares sum to {total_shares}%. Adjust to equal exactly 100%.")

st.markdown("""
<div style="text-align: center; padding: 24px 0px 32px 0px; border-bottom: 1px solid rgba(255, 255, 255, 0.05); margin-bottom: 30px;">
    <h1 style="font-size: 3.5rem; font-weight: 800; margin: 0; background: linear-gradient(135deg, #a78bfa 0%, #6366f1 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -0.04em;">ATTRIBO</h1>
    <p style="font-size: 1.15rem; color: #94a3b8; font-weight: 500; margin: 8px 0 20px 0; letter-spacing: -0.01em;">Multi-Touch Attribution & Marketing Mix Optimization Engine</p>
    <div style="display: flex; justify-content: center; gap: 12px; align-items: center;">
        <span style="display: inline-flex; align-items: center; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); color: #10b981; font-size: 0.75rem; font-weight: 600; padding: 4px 10px; border-radius: 9999px;">
            <span style="width: 6px; height: 6px; background: #10b981; border-radius: 50%; display: inline-block; margin-right: 6px; box-shadow: 0 0 8px #10b981;"></span>
            Markov Model Active
        </span>
        <span style="display: inline-flex; align-items: center; background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.2); color: #6366f1; font-size: 0.75rem; font-weight: 600; padding: 4px 10px; border-radius: 9999px;">
            <span style="width: 6px; height: 6px; background: #6366f1; border-radius: 50%; display: inline-block; margin-right: 6px; box-shadow: 0 0 8px #6366f1;"></span>
            6 Channels Active
        </span>
        <span style="display: inline-flex; align-items: center; background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.2); color: #f59e0b; font-size: 0.75rem; font-weight: 600; padding: 4px 10px; border-radius: 9999px;">
            Database Synced
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

if st.session_state.data_loaded:
    df_raw = st.session_state.df_raw
    total_conversions = int(df_raw[df_raw['converted'] == 1]['user_id'].nunique())
    total_users = int(df_raw['user_id'].nunique())
    overall_conv_rate = (total_conversions / total_users) * 100
    
    st.session_state.total_conversions = total_conversions
    st.session_state.total_users = total_users
    st.session_state.overall_conv_rate = overall_conv_rate

    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    with kpi_col1:
        st.metric("Total User Journeys Analyzed", f"{total_users:,}")
    with kpi_col2:
        st.metric("Total Conversions", f"{total_conversions:,}")
    with kpi_col3:
        st.metric("Overall Conversion Rate", f"{overall_conv_rate:.2f}%")
    with kpi_col4:
        st.metric("Modeled Marketing Channels", f"{len(st.session_state.channels)}")

    st.markdown("---")

    pages = {
        "Attribution Analytics": [
            st.Page("views/overview.py", title="Attribution Comparisons", icon=":material/bar_chart:"),
            st.Page("views/flow.py", title="Markov Chain Flow", icon=":material/route:"),
            st.Page("views/path_explorer.py", title="Journey Path Explorer", icon=":material/explore:")
        ],
        "Planning & Optimization": [
            st.Page("views/simulator.py", title="Channel Blocking Sandbox", icon=":material/block:"),
            st.Page("views/roi.py", title="Budget Reallocation & ROI", icon=":material/payments:"),
            st.Page("views/data_uploader.py", title="Data Upload & Settings", icon=":material/settings:")
        ],
        "Information": [
            st.Page("views/about.py", title="About & Methodology", icon=":material/menu_book:")
        ]
    }
    
    pg = st.navigation(pages)
    pg.run()
else:
    st.info("Generating mock transactional database and building Markov models in the background. Please wait a few seconds...")
