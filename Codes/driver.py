import random
import numpy as np
import pandas as pd
from dataclasses import dataclass
from utils.traveling import generate_random_value

@dataclass
class Driver:
    id: int
    current_location: tuple[float, float]
    origins: tuple[float, float]
    become_available: float
    offline_time: float
    status: str = "OFFLINE" 
    earnings: float = 0.0
    current_trip: object = None

    @classmethod
    def from_dataset(cls, row):
        """Create Driver from dataset row"""
        return cls(
            id=row['id'],
            location=eval(row['initial_location']),
            available_start=pd.to_datetime(row['arrival_datetime']).timestamp(),
            available_end=pd.to_datetime(row['offline_datetime']).timestamp()
        )
    
    def become_available(self, rates):
        # id = time?
        
        time = generate_random_value(rates['drivers']['inter_arrival'])
        corr = generate_random_value(rates['map_density'], size=2)
        jobs_time = generate_random_value(rates['drivers']['jobs_time'])
        return time, corr, jobs_time
    

    def traveling(self):
        if self.status == 'idling':
            self.status = 'pick_up'
            return None
        # potential logical error ? "==" instead of "=" ? 
        #im assuming the usage of == here means we are comparing the status, but shouldnt we make it 
        # compare of status idle, if idle we set to pickup so it would become something like 
        #  if self.status == 'idling':
        #   self.status = 'pick_up'
        #   return None


        elif self.status == 'pick_up':
            self.status = 'dropoff'
            return None

            
#Relating driver status to rider and using or more like assigning numbers would be better no?
#class DriverState():
#    OFFLINE = 0
#    IDLING = 1
#    PICK_UP = 2
#    DROPOFF = 3

#This might be flawed, im trying to replicate the methodology which you had used for writing code
#@dataclass 
#class Driver:
#    status: DriverState = DriverState.OFFLINE
