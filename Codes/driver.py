import random
import numpy as np
from dataclasses import dataclass
from utils.traveling import generate_random_value

@dataclass
class Driver:
    # id: int
    # location: tuple[float, float]
    # available_start: float
    # available_end: float
    # status: str = "OFFLINE" 
    # earnings: float = 0.0
    # current_trip: object = None

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
        return time, corr
    

    def traveling(self):
        if self.status == 'idling':
            self.status == 'pick_up'
            return None
        
        elif self.status == 'pick_up':
            self.status == 'dropoff'
            return None

            
