import streamlit as st
import pandas as pd
import numpy as np
import os

# Set page configurations (MUST be the first Streamlit command)
st.set_page_config(
    page_title="Marketing Attribution Suite",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium styling via CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background-color: #0b0f19;
        color: #f1f5f9;
    }
    
    .stMetric {
        background: rgba(30, 41, 59, 0.4);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    div[data-testid="stMetricValue"] {
        color: #38bdf8 !important;
        font-size: 2.2rem !important;
        font-weight: 700;
    }
    
    div[data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: 0.95rem !important;
        font-weight: 500;
    }
    
    h1, h2, h3, h4 {
        color: #f8fafc;
        font-weight: 600 !important;
        letter-spacing: -0.025em;
    }
    
    .highlight-card {
        background: linear-gradient(135deg, rgba(30, 27, 75, 0.5) 0%, rgba(49, 16, 66, 0.5) 100%);
        border: 1px solid rgba(139, 92, 246, 0.25);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
    }
    
    .sim-card {
        background: rgba(30, 41, 59, 0.3);
        border-radius: 12px;
        border: 1px solid rgba(59, 130, 246, 0.25);
        padding: 20px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to load data
def load_data():
    if not os.path.exists("attribution_results.csv") or not os.path.exists("user_journeys.csv"):
        import subprocess
        subprocess.run(["python", "generate_data.py"])
        subprocess.run(["python", "attribution_model.py"])
        
    df_results = pd.read_csv("attribution_results.csv")
    df_transition = pd.read_csv("transition_matrix.csv", index_col=0)
    df_raw = pd.read_csv("user_journeys.csv")
    return df_results, df_transition, df_raw

# Initialize data in session state
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

# Sidebar configurations
st.sidebar.markdown("<h2 style='color: #38bdf8;'>Controls & Settings</h2>", unsafe_allow_html=True)
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
    default_shares = [30, 25, 20, 10, 10, 5] # Default split summing to 100

    for idx, ch in enumerate(channels):
        current_shares[ch] = st.sidebar.slider(
            f"{ch} (%)",
            min_value=0,
            max_value=100,
            value=default_shares[idx] if idx < len(default_shares) else 0,
            key=f"slider_{ch}"
        )
    st.session_state.current_shares = current_shares

    # Validate split sums to 100
    total_shares = sum(current_shares.values())
    if total_shares != 100:
        st.sidebar.warning(f"Current budget shares sum to {total_shares}%. Adjust to equal exactly 100%.")

# Main Title Header
st.markdown("<h1 style='text-align: center; margin-bottom: 5px;'>Multi-Touch Marketing Attribution Suite</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 1.1rem; margin-bottom: 30px;'>Solving Last-Touch Bias with Markov Chain Probability Modeling</p>", unsafe_allow_html=True)

if st.session_state.data_loaded:
    df_raw = st.session_state.df_raw
    total_conversions = int(df_raw[df_raw['converted'] == 1]['user_id'].nunique())
    total_users = int(df_raw['user_id'].nunique())
    overall_conv_rate = (total_conversions / total_users) * 100
    
    st.session_state.total_conversions = total_conversions
    st.session_state.total_users = total_users
    st.session_state.overall_conv_rate = overall_conv_rate

    # KPI Summary Row
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

    # Define Multi-page Navigation
    pages = {
        "Attribution Analytics": [
            st.Page("views/overview.py", title="Attribution Comparisons"),
            st.Page("views/flow.py", title="Markov Chain Flow"),
            st.Page("views/path_explorer.py", title="Journey Path Explorer")
        ],
        "Planning & Optimization": [
            st.Page("views/simulator.py", title="Channel Blocking Sandbox"),
            st.Page("views/roi.py", title="Budget Reallocation & ROI"),
            st.Page("views/data_uploader.py", title="Data Upload & Settings")
        ],
        "Information": [
            st.Page("views/about.py", title="About & Methodology")
        ]
    }
    
    pg = st.navigation(pages)
    pg.run()
else:
    st.info("Generating mock transactional database and building Markov models in the background. Please wait a few seconds...")
