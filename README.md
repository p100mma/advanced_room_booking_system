## Sala reservation system

Ten project jest about rezerwacje sali in the university.



### Instrukcja uruchomienia

Używając pythona version number min 3.10

wewnątrz folderu z repozytorium stworzyć najlepiej środowisko wirtualne.

```
python3 -m venv .venv
```

uruchom je (unix):

```
source .venv/bin/activate
```

(win):

```
.venv\Scripts\Activate.ps1
```


Instaluj pakiet: ( specyfikacja `[dev]` instaluje `pytest` - do testowania, zobacz `pyproject.toml`)

```
python -m pip install -e ".[dev]"
```


Uruchom testy:

```
pytest -v
```

Powinno przejść:

```
configfile: pyproject.toml
collected 8 items

tests/test_booking.py::test_create_reservation PASSED
tests/test_booking.py::test_room_cannot_be_booked_twice_for_same_slot PASSED
tests/test_booking.py::test_overlapping_slots_are_rejected PASSED
tests/test_booking.py::test_adjacent_slots_are_allowed PASSED
tests/test_booking.py::test_different_rooms_can_be_booked_at_same_time PASSED
tests/test_booking.py::test_cancelled_reservation_does_not_block_room PASSED
tests/test_booking.py::test_invalid_room_is_rejected PASSED
tests/test_booking.py::test_invalid_staff_member_is_rejected PASSED 
```


### Dodatkowe uwagi

W projekcie brakuje pliku `main.py`, ale to tylko szkielet demonstracyjny. Dodatkowo, logika `TimeSlot -- reservation` (godzina akademicka, rezerwacja) jest do dopracowania.


