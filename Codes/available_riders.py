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
        """Finds the closest rider to the given driver.
        
        If the driver is in pre_search mode and has an active trip, the distance
        is computed using the driver's drop-off destination as the reference point.
        Otherwise, the Euclidean distance is computed from the driver's current location.
        """
        if not self.riders:
            return None

        rider_ids = list(self.riders.keys())
        effective_distances = []
        for rider in self.riders.values():
            if hasattr(driver, 'pre_search') and driver.pre_search and driver.current_trip:
                # Use the drop-off destination directly
                effective_distance = calculate_distance(
                    driver.current_trip['destination'][0], driver.current_trip['destination'][1],
                    rider.current_location[0], rider.current_location[1]
                )
            else:
                effective_distance = calculate_distance(
                    driver.current_location[0], driver.current_location[1],
                    rider.current_location[0], rider.current_location[1]
                )
            effective_distances.append(effective_distance)

        closest_index = np.argmin(effective_distances)
        return self.riders[rider_ids[closest_index]], effective_distances[closest_index]
    