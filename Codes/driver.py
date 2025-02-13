import random
import numpy as np
import pandas as pd
from dataclasses import dataclass
from utils.traveling import generate_random_value, calculate_fare, calculate_travel


@dataclass
class Driver:
    id: int
    current_location: tuple[float, float]
    origin: tuple[float, float]
    become_available: float = np.inf
    offline_time: float = np.inf
    status: str = "OFFLINE"
    earnings: float = 0.0
    current_trip: dict = None

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
        n_time = generate_random_value(rates['drivers']['inter_arrival']) #what values would it generate? Assuming size is 1
        corr = generate_random_value(rates['map_density'], size=2)
        jobs_time = generate_random_value(rates['drivers']['jobs_time']) #is this the maximum time we can work for?

        self.current_location = corr
        self.origin = corr
        self.offline_time = time + jobs_time
    #include the total time a single driver would be generated? 
        return time + n_time

    def picking_up(self, rider, ec, time, rates):
        distance, expected_travel_time, actual_travel_time, travel_rates = calculate_travel(
            self.current_location[0], self.current_location[1], rider.origin[0], rider.origin[1], rates)
        self.current_trip = {
            'origin': self.current_location, 
            'destination': rider.origin,
            'distance': distance,
            'expected_travel_time': expected_travel_time,
            'actual_travel_time': actual_travel_time,
            'travel_rates': travel_rates,
            'time_departure': time,
            'time_arrival': time + actual_travel_time
        }
        self.status = 'picking_up'  
        rider.status = 'matched'
        ec.add_event(time + actual_travel_time, {
            'type': 'driver', 'events': 'departing'}, {'driver': self.id, 'rider': rider.id})
        return None

    def departing(self, rider, ec, time, rates):
        self.current_location = self.current_trip['destination']
        distance, expected_travel_time, actual_travel_time, travel_rates = calculate_travel(
            self.current_location[0], self.current_location[1], rider.destination[0], rider.destination[1], rates)
        self.current_trip = {
            'origin': self.current_location,
            'destination': rider.destination,
            'distance': distance,
            'expected_travel_time': expected_travel_time,
            'actual_travel_time': actual_travel_time,
            'travel_rates': travel_rates,
            'time_departure': time,
            'time_arrival': time + actual_travel_time,
            'fare': calculate_fare(distance, rates)
        }
        self.status = 'departing'
        rider.status = 'riding'
        ec.add_event(time + actual_travel_time, {
            'type': 'driver', 'events': 'dropping_off'}, {'driver': self.id, 'rider': rider.id})
        
        return None

    def dropping_off(self, rider, ec, time):
        print(self)
        self.current_location = self.current_trip['destination']
        self.earnings += self.current_trip['fare']
        self.current_trip = {}
        self.status = 'dropping_off'
        rider.status = 'dropped_off'
        ec.add_event(time, {
            'type': 'driver', 'events': 'searching_for_rider'}, {'driver': self.id})
        
        return None

    def searching_for_rider(self, ec, time): #we start this when driver becomes available no?
        self.status = 'searching_for_rider'
        return None

    def stop_working(self):
        self.status = 'OFFLINE'
# are we considering the random distribution to include or making people go offline ? if yes where is this being done,
#we need to consider if a driver is working then he stays online for 5 to 8hrs if and if he is going to go offline 
#but still has a last ride we driver finishes and goes offline, basically he is available for some time
        return None

    #def driver_disappear(self):
    #    if self.status == 'departing' or self.status == 'dropping_off':
    #       #the logic is to introduce that a driver can disappear between 5 to 8 uniform random distribution


#order which we have in this code?
#generate driver --> They become available for a random time (we get an idea of the time they are avaible for)
# ---> Now once available we track or search for riders ----> We pick up riders (travel to pick up)
# ----> Once picked up we depart ----> We travel to drop off location ----> we drop off
# ---> After dropping of we calculate the total time we have left (available time left for this driver) and 
# we update the revenue and other factors associated with our driver. ---> We repeat this till the available time of driver runs out
#We now generate a new driver and repeat the steps.

        