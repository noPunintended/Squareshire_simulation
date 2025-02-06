import numpy as np
import yaml


def read_rates_config(filepath):
    with open(filepath, 'r') as file:
        config = yaml.safe_load(file)
    return config


def generate_random_value(rates, size=1):

    if rates[0] == 'uniform':
        return np.random.uniform(rates[1], rates[2])
    
    elif rates[0] == 'exponential':
        return np.random.uniform(rates[1], rates[2])
    
    else: return np.null 


def calculate_distance(origin, destination):

    return np.sqrt((origin[0] - destination[0])**2 + (origin[1] - destination[1])**2)


def calculate_travel(origin, destination):

    distances = calculate_distance(origin, destination)
    print(distances)
    expected_travel_time = distances/ rates['trip']['avg_travel_speed']
    print(expected_travel_time)
    actual_travel_time = expected_travel_time * generate_random_value(rates['trip']['actual_trip_bound'])

    return expected_travel_time, actual_travel_time

rates = read_rates_config('configs.yaml')
print(calculate_travel((1,1), (10, 13)))