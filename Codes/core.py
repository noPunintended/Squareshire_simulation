import pandas as pd
import numpy as np
import logging
import time
import pickle
from driver import Driver
from rider import Rider
from waiting_points import Waiting_Points
from available_drivers import AvailableDrivers
from available_riders import AvailableRiders
from events_calendar import EventCalendar
from utils.readers import ExcelReader
from utils.traveling import (read_rates_config,
                             create_first_driver_rider,
                             update_drivers_location)


def log_and_print(message, name):
    logging.info(message)
    with open(f"output/{name}_ride_simulation_output.txt", "a") as log_file:
        log_file.write(message + "\n")


def final_output(drivers, riders, name):

    # Convert to DataFrame
    drivers_df = pd.DataFrame.from_dict({k: vars(v) for k, v in drivers.items()}, orient='index')
    riders_df = pd.DataFrame.from_dict({k: vars(v) for k, v in riders.items()}, orient='index')

    # Save as pickle
    drivers_df.to_pickle(f"output/{name}_drivers.pkl")
    riders_df.to_pickle(f"output/{name}_riders.pkl")


def first_event(rates):

    first_driver, first_rider = create_first_driver_rider(rates)
    ec = EventCalendar()
    termination = rates['simulation']['termination']
    ec.add_event(first_driver, {
        'type': 'driver', 'events': 'available'})
    ec.add_event(first_rider, {
        'type': 'rider', 'events': 'available'})
    ec.add_event(termination, {'type': 'termination'})
    return ec

def new_drivers(id, time, ec):
    driver = Driver(id=f'd_{id}',
                    current_location=None,
                    origin=None,
                    become_available=time,
                    offline_time=np.inf,
                    status='idling',
                    earnings=0,
                    current_trip=None)
    
    next_driver_time = driver.generating_driver(rates, time)
    ec.add_event(next_driver_time, {
        'type': 'driver', 'events': 'available'})
    ec.add_event(driver.offline_time, {
        'type': 'driver', 'events': 'offline'}, {'driver': driver.id})
    id += 1
    return driver, id


def new_riders(id, time, ec):
    rider = Rider(id=f'r_{id}',
                  current_location=None,
                  origin=None,
                  destination=None,
                  become_available=time,
                  patience_time=np.inf,
                  status='waiting')
    next_driver_time = rider.generating_rider(ec, rates, time)
    ec.add_event(next_driver_time, {
        'type': 'rider', 'events': 'available'})
    id += 1
    return rider, id


def process_available_driver(driver, t_now, ec, available_riders, available_drivers, rates):
    """Handles both 'available' and 'searching_for_rider' events for drivers."""
    driver.searching_for_rider(ec, t_now)
    log_and_print(f'Driver {driver.id} is just available at {t_now} location: {driver.current_location}', rates['simulation']['name'])
    log_and_print(f'Driver jobs time: {driver.offline_time}', rates['simulation']['name'])
    
    # If there are available riders, match the driver with the closest rider
    if available_riders.is_not_empty():
        closest_rider, cs_distance = available_riders.find_closest_rider(driver)
        if (cs_distance < rates['maximum_match_range']['max_range']) or (not rates['simulation']['maximum_match_range']):
            driver.picking_up(closest_rider, ec, t_now, rates)
            available_riders.remove_rider(closest_rider.id)
            log_and_print(f'Matched driver {driver.id} with rider {closest_rider.id}, rider location: {closest_rider.current_location}', rates['simulation']['name'])

        else:
            driver.status = 'idling'
            driver.start_idling = t_now
            available_drivers.add_driver(driver)
            log_and_print('exceeds maximum matching range', rates['simulation']['name'])
            if rates['simulation']['waiting_points']:
                driver.waiting_time = t_now
                closest_wp = Waiting_Points.find_closest_waiting_point(driver.current_location)
                if closest_wp:
                    driver.travel_to_waiting_point(ec, t_now, closest_wp, rates)
                    log_and_print(f'Driver {driver.id} is traveling to waiting point {closest_wp.name} at {t_now}, location: {closest_wp.corr}', rates['simulation']['name'])
                    log_and_print(f'Driver {driver.id} is idling at {t_now}, location: {driver.current_location}', rates['simulation']['name'])
    # If there are no available riders, add the driver to the available drivers pool
    else:
        driver.status = 'idling'
        driver.start_idling = t_now
        available_drivers.add_driver(driver)
        if rates['simulation']['waiting_points']:
            driver.waiting_time = t_now
            closest_wp = Waiting_Points.find_closest_waiting_point(driver.current_location)
            if closest_wp:
                driver.travel_to_waiting_point(ec, t_now, closest_wp, rates)
                log_and_print(f'Driver {driver.id} is traveling to waiting point {closest_wp.name} at {t_now}, location: {closest_wp.corr}', rates['simulation']['name'])
                log_and_print(f'Driver {driver.id} is idling at {t_now}, location: {driver.current_location}', rates['simulation']['name'])
    drivers[driver.id] = driver


