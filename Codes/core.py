import heapq
import pandas as pd
from .driver import Driver
from .rider import Rider

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