import pytest

from datetime import date, time
from pathlib import Path

from reserva_de_habitacion.services import load_entries_from_csv
from reserva_de_habitacion.services import TimetableService
from reserva_de_habitacion.services import BookingService
from  reserva_de_habitacion.models import ( 
    Room,
    TimeSlot,
    StaffMember,
    RoomType,
    ReservationStatus,
    TimetableEntry,
    )


@pytest.fixture
def timetable_csv():
    return Path(__file__).parent / "data" / "example_timetable.csv"



@pytest.fixture
def booking_service():
    rooms = [
        Room(1, "A101", 30, RoomType.CLASSROOM),
        Room(2, "A102", 20, RoomType.LAB),
    ]

    slots = [
        TimeSlot(1, time(8, 0), time(9, 30)),
        TimeSlot(2, time(9, 30), time(11, 0)),
        TimeSlot(3, time(9, 0), time(10, 0)),
        TimeSlot(4, time(11, 0), time(12, 30)),
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

def test_timetable_csv_generates_reservations(
    timetable_csv,
    booking_service,
):
    # 1. Load timetable entries from CSV.
    entries = load_entries_from_csv(timetable_csv)

    # 2. Construct the timetable service.
    timetable_service = TimetableService(
        booking_service=booking_service,
        timetable_entries=entries,
    )

    # 3. Generate reservations for the semester.
    result = timetable_service.import_reservations_from_timetable(
        semester_start=date(2026, 10, 1),
        semester_end=date(2026, 10, 31),
    )

    # 4. Check the import summary.
    assert result.created_count == 13
    assert result.conflict_count == 0

    # 5. Check the actual reservations stored by BookingService.
    reservations = list(booking_service.reservations.values())

    assert len(reservations) == 13
    assert all(
        reservation.status == ReservationStatus.ACTIVE
        for reservation in reservations
    )

    # Check that reservations belong to the expected rooms and staff.
    assert {r.room_id for r in reservations} == {1, 2}
    assert {r.owner_id for r in reservations} == {1, 2}

    # All generated reservations should fall within October.
    assert all(
        date(2026, 10, 1) <= r.day <= date(2026, 10, 31)
        for r in reservations
    )
