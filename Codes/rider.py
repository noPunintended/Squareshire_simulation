import random
import numpy as np
from dataclasses import dataclass
from utils.traveling import generate_random_value


@dataclass
class Rider:

    id: int
    current_location: tuple[float, float]
    origin: tuple[float, float]
    destination: tuple[float, float]
    become_available: float = np.inf
    patience_time: float = np.inf
    wait_till_match: float = np.inf
    total_wait_time: float = 0.0
    status: str = "OFFLINE"
    driver: str = None
    pick_up_time: float = np.inf
    destination_time: float = np.inf
    offline_time: float = np.inf

    @classmethod
    def from_dataset(cls, row):
        """Create Rider from dataset row"""
        return cls(
            id=row['id'],
            origin=eval(row['pickup_location']),
            destination=eval(row['dropoff_location']),
            request_time=pd.to_datetime(row['request_datetime']).timestamp(),
            patience=random.expovariate(5) if pd.isna(
                row['pickup_datetime']) else None
        )
    # expovariate(5) seems incorrect since config states otherwise, wont this mean they would be really fast?
    # change it to expovariate(1/300) since config specifices 300s no?
    # can include it in config file itself and call it, but since its an expo do we really need it?
    # potential improvement would be trying out different random generations for patience time aswell!

    def waiting_pick_up(self, rates):

        time = generate_random_value(rates['riders']['inter_arrival'])
        corr_x = generate_random_value(rates['map']['rider_origin_x'])
        corr_y = generate_random_value(rates['map']['rider_origin_y'])
        corr = np.array([corr_x, corr_y])
        return time, corr

    def create_destination(self, rates):
        corr_x = generate_random_value(rates['map']['rider_destination_x'])
        corr_y = generate_random_value(rates['map']['rider_destination_y'])
        corr = np.array([corr_x, corr_y])

        return corr

    def generating_rider(self, ec, rates, time):

        n_time = generate_random_value(rates['riders']['inter_arrival'])
        origin_corr_x = generate_random_value(rates['map']['rider_origin_x'])
        origin_corr_y = generate_random_value(rates['map']['rider_origin_y'])
        origin_corr = np.array([origin_corr_x, origin_corr_y])
        dest_corr_x = generate_random_value(rates['map']['rider_destination_x'])
        dest_corr_y = generate_random_value(rates['map']['rider_destination_y'])
        dest_corr = np.array([dest_corr_x, dest_corr_y])
        patience_time = generate_random_value(rates['riders']['wait_time'])

        self.current_location = origin_corr
        self.origin = origin_corr
        self.destination = dest_corr
        self.patience_time = patience_time
        self.status = 'waiting'
        ec.add_event(time + patience_time, {
            'type': 'rider', 'events': 'cancel'}, {'rider': self.id})

        return time + n_time
    

# Are we using the same method to generate start and end points for rider?

# insert transistion logic here?
# def cancel_ride(self):
#    if self.status == "waiting":
#        self.status = "CANCELLED"

# def complete_ride(self):
#    if self.status == "MATCHED":
#        self.status = "COMPLETED"
