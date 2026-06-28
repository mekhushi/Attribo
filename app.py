import streamlit as st
import pandas as pd
import numpy as np
import os
import sys

st.set_page_config(
    page_title="Attribo - Marketing Attribution Engine",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .main {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    [data-testid="stAppViewContainer"] {
        background-color: #09090b !important;
        color: #f4f4f5 !important;
    }
    
    .main {
        background-color: transparent !important;
        color: #f4f4f5 !important;
    }
    
    [data-testid="stHeader"] {
        background-color: transparent !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: #09090b !important;
        border-right: 1px solid #27272a !important;
    }
    
    [data-testid="stSidebarNavHeader"], 
    div[data-testid="stSidebarNavItems"] > div > span {
        font-size: 0.65rem !important;
        font-weight: 700 !important;
        color: #71717a !important; 
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        padding: 24px 0 8px 16px !important;
        display: block;
    }
    
    [data-testid="stSidebarNavItems"] a, 
    div[data-testid="stSidebarNavItems"] ul li a {
        border-radius: 8px !important;
        margin: 2px 12px !important;
        padding: 8px 12px !important;
        color: #a1a1aa !important; 
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        transition: all 0.15s ease !important;
        text-decoration: none !important;
        display: flex !important;
        align-items: center !important;
    }
    
    [data-testid="stSidebarNavItems"] a:hover, 
    div[data-testid="stSidebarNavItems"] ul li a:hover {
        background: #18181b !important;
        color: #fafafa !important; 
    }
    
    [data-testid="stSidebarNavItems"] a[aria-current="page"], 
    div[data-testid="stSidebarNavItems"] ul li a[aria-current="page"] {
        background: #18181b !important;
        color: #ffffff !important; 
        font-weight: 600 !important;
        border-left: none !important;
        padding-left: 12px !important; 
    }
    
    [data-testid="stSidebar"] .stNumberInput, 
    [data-testid="stSidebar"] .stSlider {
        background: #09090b !important;
        padding: 12px !important;
        border-radius: 8px !important;
        border: 1px solid #27272a !important;
        margin-bottom: 12px !important;
    }
    
    /* Clean Minimal Metric Cards (Vercel/Linear style) */
    div[data-testid="stMetric"] {
        background: #09090b !important;
        border: 1px solid #27272a !important;
        border-radius: 8px !important;
        padding: 16px !important;
        transition: border-color 0.2s ease !important;
        box-shadow: none !important;
    }
    
    div[data-testid="stMetric"]:hover {
        border-color: #3f3f46 !important;
    }
    
    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
    }
    
    div[data-testid="stMetricLabel"] {
        color: #71717a !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        text-transform: none !important;
        letter-spacing: normal !important;
        margin-bottom: 4px !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-weight: 600 !important;
        letter-spacing: -0.025em !important;
    }
    
    /* Matte Solid white buttons (Vercel style) */
    div.stButton > button {
        background-color: #ffffff !important;
        color: #09090b !important;
        font-weight: 600 !important;
        border: 1px solid #ffffff !important;
        border-radius: 6px !important;
        padding: 8px 18px !important;
        transition: all 0.15s ease !important;
        width: auto !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important;
    }
    
    div.stButton > button:hover {
        background-color: #f4f4f5 !important;
        color: #09090b !important;
        border-color: #f4f4f5 !important;
    }
    
    div.stButton > button:active {
        transform: translateY(1px) !important;
    }
 
    /* Style selectboxes and text inputs */
    .stTextInput input, .stSelectbox [data-baseweb="select"], .stMultiSelect [data-baseweb="select"], .stNumberInput input {
        background-color: #09090b !important;
        border: 1px solid #27272a !important;
        border-radius: 8px !important;
        color: #fafafa !important;
        font-size: 0.9rem !important;
    }
    .stTextInput input:focus, .stSelectbox [data-baseweb="select"]:focus, .stMultiSelect [data-baseweb="select"]:focus, .stNumberInput input:focus {
        border-color: #52525b !important;
        box-shadow: none !important;
    }
    .stSelectbox [data-baseweb="select"]:hover, .stMultiSelect [data-baseweb="select"]:hover {
        border-color: #3f3f46 !important;
    }
    
    /* Alerts customization */
    div[data-testid="stAlert"] {
        background: #09090b !important;
        border: 1px solid #27272a !important;
        border-radius: 8px !important;
    }
    
    .highlight-card {
        background: #09090b !important;
        border: 1px solid #27272a !important;
        border-radius: 8px !important;
        padding: 20px !important;
        margin-bottom: 20px !important;
    }
    
    .sim-card {
        background: #09090b !important;
        border-radius: 8px !important;
        border: 1px solid #27272a !important;
        padding: 20px !important;
        margin-bottom: 20px !important;
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
        background: #27272a;
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #3f3f46;
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

st.sidebar.markdown("<h2 style='color: #ffffff; font-weight: 600; font-size: 1.35rem; letter-spacing: -0.02em;'>Controls & Settings</h2>", unsafe_allow_html=True)
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
<div style="text-align: center; padding: 40px 0px 45px 0px; margin-bottom: 20px;">
    <h1 style="font-size: 3rem; font-weight: 700; margin: 0; color: #ffffff; letter-spacing: -0.03em;">Attribo</h1>
    <p style="font-size: 1.1rem; color: #94a3b8; margin: 8px 0 0 0; font-weight: 500; letter-spacing: -0.01em;">Markov Chain Multi-Touch Marketing Attribution</p>
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
