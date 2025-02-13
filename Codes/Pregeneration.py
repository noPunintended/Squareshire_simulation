#Testing out i.e writing code for pregeneration
#Since location of spawning is uniform we can potential generate it aswell alongside the IDs
#Why do this? 
#Ans: Will allow us to keep a track of the ids and prevent clashes
#secondly if the locations are pre-generated we dont need to call the generate function in our loop
#this might save up more computational time and prevent clashes
#furthermore to make the id more unique we can have 
#id = random incremental number + time + location this would potential add more info to id (not sure)
#adding the information about simulation duration here itself for now
#furthermore we know about exponential inter-arrival times, so we can just generate it aswell cant we?


import numpy as np
import yaml #not sure if this works or not
from utils.traveling import read_rates_config, generate_random_value
simulation_duration = 86400

def pregenerate_entities(config_path, simulation_duration):
    rates = read_rates_config(config_path)
    #intention behind read_rates_config is to have a function that reads from config.yaml file
    #Again the function generation and calling seems a bit off here, but As long as you get the gist of the 
    #idea we in a good spot, im trying to replicate what you did in traveling.py
    # Generate drivers
    drivers = []
    driver_id = 0
    t = 0
    while t < simulation_duration:
        drivers.append({
            'id': f"DRV-{driver_id:04d}",
            'available_time': t,
            'location': np.random.uniform(0, 20, 2)
        })
        t += generate_random_value(rates['drivers']['inter_arrival'])
        driver_id += 1
    
    # Generate riders
    riders = []
    rider_id = 0
    t = 0
    while t < simulation_duration:
        riders.append({
            'id': f"RDR-{rider_id:06d}",
            'request_time': t,
            'origin': np.random.uniform(0, 20, 2)
        })
        t += generate_random_value(rates['riders']['inter_arrival'])
        rider_id += 1
    
    return drivers, riders

#hopefully the output would look like 
#driver : ID, available time, location
#drivers randomly vanish/go back home so we can figure out how much time would it take for a driver to spawn
#Potential issues: The inter-arrival time is not there, instead the drivers spawn
#at exponential rates.This implies that the time would be off in this code.
#potential fixes if my assumption and interpretation are wrong : Well re-structure the code and the time logic

simulation_entities = pregenerate_entities('configs.yaml', simulation_duration)