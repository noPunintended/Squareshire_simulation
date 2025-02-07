import heapq
import pandas as pd
from driver import Driver
from rider import Rider
from utils.readers import ExcelReader
from utils.traveling import read_rates_config

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


if __name__ == "__main__":
    # riders_path = "data/riders.xlsx"
    # drivers_path = "data/drivers.xlsx"
    # riders = ExcelReader(riders_path)
    # drivers = ExcelReader(drivers_path)
    # riders_df = riders.read_file(sheet_name="Sheet1")
    # drivers_df = drivers.read_file(sheet_name="Sheet1")
    rates = read_rates_config('configs.yaml')
    driver = Driver()
    print(driver.become_available(rates))