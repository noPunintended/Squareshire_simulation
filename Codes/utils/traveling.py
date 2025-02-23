import numpy as np
import yaml

#high possibility that we need to convery all the outputs to scalar or find a way to deal with them arrays
#main issue is playing with them in pregeneration itself.

def read_rates_config(filepath):
    with open(filepath, 'r') as file:
        config = yaml.safe_load(file)
    return config


def generate_random_value(dist, size=1):

    if dist[0] == 'uniform':
        vars =  np.random.uniform(dist[1], dist[2], size)
    
    elif dist[0] == 'exponential':
        vars = np.random.exponential(1/ dist[1], size)
    
    elif dist[0] == 'normal':
        vars = np.random.normal(dist[1], dist[2], size)
    
    elif dist[0] == 'beta':
        vars = (np.random.beta(dist[1], dist[2], size) * (dist[4])) + dist[3]
    
    else: return None

    if size == 1: vars = vars[0]

    return vars


def create_first_driver_rider(rates):
    f_d = generate_random_value(rates['drivers']['inter_arrival'])
    f_r = generate_random_value(rates['riders']['inter_arrival'])

    return f_d, f_r

def calculate_distance(origin_x, origin_y, destination_x, destination_y):

    return np.sqrt((origin_x - destination_x)**2 + (origin_y - destination_y)**2)


def calculate_travel(origin_x, origin_y, destination_x, destination_y, rates):

    distances = calculate_distance(origin_x, origin_y, destination_x, destination_y)
    expected_travel_time = distances/ rates['trip']['avg_travel_speed']
    travel_rates = generate_random_value(rates['trip']['actual_trip_bound'])
    actual_travel_time = expected_travel_time * travel_rates

    return distances, expected_travel_time, actual_travel_time, travel_rates #need to fix this, gives us funny values 
#convert to array to scalar?


def calculate_fare(distance, rates):
    
    return rates['riders']['initial_pay_rate'] + (rates['riders']['pay_rate'] * distance)


def find_closest_driver(available_driver_x, available_driver_y, rider):##Need Fixing

    distances = calculate_distance(rider.current_location[0], 
                                   rider.current_location[1],
                                   available_driver_x,
                                   available_driver_y,
                                   )
    
    return np.argmin(distances)


def find_closest_rider(driver, available_rider_x, available_rider_y):##Need Fixing

    distances = calculate_distance(driver.current_location[0], 
                                   driver.current_location[1],
                                   available_rider_x,
                                   available_rider_y,
                                   )
    
    return np.argmin(distances)


def return_current_pos(origin_x, origin_y, destination_x, destination_y, actual_travel_time, departure_time, current_time):

    current_trip_time = current_time - departure_time
    dist_x = (destination_x - origin_x)
    dist_y = (destination_y - origin_y)
    avg_speed_x = dist_x / actual_travel_time
    avg_speed_y = dist_y / actual_travel_time
    dist_x_traveled = current_trip_time * avg_speed_x
    dist_y_traveled = current_trip_time * avg_speed_y
    current_x = origin_x + dist_x_traveled
    current_y = origin_y + dist_y_traveled
    return current_x, current_y, dist_x_traveled, dist_y_traveled, current_trip_time


def update_drivers_location(drivers, riders, t_now, rates, mode='termination'):
    """Update the location of drivers who are currently on a trip."""
    
    driver_data = {
        "ids": [],
        "origin_x": [],
        "origin_y": [],
        "destination_x": [],
        "destination_y": [],
        "travel_time": [],
        "departure_time": []
    }

    # Collect data for drivers who have an active trip
    for driver_id, driver in drivers.items():
        if driver.current_trip:
            driver_data["ids"].append(driver_id)
            driver_data["origin_x"].append(driver.current_trip['origin'][0])
            driver_data["origin_y"].append(driver.current_trip['origin'][1])
            driver_data["destination_x"].append(driver.current_trip['destination'][0])
            driver_data["destination_y"].append(driver.current_trip['destination'][1])
            driver_data["travel_time"].append(driver.current_trip['actual_travel_time'])
            driver_data["departure_time"].append(driver.current_trip['time_departure'])

    # Convert lists to NumPy arrays for efficient computation
    origin_x = np.array(driver_data["origin_x"]).reshape(-1) 
    origin_y = np.array(driver_data["origin_y"]).reshape(-1) 
    destination_x = np.array(driver_data["destination_x"]).reshape(-1) 
    destination_y = np.array(driver_data["destination_y"]).reshape(-1) 
    travel_time = np.array(driver_data["travel_time"]).reshape(-1) 
    departure_time = np.array(driver_data["departure_time"]).reshape(-1) 

    # Compute the current positions and distances
    current_x, current_y, dist_x, dist_y, current_trip_time = return_current_pos(
        origin_x, origin_y, destination_x, destination_y, travel_time, departure_time, t_now
    )
    
    distances = np.sqrt(dist_x**2 + dist_y**2)

    # Update each driver's location and fuel cost
    for i, driver_id in enumerate(driver_data["ids"]):
        driver = drivers[driver_id]
        driver.current_location = (current_x[i], current_y[i])
        if mode == 'termination':
            driver.total_distance += distances[i]
            driver.fuel_cost += distances[i] * rates['drivers']['petrol_cost']
            driver.total_time += current_trip_time[i]
        if driver.status != 'traveling_to_waiting_points':
            riders[driver.current_trip['matched_rider']].current_location = driver.current_location

    return None
