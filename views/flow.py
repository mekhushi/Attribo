import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.markdown("## Markov Chain Flow Analytics")
st.markdown("""
Examine the mathematical pathways customers take between discovery and conversion. 
The heatmap shows the probability of moving from one channel to another, while the Sankey chart 
visualizes the actual volume flow of user journeys.
""")

if "df_transition" in st.session_state and "df_results" in st.session_state:
    df_transition = st.session_state.df_transition
    df_results = st.session_state.df_results
    df_raw = st.session_state.df_raw
    total_users = st.session_state.total_users

    col_m1, col_m2 = st.columns([1, 1])
    
    with col_m1:
        st.markdown("### Transition Probability Heatmap")
        st.markdown("""
        This heatmap displays the probability of a user transitioning from **Row (State From)** to **Column (State To)**.
        - High values in the `(Conversion)` column represent strong bottom-of-funnel converters (e.g. Email).
        - High values between channels show typical progression pathways (e.g. Facebook -> Google Ads).
        """)
        
        heatmap_data = df_transition.drop(index=['(Conversion)', '(Null)'], errors='ignore')
        
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
        The **Removal Effect** measures the relative drop in overall conversion probability if a channel is completely 
        blocked or removed from the customer lifecycle. A higher removal effect indicates a more critical assist channel.
        """)
        
        df_removal = df_results[['Channel', 'Removal Effect']].sort_values(by='Removal Effect', ascending=True)
        
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

    st.markdown("---")
    st.markdown("### Customer Journey Flow Diagram (Sankey)")
    st.markdown("Visual representation of transitions between channels from (Start) to either (Conversion) or (Null) exits.")
    
    states = list(df_transition.columns)
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
    
    for r_idx, row_name in enumerate(df_transition.index):
        for c_idx, col_name in enumerate(df_transition.columns):
            prob = df_transition.loc[row_name, col_name]
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
