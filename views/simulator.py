import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.markdown("## Channel Blocking Sandbox")
st.markdown("""
Simulate what happens if one or more channels are shut down or completely blocked from the customer journey. 
The Markov Chain transitions and absorption rates are re-calculated dynamically to show how customer paths 
get disrupted and how many conversions are lost.
""")

def simulate_channel_blocking(df_trans, blocked_channels):
    P = df_trans.copy()
    
    for ch in blocked_channels:
        if ch in P.columns:
            P['(Null)'] = P['(Null)'] + P[ch]
            P[ch] = 0.0
            
    trans_states = list(P.index)
    
    Q = P[trans_states].values
    
    R = P[['(Conversion)', '(Null)']].values
    
    I = np.identity(len(trans_states))
    try:
        N = np.linalg.inv(I - Q)
        B = np.dot(N, R)
        conv_prob = B[0, 0]
    except Exception:
        conv_prob = 0.0
        
    return conv_prob, P

if "df_transition" in st.session_state and "channels" in st.session_state:
    df_transition = st.session_state.df_transition
    channels = st.session_state.channels
    df_raw = st.session_state.df_raw
    total_conversions = st.session_state.total_conversions
    total_users = st.session_state.total_users

    selectable_channels = [c for c in channels]
    blocked_channels = st.multiselect(
        "Select channels to block/remove:",
        options=selectable_channels,
        default=[],
        help="Select channels to simulate what happens if they are shut down."
    )
    
    base_conv_prob, _ = simulate_channel_blocking(df_transition, [])
    sim_conv_prob, df_sim_transition = simulate_channel_blocking(df_transition, blocked_channels)
    
    sim_col1, sim_col2, sim_col3 = st.columns(3)
    with sim_col1:
        st.metric(
            "Baseline Conversion Probability", 
            f"{base_conv_prob * 100:.2f}%"
        )
    with sim_col2:
        pct_change = ((sim_conv_prob - base_conv_prob) / base_conv_prob) * 100 if base_conv_prob > 0 else 0
        st.metric(
            "Simulated Conversion Probability", 
            f"{sim_conv_prob * 100:.2f}%",
            delta=f"{pct_change:.2f}%",
            delta_color="normal" if pct_change == 0 else "inverse"
        )
    with sim_col3:
        lost_conversions = total_conversions * (1 - (sim_conv_prob / base_conv_prob)) if base_conv_prob > 0 else 0
        st.metric(
            "Estimated Lost Conversions", 
            f"{int(lost_conversions):,}" if len(blocked_channels) > 0 else "0"
        )
        
    if len(blocked_channels) > 0:
        st.markdown("<div class='sim-card'>", unsafe_allow_html=True)
        st.write(f"**Simulation Note:** Blocking **{', '.join(blocked_channels)}** redirects all incoming customer steps to the (Null) exit state. This models the loss of top-of-funnel discovery or middle-funnel assistance.")
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.markdown("---")
    
    col_m1, col_m2 = st.columns([1, 1])
    
    with col_m1:
        st.markdown("### Transition Probability Heatmap (Simulated)")
        st.markdown("""
        This heatmap displays the probability of a user transitioning from **Row (State From)** to **Column (State To)**.
        Blocked channels will show all transitions entering them redirected to Null.
        """)
        
        heatmap_data = df_sim_transition.drop(index=['(Conversion)', '(Null)'], errors='ignore')
        
        fig_heatmap = px.imshow(
            heatmap_data,
            labels=dict(x="Transition To", y="Transition From", color="Probability"),
            color_continuous_scale=[(0.00, '#030712'), (0.15, '#1e1b4b'), (0.55, '#6366f1'), (1.00, '#c084fc')],
            template='plotly_dark'
        )
        fig_heatmap.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Plus Jakarta Sans", color="#94a3b8"),
            margin=dict(t=30, b=30, l=10, r=10),
            coloraxis_colorbar=dict(
                title="Probability",
                thickness=15,
                len=0.8,
                tickfont=dict(color="#94a3b8")
            ),
            hoverlabel=dict(
                bgcolor="#0b0f19",
                bordercolor="rgba(255,255,255,0.08)",
                font_size=12,
                font_family="Plus Jakarta Sans"
            )
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)

    with col_m2:
        st.markdown("### Channel Removal Effects")
        st.markdown("""
        The **Removal Effect** measures the decrease in overall conversion probability if a channel is completely 
        blocked or removed from the customer lifecycle. (Calculated statically from raw baseline data)
        """)
        
        df_removal = st.session_state.df_results[['Channel', 'Removal Effect']].sort_values(by='Removal Effect', ascending=True)
        
        fig_removal = px.bar(
            df_removal,
            x='Removal Effect',
            y='Channel',
            orientation='h',
            color='Removal Effect',
            color_continuous_scale=[(0.0, '#1e1b4b'), (1.0, '#8b5cf6')],
            template='plotly_dark'
        )
        fig_removal.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Plus Jakarta Sans", color="#94a3b8"),
            xaxis=dict(
                title="Removal Index (0 = No Impact, 1 = Complete Loss)",
                gridcolor='rgba(255, 255, 255, 0.03)',
                showgrid=True
            ),
            yaxis=dict(
                title="",
                showgrid=False
            ),
            hoverlabel=dict(
                bgcolor="#0b0f19",
                bordercolor="rgba(255,255,255,0.08)",
                font_size=12,
                font_family="Plus Jakarta Sans"
            ),
            margin=dict(t=30, b=30, l=10, r=10),
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_removal, use_container_width=True)

    st.markdown("### Customer Journey Flow Diagram (Sankey)")
    st.markdown("Visual representation of transitions between channels from (Start) to either (Conversion) or (Null) exits, reflecting the current blocked/removed channels.")
    
    states = list(df_sim_transition.columns)
    node_labels = [s.replace('(', '').replace(')', '') for s in states]
    
    channel_colors_map = {
        'Start': '#64748b',
        'Conversion': '#10b981',
        'Null': '#f43f5e',
        'Facebook': '#3b82f6',
        'Instagram': '#ec4899',
        'Google Ads': '#f59e0b',
        'Email': '#06b6d4',
        'Organic Search': '#6366f1',
        'Direct': '#8b5cf6'
    }
    
    node_colors = [channel_colors_map.get(label, '#8b5cf6') for label in node_labels]
    
    sources = []
    targets = []
    values = []
    
    for r_idx, row_name in enumerate(df_sim_transition.index):
        for c_idx, col_name in enumerate(df_sim_transition.columns):
            prob = df_sim_transition.loc[row_name, col_name]
            if prob > 0.02:
                if row_name == '(Start)':
                    vol = total_users * prob
                else:
                    vol = df_raw[df_raw['channel'] == row_name]['user_id'].nunique() * prob
                
                sources.append(states.index(row_name))
                targets.append(states.index(col_name))
                values.append(vol)
                
    fig_sankey = go.Figure(data=[go.Sankey(
        node=dict(
            pad=18,
            thickness=20,
            line=dict(color="rgba(0,0,0,0.3)", width=1),
            label=node_labels,
            color=node_colors
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color="rgba(139, 92, 246, 0.15)"
        )
    )])
    fig_sankey.update_layout(
        title_text="Multi-Touch Flow Visualizer",
        font=dict(family="Plus Jakarta Sans", size=12, color="#94a3b8"),
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=520,
        margin=dict(t=50, b=20, l=10, r=10)
    )
    st.plotly_chart(fig_sankey, use_container_width=True)
else:
    st.warning("Data not loaded. Please wait or reload the home page.")
