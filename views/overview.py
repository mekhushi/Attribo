import streamlit as st
import pandas as pd
import plotly.express as px

st.markdown("## Attribution Comparisons")
st.markdown("""
Compare how different attribution models distribute conversion credits across channels. 
Traditional models like **Last Touch** overvalue end-of-funnel channels, while the **Markov Chain model** uses 
a probabilistic "Removal Effect" to capture true assist value.
""")

if "df_results" in st.session_state:
    df_results = st.session_state.df_results

    # Melt df for plotting
    df_melted = df_results.melt(
        id_vars=['Channel'], 
        value_vars=['First Touch', 'Last Touch', 'Linear', 'Time Decay', 'Position-Based', 'Markov Attribution'],
        var_name='Attribution Model', 
        value_name='Attributed Conversions'
    )

    fig_compare = px.bar(
        df_melted,
        x='Channel',
        y='Attributed Conversions',
        color='Attribution Model',
        barmode='group',
        color_discrete_sequence=['#818cf8', '#f472b6', '#60a5fa', '#fb7185', '#fbbf24', '#34d399'],
        template='plotly_dark'
    )
    fig_compare.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_title="Marketing Channel",
        yaxis_title="Allocated Conversions",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_compare, use_container_width=True)

    # Comparative Table
    st.markdown("### Exact Model Distributions")
    df_table = df_results[['Channel', 'First Touch', 'Last Touch', 'Linear', 'Time Decay', 'Position-Based', 'Markov Attribution']].copy()
    for col in df_table.columns[1:]:
        df_table[col] = df_table[col].round(1)
    st.dataframe(df_table, use_container_width=True, hide_index=True)

    # Strategic Insights Card
    st.markdown("<div class='highlight-card'>", unsafe_allow_html=True)
    st.markdown("### Strategic Analyst Insight")
    
    # Calculate difference for Facebook
    fb_last = df_results[df_results['Channel'] == 'Facebook']['Last Touch'].values[0]
    fb_markov = df_results[df_results['Channel'] == 'Facebook']['Markov Attribution'].values[0]
    fb_diff = ((fb_markov - fb_last) / fb_last) * 100 if fb_last > 0 else 0
    
    st.write(f"""
    *   **Top-of-Funnel Undervaluation:** Notice that **Facebook** and **Instagram** receive significantly higher credit in the **Markov Chain** model compared to **Last Touch** (a **{fb_diff:.1f}% increase** for Facebook). This is because social media ads act as crucial "assistors" that initiate user paths but rarely receive the final click.
    *   **Bottom-of-Funnel Inflation:** Conversely, channels like **Direct** or **Google Ads** are frequently overvalued by Last-Touch attribution, as they are clicked right before conversion, masking the discovery channels that brought the customer in originally.
    *   **Intermediate Models:** **Time Decay** strikes a balance by shifting credit to latter channels while keeping top-of-funnel visible. **Position-Based (U-Shaped)** ensures first discovery and final push are heavily rewarded.
    """)
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.warning("Data not loaded. Please wait or reload the home page.")
