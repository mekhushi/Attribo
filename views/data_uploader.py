import streamlit as st
import pandas as pd
import subprocess
import os
import sys

st.markdown("## Data Upload & Settings")
st.markdown("""
Upload your multi-touch marketing event log to recalculate Heuristic and Markov attribution weights. 
Ensure your file contains the proper schema before uploading.
""")

REQUIRED_COLUMNS = ['user_id', 'timestamp', 'channel', 'converted']

st.markdown("<div class='highlight-card'>", unsafe_allow_html=True)
st.markdown("<h3 style='margin-top: 0;'>CSV Schema Guidelines</h3>", unsafe_allow_html=True)
st.markdown("""
Your CSV file must include the following column headers exactly:
- **`user_id`**: Unique string identifying the customer (e.g. `usr_100000`).
- **`timestamp`**: Date and time of the interaction formatted as `YYYY-MM-DD HH:MM:SS`.
- **`channel`**: The marketing channel name (e.g., `Facebook`, `Email`, `Google Ads`).
- **`converted`**: Integer (`1` if this final click resulted in a purchase/conversion, else `0`).
""")
st.markdown("</div>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload customer journeys CSV", type=['csv'])

if uploaded_file is not None:
    try:
        df_preview = pd.read_csv(uploaded_file, nrows=5)
        columns = [c.lower().strip() for c in df_preview.columns]
        
        missing_cols = [col for col in REQUIRED_COLUMNS if col not in columns]
        
        if len(missing_cols) > 0:
            st.error(f"Validation Failed: Missing required columns: {', '.join(missing_cols)}")
        else:
            uploaded_file.seek(0)
            df_full = pd.read_csv(uploaded_file)
            
            df_full.columns = [c.lower().strip() for c in df_full.columns]
            
            df_full['converted'] = pd.to_numeric(df_full['converted'], errors='coerce')
            df_full = df_full.dropna(subset=['converted'])
            df_full['converted'] = df_full['converted'].astype(int)
            
            invalid_conv = df_full[~df_full['converted'].isin([0, 1])]
            if len(invalid_conv) > 0:
                st.error("Validation Failed: The 'converted' column must only contain 0 or 1 values.")
            else:
                st.success("CSV file successfully validated and ready to process!")
                st.markdown("#### Preview of Uploaded Data")
                st.dataframe(df_full.head(10), use_container_width=True)
                
                if st.button("Compile Uploaded Data & Update Suite"):
                    with st.spinner("Writing dataset and re-calculating attribution models..."):
                        df_full.to_csv("user_journeys.csv", index=False)
                        
                        res = subprocess.run([sys.executable, "attribution_model.py"], capture_output=True, text=True)
                        
                        if res.returncode == 0:
                            st.cache_data.clear()
                            
                            df_results = pd.read_csv("attribution_results.csv")
                            df_transition = pd.read_csv("transition_matrix.csv", index_col=0)
                            df_raw = pd.read_csv("user_journeys.csv")
                            
                            st.session_state.df_results = df_results
                            st.session_state.df_transition = df_transition
                            st.session_state.df_raw = df_raw
                            st.session_state.channels = df_results['Channel'].tolist()
                            st.session_state.data_loaded = True
                            
                            st.success("Attribution calculations updated successfully! Navigate to comparisons or flow to view your results.")
                        else:
                            st.error(f"Error executing attribution script: {res.stderr}")
    except Exception as e:
        st.error(f"Error parsing uploaded file: {e}")

st.markdown("---")
st.markdown("### System Maintenance")
st.markdown("Reset the database to default generated settings or rebuild models.")

col_reset1, col_reset2 = st.columns(2)

with col_reset1:
    if st.button("Reset to Default Generated Dataset"):
        with st.spinner("Generating clean mock dataset and running calculations..."):
            try:
                subprocess.run([sys.executable, "generate_data.py"])
                res = subprocess.run([sys.executable, "attribution_model.py"], capture_output=True, text=True)
                
                if res.returncode == 0:
                    st.cache_data.clear()
                    
                    df_results = pd.read_csv("attribution_results.csv")
                    df_transition = pd.read_csv("transition_matrix.csv", index_col=0)
                    df_raw = pd.read_csv("user_journeys.csv")
                    
                    st.session_state.df_results = df_results
                    st.session_state.df_transition = df_transition
                    st.session_state.df_raw = df_raw
                    st.session_state.channels = df_results['Channel'].tolist()
                    st.session_state.data_loaded = True
                    
                    st.success("Database successfully reset back to default mock dataset!")
                else:
                    st.error(f"Error compiling reset: {res.stderr}")
            except Exception as e:
                st.error(f"Reset failed: {e}")

with col_reset2:
    if st.button("Force Recompute Markov Models"):
        with st.spinner("Running math calculations..."):
            try:
                res = subprocess.run([sys.executable, "attribution_model.py"], capture_output=True, text=True)
                if res.returncode == 0:
                    st.cache_data.clear()
                    
                    df_results = pd.read_csv("attribution_results.csv")
                    df_transition = pd.read_csv("transition_matrix.csv", index_col=0)
                    df_raw = pd.read_csv("user_journeys.csv")
                    
                    st.session_state.df_results = df_results
                    st.session_state.df_transition = df_transition
                    st.session_state.df_raw = df_raw
                    st.session_state.channels = df_results['Channel'].tolist()
                    st.session_state.data_loaded = True
                    
                    st.success("Calculations recomputed and reloaded successfully!")
                else:
                    st.error(f"Recompute failed: {res.stderr}")
            except Exception as e:
                st.error(f"Recompute failed: {e}")
