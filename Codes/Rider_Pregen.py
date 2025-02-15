import numpy as np
import pandas as pd
from utils.traveling import read_rates_config, generate_random_value

def pregenerate_riders(simulation_time, rates):
    np.random.seed(42)
    rider_data = []
    rider_id = 0
    t = 0  # Tracks simulation time

    while t <= simulation_time:
        patience_time = generate_random_value(rates['riders']['wait_time']).item()  # Exponential patience time

        rider_data.append({
            'ID': f"RDR-{rider_id:06d}",
            'Arrival Time': t,
            'Patience Time': patience_time,  # How long they wait before leaving, exponential
            'Leaving/Abandoning Trip At': t + patience_time,  # Time when they leave if not picked up, when they abandon
            'Pickup_Location_X': np.random.uniform(0, 20),
            'Pickup_Location_Y': np.random.uniform(0, 20),
            'Destination_X': np.random.uniform(0, 20),
            'Destination_Y': np.random.uniform(0, 20),
        })

        inter_arrival_time = generate_random_value(rates['riders']['inter_arrival']).item()  
        t += inter_arrival_time  
        rider_id += 1

        # Prevent memory overflow
        if len(rider_data) > 1_000_000:  
            print("Warning: Too many riders generated!")
            break  

    return pd.DataFrame(rider_data)

# Load rates from YAML config
rates = read_rates_config('configs.yaml')

# Run pre-generation for a simulation time of 86400 seconds (1 day)
simulation_time = 86400
riders_df = pregenerate_riders(simulation_time, rates)

# Display first few riders
print(riders_df.head())
