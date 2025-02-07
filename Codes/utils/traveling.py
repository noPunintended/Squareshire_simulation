import numpy as np
import yaml


def read_rates_config(filepath):
    with open(filepath, 'r') as file:
        config = yaml.safe_load(file)
    return config


def generate_random_value(dist, size=1):

    if dist[0] == 'uniform':
        return np.random.uniform(dist[1], dist[2], size)
    
    elif dist[0] == 'exponential':
        return np.random.exponential(1/ dist[1], size)
    
    else: return np.null 


def calculate_distance(origin_x, origin_y, destination_x, destination_y):

    return np.sqrt((origin_x - destination_x)**2 + (origin_y - destination_y)**2)


def calculate_travel(origin_x, origin_y, destination_x, destination_y):

    distances = calculate_distance(origin_x, origin_y, destination_x, destination_y)
    print(distances)
    expected_travel_time = distances/ rates['trip']['avg_travel_speed']
    print(expected_travel_time)
    travel_rates = generate_random_value(rates['trip']['actual_trip_bound'])
    actual_travel_time = expected_travel_time * travel_rates

    return expected_travel_time, actual_travel_time, travel_rates


def return_current_pos(origin_x, origin_y, destination_x, destination_y, actual_travel_time, departure_time, current_time):

    current_trip_time = current_time - departure_time
    dist_x = (destination_x - origin_x)
    dist_y = (destination_y - origin_y)
    avg_speed_x = dist_x / actual_travel_time
    avg_speed_y = dist_y / actual_travel_time
    dist_x = current_trip_time * avg_speed_x
    dist_y = current_trip_time * avg_speed_y
    current_x = origin_x + dist_x
    current_y = origin_y + dist_y
    return current_x, current_y

## To save in calculation origin, destination, travel_rates, depart_time, status
# rates = read_rates_config('configs.yaml')
# print(calculate_travel(1, 1, 10, 13))
# print(return_current_pos(np.array([1, 2]), np.array([1, 8]), np.array([10, -9]), np.array([13, 6]), np.array([45.0, 100]), np.array([0, 0]), 10))