def snapshot(iter, drivers, riders, t_now, rates):
    update_drivers_location(drivers, riders, t_now, rates, mode='snapshot')
    names = rates['simulation']['name'] + f'_snapshot_{iter}' 
    final_output(drivers, riders, names)


def create_snapshot(ec, rates, n_snapshot=10):
    time_steps = np.linspace(0,  rates['simulation']['termination'], n_snapshot + 1)  
    for snap in time_steps:
        ec.add_event(snap, {'type': 'snapshot', 'events': snap})


def log_values(concurrent_drivers, concurrent_riders, t_now, snap_df):
    
    current_time = t_now  # Capture the current timestamp
    new_row = pd.DataFrame([{"time": current_time, "concurrent_drivers": concurrent_drivers, "concurrent_riders": concurrent_riders}])
    snap_df = pd.concat([snap_df, new_row], ignore_index=True)
    return snap_df


def simulation_stats(start, sim_start, termination, n_events, name):
    """Prints the simulation statistics."""
    sim_time = time.time() - sim_start
    total_time = time.time() - start
    sim = {}
    sim['simulation_time'] = sim_time
    sim['total_time'] = total_time
    sim['termination'] = termination
    sim['n_events'] = n_events
    pickle.dump(sim, open(f'output/{name}_simulation_stats.pkl', 'wb'))


