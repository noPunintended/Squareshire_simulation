import numpy as np
from dataclasses import dataclass

@dataclass
class Waiting_Points:
    name: str
    corr: tuple[float, float]

    # Class variable to store predefined waiting points
    # waiting_points = [
    #     {"name": "WP1", "corr": (15, 15)},
    #     {"name": "WP2", "corr": (15, 5)},
    #     {"name": "WP3", "corr": (5, 15)},
    #     {"name": "WP3", "corr": (5, 5)},
    # ]

    waiting_points = [
        {"name": "WP1", "corr": (3.702, 4.448)},
        {"name": "WP2", "corr": (2.978, 11.641)},
        {"name": "WP3", "corr": (10.505, 6.342)},
        {"name": "WP3", "corr": (8.732, 14.030)},
    ]


    @classmethod
    def get_waiting_points(cls):
        """Returns a list of Waiting_Points instances based on stored data."""
        return [cls(name=wp["name"], corr=wp["corr"]) for wp in cls.waiting_points]

    @classmethod
    def find_closest_waiting_point(cls, driver_location):
        """
        Finds the closest waiting point to the driver's location.

        :param driver_location: tuple (lat, lon) of the driver's current location
        :return: Waiting_Points instance closest to the driver
        """
        waiting_points_instances = cls.get_waiting_points()
        
        if not waiting_points_instances:
            return None  # Return None if no waiting points are available

        # Convert driver location to a NumPy array for distance calculations
        driver_loc = np.array(driver_location)

        # Compute distances to all waiting points
        distances = [
            (wp, np.linalg.norm(driver_loc - np.array(wp.corr)))
            for wp in waiting_points_instances
        ]

        # Return the waiting point with the minimum distance
        closest_waiting_point = min(distances, key=lambda x: x[1])[0]
        return closest_waiting_point
