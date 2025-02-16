import random
import numpy as np
import pandas as pd
from dataclasses import dataclass
from utils.traveling import generate_random_value, calculate_fare, calculate_travel
from dataclasses import dataclass, field

@dataclass
class Driver:
    id: int
    current_location: tuple[float, float]
    origin: tuple[float, float]
    become_available: float = np.inf
    offline_time: float = np.inf
    status: str = "OFFLINE"
    matched_rider: str = None
    earnings: float = 0.0
    current_trip: dict = None
    going_offline: bool = False
    number_of_trips: int = 0
    fuel_cost: float = 0.0
    total_pickup_distance: float = 0.0
    total_dropoff_distance: float = 0.0
    total_distance: float = 0.0
    past_pickup: list = field(default_factory=list) 
    past_trip: list = field(default_factory=list)
    past_fares: list = field(default_factory=list)
    past_riders: list = field(default_factory=list)
    past_locations: list = field(default_factory=list)

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
        self.past_locations.append(corr)
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
            'time_arrival': time + actual_travel_time,
            'matched_rider': rider.id
        }
        self.status = 'picking_up'
        self.past_riders.append(rider.id)
        rider.status = 'matched'
        rider.driver = self.id
        ec.add_event(time + actual_travel_time, {
            'type': 'driver', 'events': 'departing'}, {'driver': self.id, 'rider': rider.id})
        return None

    def departing(self, rider, ec, time, rates):
        self.current_location = self.current_trip['destination']
        self.fuel_cost += self.current_trip['distance'] * rates['drivers']['petrol_cost']
        self.total_pickup_distance += self.current_trip['distance']
        self.total_distance += self.current_trip['distance']
        self.past_pickup.append((self.current_trip['origin'], self.current_trip['destination']))
        self.past_locations.append(self.current_location)
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
            'fare': calculate_fare(distance, rates),
            'matched_rider': rider.id
        }
        self.status = 'departing'
        rider.status = 'riding'
        rider.pick_up_time = time
        ec.add_event(time + actual_travel_time, {
            'type': 'driver', 'events': 'dropping_off'}, {'driver': self.id, 'rider': rider.id})
        self.number_of_trips += 1
        return None

    def dropping_off(self, rider, ec, time, rates):
        self.current_location = self.current_trip['destination']
        self.fuel_cost += self.current_trip['distance'] * rates['drivers']['petrol_cost']
        self.total_dropoff_distance += self.current_trip['distance']
        self.total_distance += self.current_trip['distance']
        self.past_trip.append((self.current_trip['origin'], self.current_trip['destination']))
        self.past_locations.append(self.current_location)
        self.earnings += self.current_trip['fare']
        self.past_fares.append(self.current_trip['fare'])
        self.current_trip = {}
        self.status = 'dropping_off'
        rider.status = 'reached_destination'
        if not self.going_offline:
            ec.add_event(time, {
                'type': 'driver', 'events': 'searching_for_rider'}, {'driver': self.id})
        rider.destination_time = time
        
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

        