import numpy as np
from utils.traveling import calculate_distance


class AvailableDrivers:
    def __init__(self):
        self.drivers = {}

    def is_not_empty(self):
        return len(self.drivers) > 0


    def add_driver(self, driver):
        """Adds a driver to the available pool."""
        self.drivers[driver.id] = driver

    def remove_driver(self, driver_id):
        """Removes a driver from the available pool."""
        if driver_id in self.drivers:
            del self.drivers[driver_id]

    def get_all_driver_locations(self):
        """Returns all available driver IDs, x-coordinates, and y-coordinates."""
        driver_ids = list(self.drivers.keys())
        driver_x = [driver.current_location[0] for driver in self.drivers.values()]
        driver_y = [driver.current_location[1] for driver in self.drivers.values()]
        return driver_ids, driver_x, driver_y
    

    def find_closest_driver(self, rider):
        """Finds the closest driver using argmin and Euclidean distance"""
        if not self.drivers:
            return None
        
        driver_ids, driver_x, driver_y = self.get_all_driver_locations()
        rider_x, rider_y = rider.current_location

        distances = calculate_distance(rider_x, rider_y, driver_x, driver_y)
        closest_index = np.argmin(distances)  # Get index of closest driver
        return self.drivers[driver_ids[closest_index]]  # Return driver object