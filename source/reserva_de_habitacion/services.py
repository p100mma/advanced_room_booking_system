
from datetime import date
from collections.abc import Iterable

# current workdir
from .models import (
    Room,
    TimeSlot,
    StaffMember,
    Reservation,
    ReservationStatus,
)


#this is currently responsible BOTH for logic and in memory storage
#   as project grows, storage should be delegated to separate database.
#   data does not survive application restart.


class RoomUnavailableError(Exception):
    """Raised when a room is already booked for the requested period."""



class BookingService:
    def __init__( #currently all data is  stored here as fields with plain dicts. ID: object.
                  # inputs are iterables of objects (such as lists)
                  # and index_by_id converts them to dictionaries indexed by object ids.
        self,
        rooms: Iterable[Room] = (), 
        time_slots: Iterable[TimeSlot] = (), 
        staff_members: Iterable[StaffMember] = (), 
        reservations: Iterable[Reservation] = (),
    ):
        self.rooms = self._index_by_id(rooms)
        self.time_slots = self._index_by_id(time_slots)
        self.staff_members = self._index_by_id(staff_members)
        self.reservations = self._index_by_id(reservations)

        self._next_reservation_id = (             #for auto assignment of ned reservations 
            max(self.reservations, default=0) + 1
        )

    @staticmethod           
    def _index_by_id(items):
        result = {}
        for item in items:
            if item.id in result: #unique id check 
                raise ValueError(f"Duplicate ID: {item.id}")
            result[item.id] = item
        return result

    # for the end user to see the selections

    def list_rooms(self) -> list[Room]:
        return list(self.rooms.values())

    def list_time_slots(self) -> list[TimeSlot]:
        return list(self.time_slots.values())

    # checks the correctness of the user input
    def is_available( self, room_id: int,
                            time_slot_id: int,
                            day:date,) -> bool:

        if room_id not in self.rooms:
            raise ValueError(f"Unknown room id {room_id}")

        if time_slot_id  not in self.time_slots:
            raise ValueError(f"Unknown time slot id {room_id}")

        requested_slot= self.time_slots[time_slot_id]
        for existing in self.reservations.values():
            if (
                existing.status == ReservationStatus.ACTIVE
                and existing.room_id == room_id
                and existing.day == day
            ): #check only active reservations done on the same day of the same room.
                existing_slot = self.time_slots[existing.time_slot_id]

                # there is an overlap if:
                #   requested start time is before existing end time
                #   existing start time is before requested end time.

                overlaps = (
                    requested_slot.start_time < existing_slot.end_time
                    and existing_slot.start_time < requested_slot.end_time
                )

                if overlaps:
                    return False #not available

        return True

    def create_reservation(
        self,
        room_id: int,
        time_slot_id: int,
        owner_id: int,
        day: date,
    ) -> Reservation:
        if owner_id not in self.staff_members:
            raise ValueError(f"Unknown staff member ID: {owner_id}")


        if not self.is_available(room_id, time_slot_id, day):
            raise RoomUnavailableError("ZAJENTE")

        requested_slot = self.time_slots[time_slot_id]

        # Check whether the room is already booked
        # during any overlapping time interval on that day.

        reservation = Reservation(
            id=self._next_reservation_id,
            room_id=room_id,
            status=ReservationStatus.ACTIVE,
            time_slot_id=time_slot_id,
            day=day,
            owner_id=owner_id,
        )

        self.reservations[reservation.id] = reservation
        self._next_reservation_id += 1

        return reservation

    def cancel_reservation(self, reservation_id: int) -> None:
        reservation = self.reservations.get(reservation_id)

        if reservation is None:
            raise ValueError(
                f"Unknown reservation ID: {reservation_id}"
            )

        if reservation.status == ReservationStatus.CANCELED:
            raise ValueError("Reservation is already canceled.")

        reservation.status = ReservationStatus.CANCELED

    def get_reservation(self, reservation_id: int) -> Reservation:
        reservation = self.reservations.get(reservation_id) #simply call dict "get"

        if reservation is None: #with additional check
            raise ValueError(
                f"Unknown reservation ID: {reservation_id}"
            )

        return reservation

