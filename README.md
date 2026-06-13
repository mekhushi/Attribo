# Multi-Touch Marketing Attribution Suite

An advanced, corporate-ready marketing analytics platform that solves the "last-click bias" in digital marketing. Instead of giving 100% credit to the final channel a customer clicked before purchasing, this engine reconstructs complete customer journeys and uses absorbing **Markov Chains** to calculate transition probabilities between channels and determine the exact influence (Removal Effect) of each marketing touchpoint.

---

## The Business Problem

Traditional digital marketing attribution models (like Last-Touch) are rule-based and arbitrary. They attribute 100% of the conversion value to the final touchpoint (e.g., a Direct visit or a final Paid Search ad). Consequently, marketing teams often cut budgets for early-stage discovery channels (such as Facebook/Instagram ads), causing overall lead volume and company revenue to collapse because the customer acquisition pipeline is starved at the top of the funnel.

This project implements a data-driven, probabilistic attribution engine to:
1. Reconstruct chronological user touchpoint paths.
2. Evaluate traditional models (First-Touch, Last-Touch, Linear, Time Decay, Position-Based) against a **Markov Chain Model**.
3. Calculate the **Removal Effect** of each channel to find its true conversion assist-value.
4. Optimize budget allocation to maximize conversions for the same marketing spend.

---

## Key Features

The application is structured as a multi-page analytics suite:

### 1. Attribution Comparisons
- **Visual Analytics**: Interactive group bar charts comparing allocated conversions across 6 different models.
- **Model Distribution Matrix**: Full metrics comparing First Touch, Last Touch, Linear, Time Decay, Position-Based (U-Shaped), and Markov Chain attribution.
- **Analyst Insights**: Automated summaries highlighting top-of-funnel undervaluation and bottom-of-funnel inflation.

### 2. Markov Chain Flow
- **Transition Probability Heatmap**: Displays the probability of a user transitioning between any two marketing states.
- **Sankey Journey Diagram**: A visual flow visualizer illustrating traffic volume from (Start) to conversion or exit endpoints.
- **Channel Removal Effects**: A sorted index ranking which channels are most critical to keeping journeys alive.

### 3. Journey Path Explorer
- **Path Filtering**: Search individual customer paths by User ID, or filter by conversion status, path length, and specific channels clicked.
- **Visual Sequence Badges**: Renders customer journeys as chronological sequence badges (e.g., `Facebook` -> `Organic Search` -> `Converted`).
- **Leaderboard**: Displays a table of the most common user paths and their conversion success rates.

### 4. Channel Blocking Sandbox
- **Real-Time Simulation**: Block specific marketing channels dynamically.
- **Funnel Drop Calculator**: Instantly recalculates the fundamental matrix to estimate lost conversions and drops in overall conversion rate.
- **Simulated Flows**: Re-draws transition heatmaps and Sankey diagrams to show how traffic gets rerouted when channels are closed.

### 5. Budget Reallocation & ROI
- **Spend Optimization**: Input monthly budgets and average order values (AOV) to calculate variance splits.
- **CAC & ROAS Comparisons**: Side-by-side analysis showing how Return on Ad Spend (ROAS) and Cost Acquisition Cost (CAC) shift under Markov attribution.
- **Efficiency Gain Projections**: Modeled growth estimations highlighting CAC reduction percentages.

### 6. Data Upload & Settings
- **Custom CSV Loader**: Upload your own marketing campaigns event log.
- **Schema Validation**: Validates that uploaded data matches required columns (`user_id`, `timestamp`, `channel`, `converted`).
- **Pipeline Recompile**: Re-runs the calculations in python and updates all dashboard metrics instantly.

---

## Mathematical Methodology

A customer's journey is modeled as a random walk through a directed graph where marketing channels are **transient states**, and `(Conversion)` and `(Null)` are **absorbing states**.

### 1. Transition Matrix
Let $S = \{s_1, s_2, \dots, s_n\}$ be the set of states. We calculate the transition probability from state $i$ to state $j$ as:
$$P(j | i) = \frac{\text{Count}(i \rightarrow j)}{\sum_k \text{Count}(i \rightarrow k)}$$

The transition matrix $P$ is structured in canonical absorbing form:
$$P = \begin{pmatrix} Q & R \\ 0 & I \end{pmatrix}$$
where:
*   $Q$ is an $M \times M$ matrix representing probabilities of moving between transient marketing channels.
*   $R$ is an $M \times 2$ matrix representing probabilities of moving from transient channels to absorbing exits (Conversion, Null).
*   $I$ is the $2 \times 2$ identity matrix representing absorbing states.

### 2. Absorption Probabilities
Using absorbing Markov chain algebra, the fundamental matrix $N$ is calculated as:
$$N = (I - Q)^{-1}$$
where $N_{i, j}$ represents the expected number of times the chain is in transient state $j$ starting from transient state $i$.

The probability of absorption (ending up in a final conversion state) starting from each transient state is given by the matrix $B$:
$$B = N \times R = (I - Q)^{-1} R$$

The baseline probability of starting at `(Start)` and reaching `(Conversion)` is the value $B[\text{'(Start)'}, \text{'(Conversion)'}]$.

### 3. Removal Effect
To calculate the importance of channel $X$, we set all transitions entering channel $X$ to transition instead to `(Null)`. We then recompute the conversion probability $p_{\text{blocked}}$. The **Removal Effect (RE)** is:
$$\text{RE}_X = \frac{p_{\text{base}} - p_{\text{blocked}}}{p_{\text{base}}}$$

The attribution weight for channel $X$ is then:
$$\text{Attribution Weight}_X = \frac{\text{RE}_X}{\sum_j \text{RE}_j}$$

---

## Project Structure

```
├── app.py                     # Main navigation router and styling manager
├── attribution_model.py       # Core modeling script (heuristics & Markov formulas)
├── generate_data.py           # Customer journey dataset generator
├── queries.sql                # Portfolio SQL queries (CTE sessionization & pathing)
├── requirements.txt           # Python package dependencies
├── .gitignore                 # Version control ignores
└── views/                     # Dedicated multipage view modules
    ├── overview.py            # Conversions bar charts & strategic insights
    ├── flow.py                # Heatmaps, removal index, & baseline Sankey
    ├── path_explorer.py       # Journey search & sequence badges
    ├── simulator.py           # Channel blocking sandbox simulator
    ├── roi.py                 # Spend reallocator & ROAS/CAC comparative metrics
    ├── data_uploader.py       # CSV upload validation & reset controls
    └── about.py               # Documentation and absorbing matrix math
```

---

## Setup & Execution

### 1. Prerequisites
Make sure Python 3.9+ is installed on your system.

### 2. Environment Setup
Create a virtual environment and install dependencies:
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Generate Data & Run Calculations
Execute the processing pipeline to generate user journeys and calculate the attribution models:
```powershell
# Generate customer journey data
python generate_data.py

# Calculate attribution models (saves results to CSV)
python attribution_model.py
```

### 4. Launch the Dashboard
Run the multi-page Streamlit suite locally:
```powershell
streamlit run app.py
```
Open **`http://localhost:8501`** in your browser to view the application.
