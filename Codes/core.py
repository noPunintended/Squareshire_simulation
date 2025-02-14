import heapq
import pandas as pd
import numpy as np
import logging
from driver import Driver
from rider import Rider
from available_drivers import AvailableDrivers
from available_riders import AvailableRiders
from events_calendar import EventCalendar
from utils.readers import ExcelReader
from utils.traveling import (read_rates_config,
                             create_first_driver_rider,
                             find_closest_driver,
                             find_closest_rider,
                             calculate_distance)


# Configure logging
logging.basicConfig(
    filename='ride_simulation.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='w'  # Overwrites the log file each time the script runs
)

# Ensure the output text file is overwritten each time the script runs
with open("ride_simulation_output.txt", "w") as log_file:
    log_file.write("")

def log_and_print(message):
    print(message)
    logging.info(message)
    with open("ride_simulation_output.txt", "a") as log_file:
        log_file.write(message + "\n")


def first_event(rates):

    first_driver, first_rider = create_first_driver_rider(rates)
    ec = EventCalendar()
    ec.add_event(first_driver, {
        'type': 'driver', 'events': 'available'})
    ec.add_event(first_rider, {
        'type': 'rider', 'events': 'available'})

    return ec

def new_drivers(id, time, ec):
    driver = Driver(id=f'd_{id}',
                    current_location=None,
                    origin=None,
                    become_available=time,
                    offline_time=np.inf,
                    status='IDLING',
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
                  status='Waiting')
    next_driver_time = rider.generating_rider(ec, rates, time)
    ec.add_event(next_driver_time, {
        'type': 'rider', 'events': 'available'})
    id += 1
    return rider, id


def process_available_driver(driver, t_now, ec, available_riders, available_drivers, rates):
    """Handles both 'available' and 'searching_for_rider' events for drivers."""
    driver.searching_for_rider(ec, t_now)
    log_and_print(f'Driver {driver.id} is just available at {t_now}')
    
    # If there are available riders, match the driver with the closest rider
    if available_riders.is_not_empty():
        closest_rider = available_riders.find_closest_rider(driver)
        driver.picking_up(closest_rider, ec, t_now, rates)
        available_riders.remove_rider(closest_rider.id)
        log_and_print(f'Matched driver {driver.id} with rider {closest_rider.id}, rider location: {closest_rider.current_location}')
    # If there are no available riders, add the driver to the available drivers pool
    else:
        driver.status = 'IDLING'
        available_drivers.add_driver(driver)
        log_and_print(f'Driver {driver.id} is idling at {t_now}, location: {driver.current_location}')


if __name__ == "__main__":
    rates = read_rates_config('configs.yaml')
    np.random.seed(42)
    ec = EventCalendar()
    drivers = {}
    riders = {}
    available_drivers = AvailableDrivers()
    available_riders = AvailableRiders()
    t_now, termination = 0, 120
    driver_id, rider_id = 0, 0
    ec = first_event(rates)

    while t_now < termination:
        event = ec.pop(0)
        t_now = event['time']

        # Process the event
        if event['type']['type'] == 'driver':
            # Check if the driver is available or searching for a rider
            if event['type']['events'] in ['available', 'searching_for_rider']:
                # Create a new driver if available
                if event['type']['events'] == 'available':
                    driver, driver_id = new_drivers(driver_id, t_now, ec)
                    drivers[driver.id] = driver
                # Get existing driver if searching
                else:   driver = drivers.get(event['data']['driver'])  # Get existing driver if searching

                process_available_driver(driver, t_now, ec, available_riders, available_drivers, rates)

            # If the driver is departing
            elif event['type']['events'] == 'departing':

                # Get the driver and rider objects
                driver = drivers[event['data']['driver']]
                rider = riders[event['data']['rider']]
                # Execute the departing method
                driver.departing(rider, ec, t_now, rates)
                log_and_print(f'Driver {driver.id} and riders {rider.id} is departing at {t_now}, location: {driver.current_location} to {rider.destination}')
                # Update the driver and rider dictionaries
                drivers[driver.id] = driver
                riders[rider.id] = rider

            # If the driver is dropping off
            elif event['type']['events'] == 'dropping_off':

                # Get the driver and rider objects
                driver = drivers[event['data']['driver']]
                rider = riders[event['data']['rider']]
                # Execute the dropping off method
                driver.dropping_off(rider, ec, t_now)
                log_and_print(f'Driver {driver.id} is dropping off rider {rider.id} at {t_now}, location: {driver.current_location}')
                #  Search for a new rider
                driver.searching_for_rider(ec, t_now)

                # Update the driver and rider dictionaries
                drivers[driver.id] = driver
                riders[rider.id] = rider

            # If the driver is going offline
            elif event['type']['events'] == 'offline':
                driver = drivers[event['data']['driver']]
                # Check if the driver is idling or dropping off
                if driver.status == 'IDLING':
                    driver.stopped_working()
                    driver.status = 'offline'
                    log_and_print(f'Driver {event["data"]["driver"]} is going offline at {t_now}')
                else:
                    # If the driver is dropping off, go offline after dropping off
                    ec.add_event(driver.current_trip.time_arrival, 'driver', {'events': 'offline', 'driver': driver.id})   
                    log_and_print(f'Driver {event["data"]["driver"]} is dropping off and then going offline at {t_now}')

        # If the event is a rider event
        elif event['type']['type'] == 'rider':
            # If the rider is available
            if event['type']['events'] == 'available':
                # Create a new rider and queue the next rider event
                rider, rider_id = new_riders(rider_id, t_now, ec)
                log_and_print(f'Rider {rider.id} is available at {t_now}, location: {rider.current_location}')

                # If there are available drivers, match the rider with the closest driver
                if available_drivers.is_not_empty():
                    closest_driver = available_drivers.find_closest_driver(rider)
                    closest_driver.picking_up(rider, ec, t_now, rates)
                    available_drivers.remove_driver(closest_driver.id)
                    log_and_print(f'Matched driver {closest_driver.id} with rider {rider.id}, rider location: {rider.current_location}')
                # If there are no available drivers, add the rider to the available riders pool
                else:
                    available_riders.add_rider(rider)
                    log_and_print(f'Rider {rider.id} is waiting at {t_now}, location: {rider.current_location}')
                riders[rider.id] = rider
            
            # If the rider is abandoning the ride
            elif event['type']['events'] == 'cancel':
                rider = riders[event['data']['rider']]
                if rider.status == 'Waiting':
                    rider.status = 'abandoned'
                    riders[rider.id] = rider
                    log_and_print(f'Rider {rider.id} has abandoned the ride at {t_now}, location: {rider.current_location}')




# This just works for one customer but we need to now relate the driver and rider assignment logic
# potential way to implement it
# def process_driver_event(self, driver):
#    if driver.status == DriverState.IDLING:
#        self.assign_trip(driver)
#    elif driver.status == DriverState.PICK_UP:
#        self.start_trip(driver)
#    elif driver.status == DriverState.DROPOFF:
#        self.complete_trip(driver)


# Need a way to keep track of the model and validate -> Suggestion add logging mechanism of some sort
# potential make a new df which logs the assignment of drivers, and status at real time
# add a unique ID for each rider and driver, eg: driver AB111 -> Rider PUN123 Driver_status:Progress
# (if rider sits its in progress)
# so we might need a new state called as transitioning state or in progress state i.e ride-in-progress
# This seems like real time monitoring/logging ig
# need to look more into this would potential find a way to get it by sunday 2359
# todo: Rider-driver matching logic
# completing or abandoning logic for rider-driver
# loop to make this work for our required time period   