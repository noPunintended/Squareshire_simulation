import numpy as np
import pandas as pd 
from utils.traveling import read_rates_config, generate_random_value

def pregenerate_drivers(simulation_time, rates):
    driver_data = []
    driver_id = 0
    t = 0  # Tracks simulation time

    while t <= simulation_time:
        driver_data.append({
            'ID': f"DRV-{driver_id:06d}",
            'Arrival Time': t,
            'Location_X': np.random.uniform(0, 20),  
            'Location_Y': np.random.uniform(0, 20)
        })
        
        # Get next arrival time (extract scalar to prevent arrays)
        inter_arrival_time = float(generate_random_value(rates['drivers']['inter_arrival']))
        
        t += inter_arrival_time
        driver_id += 1

        # Prevent memory overflow
        if len(driver_data) > 1_000_000:  
            print("Warning: Too many drivers generated!")
            break  

    return pd.DataFrame(driver_data)

# Load rates from YAML config
rates = read_rates_config('configs.yaml')

# Run pre-generation for a simulation time of 100 units
simulation_time = 86400
drivers_df = pregenerate_drivers(simulation_time, rates)

# Display first few drivers
print(drivers_df.head())
