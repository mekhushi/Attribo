import pandas as pd
import numpy as np
from collections import defaultdict

def load_and_preprocess_data(filepath="user_journeys.csv"):
    """
    Loads raw user event logs and aggregates them into sequential paths for each user.
    """
    df = pd.read_csv(filepath)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values(by=['user_id', 'timestamp'])
    
    # Group by user and reconstruct chronological channel paths and timestamps
    paths = df.groupby('user_id').agg({
        'channel': lambda x: list(x),
        'timestamp': lambda x: list(x),
        'converted': 'max' # 1 if any touchpoint resulted in conversion, else 0
    }).reset_index()
    
    paths.rename(columns={'channel': 'path', 'timestamp': 'timestamps'}, inplace=True)
    return paths

def calculate_heuristic_attribution(paths):
    """
    Calculates standard baseline models: First-Touch, Last-Touch, Linear, Time Decay, and Position-Based (U-Shaped).
    """
    first_touch = defaultdict(float)
    last_touch = defaultdict(float)
    linear = defaultdict(float)
    time_decay = defaultdict(float)
    position_based = defaultdict(float)
    
    total_conversions = 0
    half_life_days = 7.0
    
    for _, row in paths.iterrows():
        path = row['path']
        timestamps = row['timestamps']
        converted = row['converted']
        
        if converted == 1:
            total_conversions += 1
            n_steps = len(path)
            
            # 1. First Touch
            first_touch[path[0]] += 1
            
            # 2. Last Touch
            last_touch[path[-1]] += 1
            
            # 3. Linear (equal split)
            for channel in path:
                linear[channel] += 1.0 / n_steps
                
            # 4. Time Decay (7-day half-life decay from the time of last touchpoint)
            last_time = timestamps[-1]
            weights = []
            for t in timestamps:
                # Convert time delta to days
                delta_days = (last_time - t).total_seconds() / (24 * 3600)
                # Apply decay formula: 2^(-t / half_life)
                weight = 2.0 ** (-delta_days / half_life_days)
                weights.append(weight)
                
            # Normalize weights
            sum_weights = sum(weights)
            if sum_weights > 0:
                weights = [w / sum_weights for w in weights]
            else:
                weights = [1.0 / n_steps] * n_steps
                
            for idx, channel in enumerate(path):
                time_decay[channel] += weights[idx]
                
            # 5. Position-Based (U-Shaped: 40% First, 40% Last, 20% split among middle)
            if n_steps == 1:
                position_based[path[0]] += 1.0
            elif n_steps == 2:
                position_based[path[0]] += 0.5
                position_based[path[1]] += 0.5
            else:
                position_based[path[0]] += 0.4
                position_based[path[-1]] += 0.4
                middle_weight = 0.2 / (n_steps - 2)
                for channel in path[1:-1]:
                    position_based[channel] += middle_weight
                
    # Convert to DataFrame
    all_channels = sorted(list(set([ch for p in paths['path'] for ch in p])))
    
    df_heuristics = pd.DataFrame({
        'Channel': all_channels,
        'First Touch': [first_touch[ch] for ch in all_channels],
        'Last Touch': [last_touch[ch] for ch in all_channels],
        'Linear': [linear[ch] for ch in all_channels],
        'Time Decay': [time_decay[ch] for ch in all_channels],
        'Position-Based': [position_based[ch] for ch in all_channels]
    })
    
    return df_heuristics, total_conversions

