#queue algorithm logic

while current_time < simulation_end_time and event_queue not empty:
    event_time, event_type, entity = insert next event
    current_time = event_time
    handle_event(event_type, entity)


#rider algorithm matching and cancelling logic

def match_rider(rider):
    closest_driver = None
    min_distance = inf
    
    for driver in available_drivers:
        distance = euclidean(rider.origin, driver.location)
        if distance < min_distance:
            min_distance = distance
            closest_driver = driver
    
    if closest_driver:
        schedule_pickup(rider, closest_driver)
    else:
        add_to_waiting_list(rider)

#distance time for trip algorithm logic
base_time = euclidean_distance(A,B)/20  # 20 mph avg speed
actual_time = Uniform(0.8*base_time, 1.2*base_time)

#For KPI tracking 
metrics = {
    'total_riders': 0,
    'completed_rides': 0,
    'abandoned_riders': 0,
    'total_wait_time': 0.0,
    'driver_stats': {
        driver_id: {'earnings': 0.0, 'active_hours': 0.0}
    }
}


#For Random variable generations and stuff

# Driver availability duration
availability_time = 5 + 3*random.random()  # Uniform(5,8)

# Rider patience time
patience = random.expovariate(5)  # Mean 1/5 hours



######DUMMY CODE FOR TESTING#######

# Initialize (Procedural?) #Import data from excel
event_queue = []  # Priority queue for events
current_time = 0.0  # Simulation clock
available_drivers = []  # List of available drivers (location tuples)
waiting_riders = []  # List of waiting riders (dicts with patience, origin, etc.)
active_trips = []  # List of active trips (dicts with driver, rider, etc.)
metrics = {
    "total_riders": 0,
    "abandoned_riders": 0,
    "completed_rides": 0,
    "total_wait_time": 0.0,
    "driver_earnings": {},
}


#######################################################
