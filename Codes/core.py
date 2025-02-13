import heapq
import pandas as pd
import numpy as np
import bisect
import logging
from driver import Driver
from rider import Rider
from bisect import bisect_right
from typing import Callable, List, Dict, Any
from utils.readers import ExcelReader
from utils.traveling import (read_rates_config,
                             create_first_driver_rider,
                             find_closest_driver,
                             find_closest_rider)


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


class EventCalendar(list):
    def add_event(self, event_time: float, event_type: str, event_data: Any = None):
        event = {'time': event_time, 'type': event_type, 'data': event_data}
        index = bisect_right([e['time'] for e in self], event_time)
        self.insert(index, event)
        return self


def first_event(rates):

    first_driver, first_rider = create_first_driver_rider(rates)
    ec = EventCalendar()
    ec.add_event(first_driver, {
        'type': 'driver', 'events': 'available'})
    ec.add_event(first_rider, {
        'type': 'rider', 'events': 'available'})

    return ec


class EventCalendar(list):
    def add_event(self, event_time: float, event_type: str, event_data: Any = None):
        event = {'time': event_time, 'type': event_type, 'data': event_data}
        index = bisect_right([e['time'] for e in self], event_time)
        self.insert(index, event)
        return self

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

if __name__ == "__main__":
    rates = read_rates_config('configs.yaml')
    np.random.seed(42)
    ec = EventCalendar()
    drivers = {}
    riders = {}
    available_driver_id, available_driver_x, available_driver_y = [], [], []
    available_rider_id, available_rider_x, available_rider_y = [], [], []
    t_now, termination = 0, 120
    driver_id, rider_id = 0, 0
    ec = first_event(rates)

    while t_now < termination:
        event = ec.pop(0)
        t_now = event['time']

        if event['type']['type'] == 'driver':
            if event['type']['events'] == 'available':
                driver, driver_id = new_drivers(driver_id, t_now, ec)
                driver.searching_for_rider(ec, t_now)
                log_and_print(f'Driver {driver.id} is just available at {t_now}')
                
                if available_rider_id:
                    rider_args = find_closest_rider(driver, available_rider_x, available_rider_y)
                    closest_rider = riders[available_rider_id[rider_args]]
                    driver.picking_up(closest_rider, ec, t_now, rates)
                    available_rider_id.pop(rider_args)
                    available_rider_x.pop(rider_args)
                    available_rider_y.pop(rider_args)
                    log_and_print(f'Matched driver {driver.id} with rider {closest_rider.id}, rider location: {closest_rider.current_location}')
                else:
                    driver.status = 'IDLING'
                    available_driver_id.append(driver.id)
                    available_driver_x.append(driver.current_location[0])
                    available_driver_y.append(driver.current_location[1])
                    log_and_print(f'Driver {driver.id} is idling at {t_now}, location: {driver.current_location}')
                drivers[driver.id] = driver

            elif event['type']['events'] == 'searching_for_rider':

                print(f'driver_id: {event["data"]["driver"]} is searching for a rider at {t_now}')
                driver = drivers[event['data']['driver']]
                driver.searching_for_rider(ec, t_now)
                if len(available_rider_id) > 0:
                    rider_args = find_closest_rider(
                        driver, available_rider_x, available_rider_y)
                    closest_rider = riders[available_rider_id[rider_args]]
                    driver.picking_up(closest_rider, ec, t_now, rates)
                    # Need to update the driver status
                    # Need to update the rider status as well
                    available_rider_id.pop(rider_args)
                    available_rider_x.pop(rider_args)
                    available_rider_y.pop(rider_args)
                    log_and_print(f'Matched driver {driver.id} with rider {closest_rider.id}, rider location: {closest_rider.current_location}')

                else:  # Driver is idle
                    driver.status = 'IDLING'
                    available_driver_id.append(driver.id)
                    available_driver_x.append(driver.current_location[0])
                    available_driver_y.append(driver.current_location[1])
                    log_and_print(f'Driver {driver.id} is idling at {t_now}, location: {driver.current_location}')

                drivers[driver.id] = driver

            elif event['type']['events'] == 'departing':

                driver = drivers[event['data']['driver']]
                rider = riders[event['data']['rider']]
                driver.departing(rider, ec, t_now, rates)
                log_and_print(f'Driver {driver.id} and riders {rider.id} is departing at {t_now}, location: {driver.current_location} to {rider.destination}')
                drivers[driver.id] = driver
                riders[rider.id] = rider

            elif event['type']['events'] == 'dropping_off':

                driver = drivers[event['data']['driver']]
                rider = riders[event['data']['rider']]
                driver.dropping_off(rider, ec, t_now)
                log_and_print(f'Driver {driver.id} is dropping off rider {rider.id} at {t_now}, location: {driver.current_location}')
                driver.searching_for_rider(ec, t_now)

                drivers[driver.id] = driver
                riders[rider.id] = rider

            elif event['type']['events'] == 'offline':
                driver = drivers[event['data']['driver']]
                if driver.status == 'IDLING':
                    driver.stopped_working()
                    driver.status = 'offline'
                    log_and_print(f'Driver {event["data"]["driver"]} is going offline at {t_now}')
                else:
                    ec.add_event(driver.current_trip.time_arrival, 'driver', {'events': 'offline', 'driver': driver.id})   
                    log_and_print(f'Driver {event["data"]["driver"]} is dropping off and then going offline at {t_now}')

        elif event['type']['type'] == 'rider':
            if event['type']['events'] == 'available':
                rider, rider_id = new_riders(rider_id, t_now, ec)
                log_and_print(f'Rider {rider.id} is available at {t_now}, location: {rider.current_location}')
                if available_driver_id:
                    driver_args = find_closest_driver(available_driver_x, available_driver_y, rider)
                    closest_driver = drivers[available_driver_id[driver_args]]
                    closest_driver.picking_up(rider, ec, t_now, rates)
                    available_driver_id.pop(driver_args)
                    available_driver_x.pop(driver_args)
                    available_driver_y.pop(driver_args)
                    log_and_print(f'Matched driver {closest_driver.id} with rider {rider.id}, rider location: {rider.current_location}')
                else:
                    available_rider_id.append(rider.id)
                    available_rider_x.append(rider.current_location[0])
                    available_rider_y.append(rider.current_location[1])
                    log_and_print(f'Rider {rider.id} is waiting at {t_now}, location: {rider.current_location}')
                riders[rider.id] = rider
            
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