def calculate_markov_attribution(paths, total_conversions):
    """
    Implements Markov Chain attribution using the Removal Effect.
    Uses absorbing state matrix algebra to compute exact conversion probabilities.
    """
    # Step 1: Count transitions between states
    # States include: (Start), channels, (Conversion), (Null)
    transition_counts = defaultdict(lambda: defaultdict(int))
    
    for _, row in paths.iterrows():
        path = row['path']
        converted = row['converted']
        
        # Add (Start) at the beginning
        full_path = ['(Start)'] + path
        
        # Add final state
        if converted == 1:
            full_path.append('(Conversion)')
        else:
            full_path.append('(Null)')
            
        # Record transitions
        for i in range(len(full_path) - 1):
            state_from = full_path[i]
            state_to = full_path[i+1]
            transition_counts[state_from][state_to] += 1
            
    # Step 2: Compute baseline transition probability matrix
    # We will build a matrix over all transient states to all states
    channels = sorted(list(set([ch for p in paths['path'] for ch in p])))
    transient_states = ['(Start)'] + channels
    absorbing_states = ['(Conversion)', '(Null)']
    all_states = transient_states + absorbing_states
    
    # Calculate transition matrix P
    # P = [[Q, R], [0, I]]
    # Q: transient to transient (M x M)
    # R: transient to absorbing (M x 2)
    def build_transition_matrix(blocked_channel=None):
        Q = np.zeros((len(transient_states), len(transient_states)))
        R = np.zeros((len(transient_states), len(absorbing_states)))
        
        for idx_from, state_from in enumerate(transient_states):
            total_out = sum(transition_counts[state_from].values())
            
            if total_out == 0:
                continue
                
            for state_to, count in transition_counts[state_from].items():
                prob = count / total_out
                
                # If we are calculating the removal effect of a channel, 
                # we block any transitions entering that channel (redirect to Null)
                actual_state_to = state_to
                if blocked_channel and state_to == blocked_channel:
                    actual_state_to = '(Null)'
                    
                if actual_state_to in transient_states:
                    idx_to = transient_states.index(actual_state_to)
                    Q[idx_from, idx_to] = prob
                else:
                    idx_to = absorbing_states.index(actual_state_to)
                    R[idx_from, idx_to] = prob
                    
        return Q, R

    # Calculate base conversion probability
    Q_base, R_base = build_transition_matrix()
    # Fundamental Matrix N = (I - Q)^-1
    I = np.identity(len(transient_states))
    N_base = np.linalg.inv(I - Q_base)
    # Absorption probabilities B = N * R
    B_base = np.dot(N_base, R_base)
    
    # Base probability of starting at (Start) and reaching (Conversion)
    p_conversion_base = B_base[0, 0] # Index 0 is '(Start)', Index 0 of R is '(Conversion)'
    
    # Step 3: Calculate Removal Effect for each channel
    removal_effects = {}
    for channel in channels:
        Q_blocked, R_blocked = build_transition_matrix(blocked_channel=channel)
        N_blocked = np.linalg.inv(I - Q_blocked)
        B_blocked = np.dot(N_blocked, R_blocked)
        p_conversion_blocked = B_blocked[0, 0]
        
        # Removal Effect is the relative drop in conversion probability
        removal_effects[channel] = (p_conversion_base - p_conversion_blocked) / p_conversion_base
        
    # Step 4: Allocate conversions based on Removal Effects
    sum_removal_effects = sum(removal_effects.values())
    markov_conversions = {}
    
    for channel in channels:
        if sum_removal_effects > 0:
            weight = removal_effects[channel] / sum_removal_effects
        else:
            weight = 0.0
        markov_conversions[channel] = weight * total_conversions
        
    df_markov = pd.DataFrame({
        'Channel': channels,
        'Removal Effect': [removal_effects[ch] for ch in channels],
        'Markov Attribution': [markov_conversions[ch] for ch in channels]
    })
    
    # Also return the transition matrix for plotting
    df_transition = pd.DataFrame(0.0, index=transient_states, columns=all_states)
    for state_from in transient_states:
        total_out = sum(transition_counts[state_from].values())
        if total_out > 0:
            for state_to, count in transition_counts[state_from].items():
                df_transition.loc[state_from, state_to] = count / total_out
                
    return df_markov, df_transition

def main():
    print("Loading paths and cleaning data...")
    paths = load_and_preprocess_data("user_journeys.csv")
    
    print("Calculating heuristic and advanced models (First-Touch, Last-Touch, Linear, Time Decay, Position-Based)...")
    df_heuristics, total_conv = calculate_heuristic_attribution(paths)
    
    print(f"Calculating Markov Chain model (Total conversions to distribute: {total_conv})...")
    df_markov, df_transition = calculate_markov_attribution(paths, total_conv)
    
    # Merge results
    df_results = pd.merge(df_heuristics, df_markov, on='Channel')
    
    # Save files
    df_results.to_csv("attribution_results.csv", index=False)
    df_transition.to_csv("transition_matrix.csv")
    
    print("Models computed successfully! Saved 'attribution_results.csv' and 'transition_matrix.csv'")
    print("\nSummary of Attribution Models:")
    print(df_results[['Channel', 'First Touch', 'Last Touch', 'Linear', 'Time Decay', 'Position-Based', 'Markov Attribution']].round(1))

if __name__ == "__main__":
    main()
