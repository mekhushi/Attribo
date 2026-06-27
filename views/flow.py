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
            color_continuous_scale='Viridis',
            template='plotly_dark'
        )
        fig_heatmap.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
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
            color_continuous_scale='Blues',
            template='plotly_dark'
        )
        fig_removal.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title="Removal Index (0 = No Impact, 1 = Complete Loss)"
        )
        st.plotly_chart(fig_removal, use_container_width=True)

    st.markdown("---")
    st.markdown("### Customer Journey Flow Diagram (Sankey)")
    st.markdown("Visual representation of transitions between channels from (Start) to either (Conversion) or (Null) exits.")
    
    states = list(df_transition.columns)
    node_labels = [s.replace('(', '').replace(')', '') for s in states]
    
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
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=node_labels,
            color="#6366f1"
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color="rgba(99, 102, 241, 0.2)"
        )
    )])
    fig_sankey.update_layout(
        title_text="Multi-Touch Flow Visualizer",
        font_size=12,
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=500
    )
    st.plotly_chart(fig_sankey, use_container_width=True)
else:
    st.warning("Data not loaded. Please wait or reload the home page.")
