import random
from dataclasses import dataclass
from pandas import pd

@dataclass
class Driver:
    id: int
    location: tuple[float, float]
    available_start: float
    available_end: float
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
