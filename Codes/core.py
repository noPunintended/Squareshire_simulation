import heapq
import pandas as pd
import numpy as np
import bisect
from driver import Driver
from rider import Rider
from bisect import bisect_right
from typing import Callable, List, Dict, Any
from utils.readers import ExcelReader
from utils.traveling import read_rates_config, create_first_driver_rider


class RideSimulation:
    def __init__(self):
        self.event_queue = []
        self.current_time = 0.0
        self.available_drivers = []
        self.waiting_riders = []
        self.active_trips = []
        self.metrics = {
            'total_riders': 0,
            'abandoned': 0,
            'completed': 0,
            'driver_earnings': {}
        }

    def load_data(self, driver_path, rider_path):

        drivers_df = pd.read_excel(driver_path)
        riders_df = pd.read_excel(rider_path)


def add_event(event_calendar, event_time: float, event_type: str, event_data: Any = None):
    event = {'time': event_time, 'type': event_type, 'data': event_data}
    index = bisect_right([e['time'] for e in event_calendar], event_time)
    event_calendar.insert(index, event)

    return event_calendar


def new_drivers(id, time, ec):

    id = id + 1
    driver = Driver(id=f'd_{id}',
                    current_location=None,
                    origin=None, become_available=time,
                    offline_time=np.inf, status='IDLING',
                    earnings=0, current_trip=None)
    print(driver)
    next_driver_time = driver.generating_driver(rates, time)
    ec = add_event(ec, next_driver_time, {
                   'type': 'driver', 'events': 'first_available'})

    return driver


def new_riders(id, time, ec):

    id = id + 1
    rider = Rider(id: id
                  current_location=None
                  origin=None
                  destination=None
                  become_available=time
                  patience_time=np.inf
                  status='Waiting')
    next_driver_time = rider.generating_rider(rates, time)
    ec = add_event(ec, next_driver_time, {
                   'type': 'rider', 'events': 'available'})

    return rider


if __name__ == "__main__":

    rates = read_rates_config('configs.yaml')
    np.random.seed(42)
    ec = []
    t_now = 0
    termination = 60
    driver_id = 0
    rider_id = 0

    first_driver, first_rider = create_first_driver_rider(rates)
    ec = add_event(ec, first_driver, {
                   'type': 'driver', 'events': 'first_available'})
    ec = add_event(ec, first_rider, {'type': 'rider', 'events': 'available'})

    print(ec)
    print(new_drivers(driver_id, 5, ec))
    print(new_riders(rider_id, 6, ec))
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
