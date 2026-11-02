# things which generaly store data. objects in the domain model

# we could assign object references as attributes to define the relations.
#   we just assign unique_ids. 
#   no code here actually enforces the one:many type relationships defined on UML diagram.
#   this will be the job of a database connector.
#       end user will not have access to individual instances of the defined object.
#           thank you. subscribe, leave thumbs up and most importantly:
#                                                               take an effin shower.

# this one for timeslot starts and ends
from datetime import date, time


# auto __repr__ __str__ methods etc.
from dataclasses import dataclass

# from enum import Enum such that you can use enums 
from enum import Enum

class RoomType(Enum):
    LAB = 1
    AUDITORIUM = 2
    CLASSROOM = 3

class ReservationStatus(Enum):
    ACTIVE = 1
    CANCELED = 2

@dataclass
class Room:
    id: int
    name: str
    capacity: int
    type: RoomType

@dataclass
class TimeSlot:
    id: int
    start_time: time
    end_time: time

    def __post_init__(self):
        if self.end_time <= self.start_time: # BUT WHAT ABOUT MIDNIGHT THO
            raise ValueError("End time must be after start time.")

@dataclass
class StaffMember:
    id: int
    name: str

@dataclass
class Reservation:
    id: int
    room_id: int
    status: ReservationStatus
    time_slot_id: int 
    day: date
    owner_id: int #of StaffMember


    


