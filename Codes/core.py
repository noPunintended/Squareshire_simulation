import heapq
import pandas as pd
import numpy as np
import bisect
from driver import Driver
from rider import Rider
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


def new_drivers(id, time, ec):

    driver = Driver(id=f'd_{id}', current_location=None, 
                    origins=None, become_available=time
                    offline_time=np.inf, status='IDLING',
                    earnings=0, current_trip=None)
    
    id = id + 1
    next_driver_time, curr_corr, jobs_time = driver.become_available(rates)
    driver.current_location = curr_corr
    driver.origins = curr_corr
    driver.offline_time = time + jobs_time

    return driver


if __name__ == "__main__":
    # riders_path = "data/riders.xlsx"
    # drivers_path = "data/drivers.xlsx"
    # riders = ExcelReader(riders_path)
    # drivers = ExcelReader(drivers_path)
    # riders_df = riders.read_file(sheet_name="Sheet1")
    # drivers_df = drivers.read_file(sheet_name="Sheet1")
    first_driver, first_rider= create_first_driver_rider()

    rates = read_rates_config('configs.yaml')
    np.random.seed(42)
    driver = Driver()
    rider = Rider()
    driver_list = []
    t_now = 0
    termination = 60
    driver_id = 0
    rider_id = 0

    
    first_customer = rider.waiting_pick_up(rates)
    first_customer_dest = rider.create_destination(rates)

    print(first_driver)
    print(first_customer)
    print(first_customer_dest)

#This just works for one customer but we need to now relate the driver and rider assignment logic
#potential way to implement it 
#def process_driver_event(self, driver):
#    if driver.status == DriverState.IDLING:
#        self.assign_trip(driver)
#    elif driver.status == DriverState.PICK_UP:
#        self.start_trip(driver)
#    elif driver.status == DriverState.DROPOFF:
#        self.complete_trip(driver)


#Need a way to keep track of the model and validate -> Suggestion add logging mechanism of some sort
#potential make a new df which logs the assignment of drivers, and status at real time
#add a unique ID for each rider and driver, eg: driver AB111 -> Rider PUN123 Driver_status:Progress 
# (if rider sits its in progress)
#so we might need a new state called as transitioning state or in progress state i.e ride-in-progress
#This seems like real time monitoring/logging ig
# need to look more into this would potential find a way to get it by sunday 2359
#todo: Rider-driver matching logic
# completing or abandoning logic for rider-driver
# loop to make this work for our required time period