import random
import numpy as np
import pandas as pd
from dataclasses import dataclass
from utils.traveling import generate_random_value


@dataclass
class Driver:
    id: int
    current_location: tuple[float, float]
    origin: tuple[float, float]
    become_available: float = np.inf
    offline_time: float = np.inf
    status: str = "OFFLINE"
    earnings: float = 0.0
    current_trip: object = None

    @classmethod
    def from_dataset(cls, row):
        """Create Driver from dataset row"""
        return cls(
            id=row['id'],
            location=eval(row['initial_location']),
            available_start=pd.to_datetime(
                row['arrival_datetime']).timestamp(),
            available_end=pd.to_datetime(row['offline_datetime']).timestamp()
        )

    def generating_driver(self, rates, time):
        # id = time?
        # suggestion string + time + location (the possibility of ID clashing reduces a really low number)

        # another suggestion would be to generate alot of drivers and Riders before we start our code
        # what i mean is that we find a max(no of rider and drivers) and just generate them at the start
        # Later we are just randomly dumping them on the map i.e we run the simulations
        # The ids are predefined which will allow updating and tracking the more convinent
        # Adding or pregenerating would require us to calculate arrival times at the start, would increase
        # simulation time, and memory consumption, the benefit is that we dont need to worry about clashes
        # use something like this for pre-generation
        # drivers = [Driver(id=f"DRV-{i:04d}") for i in range(10000)] #we can dump this in config file
        # later after each iteration we call this in our core file
        # we use hybrid sort of activation, we dont need to actively track drivers who are inactive
        # nor track riders who are done, we just append it in a different df.

        time = generate_random_value(rates['drivers']['inter_arrival'])
        corr = generate_random_value(rates['map_density'], size=2)
        jobs_time = generate_random_value(rates['drivers']['jobs_time'])

        self.current_location = corr
        self.origin = corr
        self.offline_time = time + jobs_time

        return time

    def traveling(self):
        if self.status == 'idling':
            self.status = 'pick_up'
            return None
        # potential logical error ? "==" instead of "=" ?
        # im assuming the usage of == here means we are comparing the status, but shouldnt we make it
        # compare of status idle, if idle we set to pickup so it would become something like
        #  if self.status == 'idling':
        #   self.status = 'pick_up'
        #   return None

        elif self.status == 'pick_up':
            self.status = 'dropoff'
            return None


# Relating driver status to rider and using or more like assigning numbers would be better no?
# class DriverState():
#    OFFLINE = 0
#    IDLING = 1
#    PICK_UP = 2
#    DROPOFF = 3

# This might be flawed, im trying to replicate the methodology which you had used for writing code
# @dataclass
# class Driver:
#    status: DriverState = DriverState.OFFLINE
