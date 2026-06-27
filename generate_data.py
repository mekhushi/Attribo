import numpy as np
import pandas as pd
import random
from datetime import datetime, timedelta

np.random.seed(42)
random.seed(42)

def generate_customer_journeys(num_users=5000):
    channels = ['Facebook', 'Instagram', 'Google Ads', 'Email', 'Organic Search', 'Direct']
    
    next_channel_probs = {
        'Facebook': ['Google Ads', 'Direct', 'Organic Search', 'Facebook'],
        'Instagram': ['Google Ads', 'Direct', 'Organic Search', 'Instagram'],
        'Google Ads': ['Direct', 'Email', 'Google Ads'],
        'Email': ['Direct', 'Organic Search', 'Email'],
        'Organic Search': ['Direct', 'Organic Search'],
        'Direct': ['Direct']
    }
    
    data = []
    
    start_date = datetime(2026, 5, 1)
    
    for i in range(num_users):
        user_id = f"usr_{100000 + i}"
        
        path_length = random.choices([1, 2, 3, 4, 5], weights=[0.4, 0.3, 0.15, 0.1, 0.05])[0]
        
        first_channel = random.choices(
            channels, 
            weights=[0.3, 0.25, 0.15, 0.1, 0.12, 0.08]
        )[0]
        
        path = [first_channel]
        for _ in range(path_length - 1):
            current = path[-1]
            choices = next_channel_probs[current]
            next_ch = random.choice(choices)
            path.append(next_ch)
            
        has_social = 'Facebook' in path or 'Instagram' in path
        has_search = 'Google Ads' in path or 'Organic Search' in path
        has_email = 'Email' in path
        
        if len(path) == 1:
            conv_prob = 0.015
        else:
            if has_social and has_search:
                conv_prob = 0.12
            elif has_email and has_search:
                conv_prob = 0.15
            elif has_social and has_email:
                conv_prob = 0.10
            else:
                conv_prob = 0.05
                
        converted = np.random.binomial(1, conv_prob)
        
        current_time = start_date + timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        for idx, channel in enumerate(path):
            current_time += timedelta(
                days=random.choices([0, 1, 2], weights=[0.6, 0.3, 0.1])[0],
                hours=random.randint(1, 12)
            )
            
            is_last = (idx == len(path) - 1)
            converted_flag = converted if is_last else 0
            
            data.append({
                'user_id': user_id,
                'timestamp': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                'channel': channel,
                'converted': converted_flag
            })
            
    df = pd.DataFrame(data)
    df = df.sort_values(by=['user_id', 'timestamp']).reset_index(drop=True)
    return df

if __name__ == "__main__":
    print("Generating raw user journey logs...")
    df = generate_customer_journeys(num_users=6000)
    df.to_csv("user_journeys.csv", index=False)
    print(f"Dataset successfully created! Total logs: {len(df)}")
    print(f"Total conversions: {df['converted'].sum()}")
    print("Sample data:")
    print(df.head(10))
