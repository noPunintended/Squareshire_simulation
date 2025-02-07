import random
from dataclasses import dataclass
from utils.traveling import generate_random_value

@dataclass
class Rider:
    # id: int
    # origin: tuple[float, float]
    # destination: tuple[float, float]
    # request_time: float
    # patience: float = None
    # status: str = "WAITING"  # WAITING | MATCHED | CANCELLED | COMPLETED

    @classmethod
    def from_dataset(cls, row):
        """Create Rider from dataset row"""
        return cls(
            id=row['id'],
            origin=eval(row['pickup_location']),
            destination=eval(row['dropoff_location']),
            request_time=pd.to_datetime(row['request_datetime']).timestamp(),
            patience=random.expovariate(5) if pd.isna(row['pickup_datetime']) else None
        )
    

    def waiting_pick_up(self, rates):

        time = generate_random_value(rates['riders']['inter_arrival'])
        corr = generate_random_value(rates['map_density'], size=2)
        return time, corr


    def create_destination(self, rates):
        
        return generate_random_value(rates['map_density'], size=2)
