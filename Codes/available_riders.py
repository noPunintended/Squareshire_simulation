import numpy as np
from utils.traveling import calculate_distance


class AvailableRiders:
    def __init__(self):
        self.riders = {}

    def is_not_empty(self):
        return len(self.riders) > 0

    def add_rider(self, rider):
        """Adds a rider to the waiting pool."""
        self.riders[rider.id] = rider

    def remove_rider(self, rider_id):
        """Removes a rider from the waiting pool."""
        if rider_id in self.riders:
            del self.riders[rider_id]

    def get_all_rider_locations(self):
        """Returns all available rider IDs, x-coordinates, and y-coordinates."""
        rider_ids = list(self.riders.keys())
        rider_x = [rider.current_location[0] for rider in self.riders.values()]
        rider_y = [rider.current_location[1] for rider in self.riders.values()]
        return rider_ids, rider_x, rider_y
    

    def find_closest_rider(self, driver):
        """Finds the closest rider using argmin and Euclidean distance"""
        if not self.riders:
            return None

        rider_ids, rider_x, rider_y = self.get_all_rider_locations()
        driver_x, driver_y = driver.current_location

        distances = calculate_distance(driver_x, driver_y, rider_x, rider_y)
        closest_index = np.argmin(distances)  # Get index of closest rider
        return self.riders[rider_ids[closest_index]]  # Return rider object
    