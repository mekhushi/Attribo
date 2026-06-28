import streamlit as st
import pandas as pd
from collections import Counter

st.markdown("## Journey Path Explorer")
st.markdown("""
Drill down into individual customer journeys. Reconstruct sequences, analyze the most common pathways 
converting leads, and filter paths by length, channel involvement, and final conversion state.
""")

@st.cache_data
def get_user_paths(df_raw):
    df_sorted = df_raw.sort_values(by=['user_id', 'timestamp'])
    
    paths = df_sorted.groupby('user_id').agg({
        'channel': lambda x: list(x),
        'converted': 'max',
        'timestamp': 'min'
    }).reset_index()
    
    paths.rename(columns={'channel': 'path', 'timestamp': 'started_at'}, inplace=True)
    paths['path_str'] = paths['path'].apply(lambda p: " > ".join(p))
    paths['length'] = paths['path'].apply(len)
    return paths

if "df_raw" in st.session_state and st.session_state.data_loaded:
    df_raw = st.session_state.df_raw
    channels = st.session_state.channels
    
    df_paths = get_user_paths(df_raw)
    
    total_paths = len(df_paths)
    unique_paths = df_paths['path_str'].nunique()
    converted_paths = df_paths[df_paths['converted'] == 1]
    conv_rate = (len(converted_paths) / total_paths) * 100 if total_paths > 0 else 0
    avg_length = df_paths['length'].mean()
    
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        st.metric("Total Reconstructed Paths", f"{total_paths:,}")
    with col_s2:
        st.metric("Unique Path Variations", f"{unique_paths:,}")
    with col_s3:
        st.metric("Average Path Touchpoints", f"{avg_length:.2f}")
    with col_s4:
        st.metric("Path Conversion Rate", f"{conv_rate:.2f}%")
        
    st.markdown("---")
    
    st.markdown("### Top Converting Journeys Leaderboard")
    st.markdown("The most common channel combinations that customers took and their respective conversion success rates.")
    
    df_leaderboard = df_paths.groupby('path_str').agg({
        'user_id': 'count',
        'converted': ['sum', 'mean']
    }).reset_index()
    
    df_leaderboard.columns = ['Journey Path', 'Volume', 'Conversions', 'Conversion Success Rate']
    df_leaderboard['Conversion Success Rate'] = (df_leaderboard['Conversion Success Rate'] * 100).round(2)
    df_leaderboard = df_leaderboard.sort_values(by='Volume', ascending=False)
    
    df_lead_display = df_leaderboard.copy()
    df_lead_display['Conversion Success Rate'] = df_lead_display['Conversion Success Rate'].map(lambda x: f"{x:.2f}%")
    st.dataframe(df_lead_display.head(15), use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    st.markdown("### Search & Filter Individual Paths")
    
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        search_user = st.text_input("Search User ID", placeholder="e.g. usr_100042").strip()
    with col_f2:
        filter_status = st.selectbox(
            "Conversion Status", 
            options=["All", "Converted Only", "Non-Converted Only"]
        )
    with col_f3:
        filter_channels = st.multiselect(
            "Must Include Channels", 
            options=channels,
            default=[],
            help="Show only paths that contain all of the selected channels."
        )
        
    min_len = int(df_paths['length'].min())
    max_len = int(df_paths['length'].max())
    filter_length = st.slider("Path Touchpoints Range", min_value=min_len, max_value=max_len, value=(min_len, max_len))
    
    df_filtered = df_paths.copy()
    
    if search_user:
        df_filtered = df_filtered[df_filtered['user_id'].str.contains(search_user, case=False)]
        
    if filter_status == "Converted Only":
        df_filtered = df_filtered[df_filtered['converted'] == 1]
    elif filter_status == "Non-Converted Only":
        df_filtered = df_filtered[df_filtered['converted'] == 0]
        
    df_filtered = df_filtered[(df_filtered['length'] >= filter_length[0]) & (df_filtered['length'] <= filter_length[1])]
    
    if filter_channels:
        df_filtered = df_filtered[df_filtered['path'].apply(lambda p: all(c in p for c in filter_channels))]
        
    st.markdown(f"**Showing {len(df_filtered):,} matching customer journeys**")
    
    limit_paths = 30
    df_sample = df_filtered.head(limit_paths)
    
    channel_colors = {
        'Facebook': '#3b82f6',
        'Instagram': '#ec4899',
        'Google Ads': '#f59e0b',
        'Email': '#10b981',
        'Organic Search': '#6366f1',
        'Direct': '#6b7280',
    }
    
    for idx, row in df_sample.iterrows():
        user = row['user_id']
        path_list = row['path']
        is_conv = row['converted']
        
        badges_html = []
        for ch in path_list:
            bg_color = channel_colors.get(ch, '#1e293b')
            badges_html.append(f'<span style="background-color: {bg_color}; color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.85rem; font-weight: 600; margin: 0 4px; border: 1px solid rgba(255,255,255,0.1);">{ch}</span>')
            
        if is_conv == 1:
            badges_html.append('<span style="background-color: #10b981; color: white; padding: 4px 12px; border-radius: 4px; font-size: 0.85rem; font-weight: 700; margin-left: 10px; border: 1px solid rgba(255,255,255,0.2);">Converted</span>')
        else:
            badges_html.append('<span style="background-color: #ef4444; color: white; padding: 4px 12px; border-radius: 4px; font-size: 0.85rem; font-weight: 700; margin-left: 10px; border: 1px solid rgba(255,255,255,0.2);">Null Exit</span>')
            
        full_line_html = f'<div style="background-color: rgba(30, 41, 59, 0.3); padding: 15px; border-radius: 8px; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.05); display: flex; align-items: center; justify-content: space-between;"><span style="font-weight: 700; color: #94a3b8; font-size: 0.9rem;">{user}</span><div style="display: flex; align-items: center; flex-wrap: wrap;">{" ➔ ".join(badges_html)}</div></div>'
        
        st.markdown(full_line_html, unsafe_allow_html=True)
        
    if len(df_filtered) > limit_paths:
        st.caption(f"Showing first {limit_paths} journeys. Adjust filters to refine your search.")
else:
    st.warning("Data not loaded. Please wait or reload the home page.")
