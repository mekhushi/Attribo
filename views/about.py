import streamlit as st

st.markdown("## About & Methodology")
st.markdown("""
**Attribo** is an advanced Multi-Touch Marketing Attribution Engine designed to solve the "last-click bias" in digital marketing analytics. 
Instead of attributing 100% of conversion credit to the final touchpoint, this engine models the complete, 
chronological path of customer interactions to accurately capture top-of-funnel assist value.
""")

st.markdown("<div class='highlight-card'>", unsafe_allow_html=True)
st.markdown("### The Business Problem")
st.write("""
Traditional heuristic models (like Last-Touch) are rule-based and arbitrary. They attribute 100% of sales credit 
to the final touchpoint (e.g., Direct visits or Paid Search ads). Consequently, companies often cut budgets 
for top-of-funnel discovery channels (like Facebook or Instagram ads), which starve the lead generation pipeline 
and lead to a reduction in overall revenue.

This project implements a probabilistic attribution engine to:
1. Reconstruct chronological user touchpoint paths.
2. Evaluate traditional models against a **Markov Chain Model**.
3. Calculate the **Removal Effect** of each channel to find its true conversion assist-value.
4. Optimize budget allocation to maximize conversions for the same marketing spend.
""")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("### Attribution Models Explained")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Heuristic Models")
    st.markdown("""
    - **First Touch**: Assigns 100% of the conversion credit to the first marketing channel the customer interacted with. Best for measuring top-of-funnel brand awareness.
    - **Last Touch**: Assigns 100% of the conversion credit to the final marketing channel the customer clicked before purchasing. Highly biased towards bottom-of-funnel channels.
    - **Linear**: Distributes credit equally across all touchpoints in the customer journey path.
    """)

with col2:
    st.markdown("#### Advanced Models")
    st.markdown("""
    - **Time Decay**: Assigns credit exponentially based on time proximity to the conversion event. Recent clicks receive higher credit than early interactions (using a 7-day half-life).
    - **Position-Based (U-Shaped)**: Assigns 40% of credit to the first touch, 40% to the last touch, and splits the remaining 20% equally among any intermediate touchpoints.
    - **Markov Chain (Probabilistic)**: Evaluates complete customer path transitions as a random walk through a probability network to compute the mathematical influence of each channel.
    """)

st.markdown("---")

st.markdown("### Markov Chain Mathematics")
st.markdown("""
A customer's journey is modeled as a random walk through a directed graph where marketing channels are **transient states**, 
and `(Conversion)` and `(Null)` are **absorbing states** (exits from which the user does not transition back).
""")

math_col1, math_col2 = st.columns(2)

with math_col1:
    st.markdown("#### 1. Transition Matrix")
    st.markdown("""
    Let $S = \\{s_1, s_2, \\dots, s_n\\}$ be the set of states. We calculate the transition probability from state $i$ to state $j$ as:
    $$P(j | i) = \\frac{\\text{Count}(i \\rightarrow j)}{\\sum_k \\text{Count}(i \\rightarrow k)}$$

    The transition matrix $P$ is structured in canonical absorbing form:
    $$P = \\begin{pmatrix} Q & R \\\\ 0 & I \\end{pmatrix}$$
    where:
    - $Q$ is an $M \\times M$ matrix representing probabilities of moving between transient marketing channels.
    - $R$ is an $M \\times 2$ matrix representing probabilities of moving from transient channels to absorbing exits (Conversion, Null).
    - $I$ is the $2 \\times 2$ identity matrix for absorbing states.
    """)

with math_col2:
    st.markdown("#### 2. Fundamental Matrix & Removal Effect")
    st.markdown("""
    Using absorbing Markov chain algebra, the **Fundamental Matrix** $N$ is calculated as:
    $$N = (I - Q)^{-1}$$
    where $N_{i, j}$ represents the expected number of times a customer is in transient state $j$ starting from transient state $i$.

    The probability of absorption (ending up in conversion) starting from transient states is matrix $B$:
    $$B = N \\times R = (I - Q)^{-1} R$$
    
    The baseline conversion probability $p_{\\text{base}}$ is the value of starting at `(Start)` and reaching `(Conversion)`.

    To calculate the importance of channel $X$, we set all transitions entering $X$ to transition instead to `(Null)`. We then recompute the blocked conversion probability $p_{\\text{blocked}}$. The **Removal Effect (RE)** is:
    $$\\text{RE}_X = \\frac{p_{\\text{base}} - p_{\\text{blocked}}}{p_{\\text{base}}}$$
    """)

st.markdown("---")
st.markdown("### How to Navigate Attribo")
st.markdown("""
- **Overview & Comparisons**: Review overall campaign performance, and compare conversion allocation across all six models side-by-side.
- **Markov Chain Flow**: View the raw transition matrix heatmap, and look at the path volumes in the Sankey flow chart.
- **Journey Path Explorer**: Browse, search, and filter individual paths using sequence badges.
- **Channel Blocking Sandbox**: Interact with the model by blocking channels to see estimated lost sales and rerouted path probabilities.
- **Budget Reallocation & ROI**: Input your monthly marketing spend and average order values in the sidebar to simulate budget recommendations, cost acquisition costs (CAC), and ROAS changes.
- **Data Upload**: Upload your company's own CSV event log to test the mathematical models on your real data.
""")
