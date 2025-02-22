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
        If a driver is flagged as pre_search (i.e. near drop-off), the effective distance is computed as:
          remaining drop-off distance + distance from drop-off destination to rider.
        Breaks ties by slightly adjusting distance with (1 / waiting_time) * epsilon.
        """
        if not self.drivers:
            return None

        driver_ids = list(self.drivers.keys())
        adjusted_distances = []
        
        # Iterate over each available driver to compute an effective distance
        for driver in self.drivers.values():
            if hasattr(driver, 'pre_search') and driver.pre_search and driver.current_trip:
                # Calculate the remaining drop-off distance
                remaining_distance = calculate_distance(
                    driver.current_location[0], driver.current_location[1],
                    driver.current_trip['destination'][0], driver.current_trip['destination'][1]
                )
                # Calculate the pickup distance from drop-off destination to the rider
                pickup_distance = calculate_distance(
                    driver.current_trip['destination'][0], driver.current_trip['destination'][1],
                    rider.current_location[0], rider.current_location[1]
                )
                effective_distance = remaining_distance + pickup_distance
            else:
                effective_distance = calculate_distance(
                    rider.current_location[0], rider.current_location[1],
                    driver.current_location[0], driver.current_location[1]
                )
            
            # Adjust the effective distance based on the driver's waiting_time
            if driver.waiting_time > 0:
                adjustment = (1 / (driver.waiting_time + 1e-9)) * epsilon
            else:
                adjustment = 0
            adjusted_distances.append(effective_distance + adjustment)

        # Find and return the driver with the minimum adjusted distance
        closest_index = np.argmin(adjusted_distances)
        return self.drivers[driver_ids[closest_index]], adjusted_distances[closest_index]