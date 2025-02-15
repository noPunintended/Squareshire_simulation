import numpy as np
import pandas as pd 
from utils.traveling import read_rates_config, generate_random_value
#import matplotlib.pyplot as plt  #For seeing how and where they spawn
#import seaborn as sns


def pregenerate_drivers(simulation_time, rates):
    driver_data = []
    driver_id = 0
    t = 0  # Tracks simulation time
    Et = 0 # Tracks the time when a driver exits the simulation (Available time)



    while t <= simulation_time:

        jobs_time = generate_random_value(rates['drivers']['jobs_time']).item()
        Et = t + jobs_time  

        driver_data.append({
            'ID': f"DRV-{driver_id:06d}",
            'Arrival Time': t,
            'Going home at': Et,
            'Location_X': np.random.uniform(0, 20),  
            'Location_Y': np.random.uniform(0, 20)
        })
        
        # Get next arrival time (extract scalar to prevent arrays)
        #inter_arrival_time = float(generate_random_value(rates['drivers']['inter_arrival']))
        #inter_arrival_time = generate_random_value(rates['drivers']['inter_arrival'])

        inter_arrival_time = generate_random_value(rates['drivers']['inter_arrival']).item() 
        #fixed it in a more elegant way, numpy array to a scalar.

        #For debugging
        #print(f"Generated inter-arrival time: {inter_arrival_time}, Type: {type(inter_arrival_time)}")
        #fixed it in a more elegant way, numpy array to a scalar.
        
     
        t += inter_arrival_time
        #Et = t + jobs_time
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



'''
sns.set_style("whitegrid")

# Convert arrival times to hours for better readability
drivers_df['Arrival Hour'] = drivers_df['Arrival Time'] / 3600  # Convert seconds to hours

## **1. Histogram of Driver Arrivals**
plt.figure(figsize=(10, 5))
sns.histplot(drivers_df['Arrival Hour'], bins=30, kde=True)
plt.xlabel("Time (Hours)")
plt.ylabel("Number of Drivers")
plt.title("Distribution of Driver Arrivals Over Time")
plt.show()

## **2. Scatter Plot to see driver spawning on the map**
plt.figure(figsize=(10, 5))
plt.scatter(drivers_df['Arrival Hour'], drivers_df['Location_X'], s=5, alpha=0.5, label='X Coord')
plt.scatter(drivers_df['Arrival Hour'], drivers_df['Location_Y'], s=5, alpha=0.5, label='Y Coord', color='red')
plt.xlabel("Time (Hours)")
plt.ylabel("Location")
plt.title("Driver Spawn Locations Over Time")
plt.legend()
plt.show()
'''