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
    

    def find_closest_driver(self, rider, t_now, epsilon=1e-6):
        """Finds the closest driver using Euclidean distance.
        Breaks ties by slightly adjusting distance with (1 / waiting_time) * epsilon.
        """
        if not self.drivers:
            return None

        driver_ids, driver_x, driver_y = self.get_all_driver_locations()
        rider_x, rider_y = rider.current_location

        # Calculate distances
        distances = calculate_distance(rider_x, rider_y, driver_x, driver_y)

        # Adjust distances with a very small value based on (1 / waiting_time)
        adjusted_distances = []
        for i, driver in enumerate(self.drivers.values()):
            if driver.waiting_time > 0:
                adjustment = ((driver.waiting_time + 1e-9)) * epsilon  # Add a small constant
            else:
                adjustment = 0  # Avoid division by zero
            adjusted_distances.append(distances[i] + adjustment)

        # Find the driver with the minimum adjusted distance
        closest_index = np.argmin(adjusted_distances)

        return self.drivers[driver_ids[closest_index]], adjusted_distances[closest_index] # Return driver object