if __name__ == "__main__":
    start = time.time()
    rates = read_rates_config('configs.yaml')
    # Configure logging
    logging.basicConfig(
        filename=f'output/{rates['simulation']['name']}_ride_simulation.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filemode='w'  # Overwrites the log file each time the script runs
    )
    # Ensure the output text file is overwritten each time the script runs
    with open(f"output/{rates['simulation']['name']}_ride_simulation_output.txt", "w") as log_file:
        log_file.write("")
    np.random.seed(42)
    ec = EventCalendar()
    drivers = {}
    riders = {}
    available_drivers = AvailableDrivers()
    available_riders = AvailableRiders()
    t_now, termination = 0, rates['simulation']['termination']
    driver_id, rider_id = 0, 0
    ec = first_event(rates)
    create_snapshot(ec, rates, n_snapshot=rates['simulation']['n_snaps'])
    n_events = 0
    concurrent_drivers = 0
    concurrent_riders = 0
    snap_df = pd.DataFrame()

    while t_now < termination:
        start_sim = time.time()
        event = ec.pop(0)
        n_events += 1
        t_now = event['time']

        # Process the event
        if event['type']['type'] == 'driver':
            # Check if the driver is available or searching for a rider
            if event['type']['events'] in ['available', 'searching_for_rider']:
                # Create a new driver if available
                if event['type']['events'] == 'available':
                    driver, driver_id = new_drivers(driver_id, t_now, ec)
                    drivers[driver.id] = driver
                    concurrent_drivers = concurrent_drivers + 1
                # Get existing driver if searching
                else:   driver = drivers[event['data']['driver']]  # Get existing driver if searching

                process_available_driver(driver, t_now, ec, available_riders, available_drivers, rates)

            # If the driver is departing
            elif event['type']['events'] == 'departing':

                # Get the driver and rider objects
                driver = drivers[event['data']['driver']]
                rider = riders[event['data']['rider']]
                # Execute the departing method
                driver.departing(rider, ec, t_now, rates)
                log_and_print(f'Driver {driver.id} and riders {rider.id} is departing at {t_now}, location: {driver.current_location} to {rider.destination}', rates['simulation']['name'])
                # Update the driver and rider dictionaries
                drivers[driver.id] = driver
                riders[rider.id] = rider

            # If the driver is dropping off
            elif event['type']['events'] == 'dropping_off':

                # Get the driver and rider objects
                driver = drivers[event['data']['driver']]
                rider = riders[event['data']['rider']]
                # Execute the dropping off method
                driver.dropping_off(rider, ec, t_now, rates)
                concurrent_riders = concurrent_riders - 1
                log_and_print(f'Driver {driver.id} is dropping off rider {rider.id} at {t_now}, location: {driver.current_location}', rates['simulation']['name'])

                # Update the driver and rider dictionaries
                drivers[driver.id] = driver
                riders[rider.id] = rider

            elif event['type']['events'] == 'idling':
                driver = drivers[event['data']['driver']]
                if driver.status == 'traveling_to_waiting_points':
                    log_and_print(f'Driver {driver.id} reaches waiting point and now waiting for customers', rates['simulation']['name'])
                    driver.idling(rates)


            # If the driver is going offline
            elif event['type']['events'] == 'offline':
                driver = drivers[event['data']['driver']]
                # Check if the driver is idling or dropping off
                if driver.status == 'traveling_to_waiting_points':
                    driver.interupting_trip(t_now, rates)
                if driver.status == 'idling' or driver.going_offline:
                    driver.status = 'offline'
                    driver.going_offline = True
                    driver.actual_offline_time = t_now
                    drivers[driver.id] = driver
                    concurrent_drivers = concurrent_drivers - 1
                    log_and_print(f'Driver {event["data"]["driver"]} is now offline at {t_now}', rates['simulation']['name'])
                else:
                    # If the driver is dropping off, go offline after dropping off
                    ec.add_event(driver.current_trip['time_arrival'], {'type': 'driver', 'events': 'offline'}, {'driver': driver.id})
                    driver.going_offline = True
                    drivers[driver.id] = driver
                    log_and_print(f'Driver {event["data"]["driver"]} is dropping off and then going offline at {driver.current_trip['time_arrival']}', rates['simulation']['name'])

        # If the event is a rider event
        elif event['type']['type'] == 'rider':
            # If the rider is available
            if event['type']['events'] == 'available':
                # Create a new rider and queue the next rider event
                concurrent_riders = concurrent_riders + 1
                rider, rider_id = new_riders(rider_id, t_now, ec)
                log_and_print(f'Rider {rider.id} is available at {t_now}, location: {rider.current_location}', rates['simulation']['name'])

                # If there are available drivers, match the rider with the closest driver
                if available_drivers.is_not_empty():
                    update_drivers_location(drivers, riders, t_now, rates, mode='finding_drivers')
                    closest_driver, cs_distance = available_drivers.find_closest_driver(rider, t_now)
                    if (cs_distance >= rates['maximum_match_range']['max_range']) and rates['simulation']['maximum_match_range']:
                        available_riders.add_rider(rider)
                        log_and_print("Maximum Distance Reach", rates['simulation']['name'])
                        log_and_print(f'Rider {rider.id} is waiting at {t_now}, location: {rider.current_location}', rates['simulation']['name'])
                    else:
                        available_drivers.remove_driver(closest_driver.id)
                        closest_driver.picking_up(rider, ec, t_now, rates)
                        log_and_print(f'Matched driver {closest_driver.id} with rider {rider.id}, rider location: {rider.current_location}', rates['simulation']['name'])
                # If there are no available drivers, add the rider to the available riders pool
                else:
                    available_riders.add_rider(rider)
                    log_and_print(f'Rider {rider.id} is waiting at {t_now}, location: {rider.current_location}', rates['simulation']['name'])
                riders[rider.id] = rider
            
            # If the rider is abandoning the ride
            elif event['type']['events'] == 'cancel':
                rider = riders[event['data']['rider']]
                if rider.status == 'waiting':
                    rider.status = 'abandoned'
                    concurrent_riders = concurrent_riders - 1
                    rider.offline_time = t_now
                    riders[rider.id] = rider
                    available_riders.remove_rider(rider.id)
                    log_and_print(f'Rider {rider.id} has abandoned the ride at {t_now}, location: {rider.current_location}', rates['simulation']['name'])


        elif event['type']['type'] == 'snapshot':
            snapshot(event['type']['events'], drivers, riders, t_now, rates)
            snap_df = log_values(concurrent_drivers, concurrent_riders, t_now, snap_df)

                # If the event is a termination event
        elif event['type']['type'] == 'termination':
            update_drivers_location(drivers, riders, t_now, rates)
            final_output(drivers, riders, rates['simulation']['name'])
            log_and_print(f'Simulation terminated at {t_now}', rates['simulation']['name'])
            termination = time.time()
            simulation_stats(start, start_sim, termination, n_events, rates['simulation']['name'])
            snap_df.to_csv("output/concurrent_data.csv", index=False)
            break


        else:
            log_and_print(f'Unknown event: {event}', rates['simulation']['name'])
