
from datetime import date, timedelta
from collections.abc import Iterable

# current workdir
from .models import (
    Room,
    TimeSlot,
    StaffMember,
    Reservation,
    ReservationStatus,
    TimetableEntry
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
            raise ValueError(f"Unknown time slot id {time_slot_id}")

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



class TimetableImportResult:
    """Summary of a timetable import operation."""

    def __init__(self):
        self.created = []
        self.conflicts = []

    @property
    def created_count(self):
        return len(self.created)

    @property
    def conflict_count(self):
        return len(self.conflicts)


class TimetableService:
    def __init__(
        self,
        booking_service: BookingService,
        timetable_entries: Iterable[TimetableEntry] = (),
    ):
        self.booking_service = booking_service
        self.timetable_entries = self._index_by_id(timetable_entries)

    @staticmethod
    def _index_by_id(items):
        result = {}

        for item in items:
            if item.id in result:
                raise ValueError(f"Duplicate timetable entry ID: {item.id}")

            result[item.id] = item

        return result

    def list_entries(self):
        """Return all timetable entries."""
        return list(self.timetable_entries.values())

    @staticmethod
    def _get_matching_dates(entry, semester_start, semester_end):
        """
        Generate dates on which a timetable entry takes place.
        Only dates within both the requested semester and the
        timetable entry's own validity period are returned.
        """

        start = max(semester_start, entry.semester_start)
        end = min(semester_end, entry.semester_end)

        if start > end:
            return []

        # Find the first occurrence of the required weekday.
        days_until_weekday = (entry.weekday - start.weekday()) % 7
        current_day = start + timedelta(days=days_until_weekday)

        matching_dates = []

        while current_day <= end:
            matching_dates.append(current_day)
            current_day += timedelta(days=7)

        return matching_dates

    def import_reservations_from_timetable(
        self,
        semester_start: date,
        semester_end: date,
    ) -> TimetableImportResult:
        """
        Create reservations for all timetable entries
        within the selected semester.

        Conflicts are recorded and processing continues.
        """

        if semester_start > semester_end:
            raise ValueError("Semester start must not be after semester end.")

        result = TimetableImportResult()

        for entry in self.timetable_entries.values():

            matching_dates = self._get_matching_dates(
                entry,
                semester_start,
                semester_end,
            )

            for day in matching_dates:

                try:
                    reservation = self.booking_service.create_reservation(
                        room_id=entry.room_id,
                        time_slot_id=entry.time_slot_id,
                        owner_id=entry.owner_id,
                        day=day,
                    )

                    result.created.append(reservation)

                except RoomUnavailableError:
                    result.conflicts.append({
                        "entry_id": entry.id,
                        "course_name": entry.course_name,
                        "room_id": entry.room_id,
                        "day": day,
                        "time_slot_id": entry.time_slot_id,
                    })

        return result


import csv 

def load_entries_from_csv(filename):
    """Read timetable entries from a CSV file."""

    entries = []

    with open(filename, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            entry = TimetableEntry(
                id=int(row["id"]),
                room_id=int(row["room_id"]),
                time_slot_id=int(row["time_slot_id"]),
                owner_id=int(row["owner_id"]),
                weekday=int(row["weekday"]),
                semester_start=date.fromisoformat(row["semester_start"]),
                semester_end=date.fromisoformat(row["semester_end"]),
                course_name=row["course_name"],
            )

            entries.append(entry)

    return entries
