
from datetime import date, time

import pytest

from reserva_de_habitacion.models import (
    Room,
    TimeSlot,
    StaffMember,
    ReservationStatus,
    RoomType
)
from reserva_de_habitacion.services import (
    BookingService,
    RoomUnavailableError,
)


# we define an instance of the BookingService class for testing
#   enclose basically into one function for clarity
# fixture tells the pakcage that THIS FUNCTION prepares data for tests.
@pytest.fixture
def service():
    rooms = [
        Room(1, "A101", 30, RoomType.CLASSROOM),
        Room(2, "A102", 20, RoomType.LAB),
    ]

    slots = [
        TimeSlot(1, time(8, 0), time(9, 30)),
        TimeSlot(2, time(9, 30), time(11, 0)),
        TimeSlot(3, time(9, 0), time(10, 0)),
    ]

    staff = [
        StaffMember(1, "Piotr Stomma"),
        StaffMember(2, "Pedro OneHundredMilimetersAmpers"),
    ]

    return BookingService(
        rooms=rooms,
        time_slots=slots,
        staff_members=staff,
    )

# fixture handles the testing becuase of matching name "service" in the 
#   input argument

def test_create_reservation(service):
    reservation = service.create_reservation(
        room_id=1,
        time_slot_id=1,
        owner_id=1,
        day=date(2026, 11, 10),
    )

    assert reservation.id == 1
    assert reservation.room_id == 1
    assert reservation.owner_id == 1
    assert reservation.status == ReservationStatus.ACTIVE

#passes correctly if RoomUnavailableError is raised

def test_room_cannot_be_booked_twice_for_same_slot(service):
    day = date(2026, 11, 10)

                #room_id, time_slot_id, owner_id, day
    service.create_reservation(1, 1, 1, day)
    #this part enforces the check correctly identified the error.
    with pytest.raises(RoomUnavailableError):
        # same room_id and same time slot on same day.
        # shuld be an error.
        service.create_reservation(1, 1, 2, day)


def test_overlapping_slots_are_rejected(service):
    # in final implementation, reservation should be able
    # to occupy multiple time slots
    # and time slots should not have overlapping times by design.
    #   for now, a simpler version is implemented.
    day = date(2026, 11, 10)

    service.create_reservation(1, 1, 1, day)

    # Slot 3 (09:00–10:00) overlaps with slot 1 (08:00–09:30).
    with pytest.raises(RoomUnavailableError):
        service.create_reservation(1, 3, 2, day)


def test_adjacent_slots_are_allowed(service):
    day = date(2026, 11, 10)

    service.create_reservation(1, 1, 1, day)

    # Slot 2 starts exactly when slot 1 ends.
    reservation = service.create_reservation(1, 2, 2, day)

    assert reservation.status == ReservationStatus.ACTIVE


def test_different_rooms_can_be_booked_at_same_time(service):
    day = date(2026, 11, 10)
    service.create_reservation(1, 1, 1, day)
    reservation = service.create_reservation(2, 1, 2, day)

    assert reservation.room_id == 2


def test_cancelled_reservation_does_not_block_room(service):
    day = date(2026, 11, 10)

    reservation = service.create_reservation(1, 1, 1, day)
    service.cancel_reservation(reservation.id)

    new_reservation = service.create_reservation(1, 1, 2, day)

    assert new_reservation.status == ReservationStatus.ACTIVE


def test_invalid_room_is_rejected(service):
    with pytest.raises(ValueError):
        service.create_reservation(999, 1, 1, date(2026, 11, 10))


def test_invalid_staff_member_is_rejected(service):
    with pytest.raises(ValueError):
        service.create_reservation(1, 1, 999, date(2026, 11, 10))

