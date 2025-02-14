from bisect import bisect_right
from typing import Callable, List, Dict, Any


class EventCalendar(list):


    def add_event(self, event_time: float, event_type: str, event_data: Any = None):
        event = {'time': event_time, 'type': event_type, 'data': event_data}
        index = bisect_right([e['time'] for e in self], event_time)
        self.insert(index, event)
        return self