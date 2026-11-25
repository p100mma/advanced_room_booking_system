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
tests/test_booking.py::test_create_reservation PASSED                                                            [ 11%]
tests/test_booking.py::test_room_cannot_be_booked_twice_for_same_slot PASSED                                     [ 22%]
tests/test_booking.py::test_overlapping_slots_are_rejected PASSED                                                [ 33%]
tests/test_booking.py::test_adjacent_slots_are_allowed PASSED                                                    [ 44%]
tests/test_booking.py::test_different_rooms_can_be_booked_at_same_time PASSED                                    [ 55%]
tests/test_booking.py::test_cancelled_reservation_does_not_block_room PASSED                                     [ 66%]
tests/test_booking.py::test_invalid_room_is_rejected PASSED                                                      [ 77%]
tests/test_booking.py::test_invalid_staff_member_is_rejected PASSED                                              [ 88%]
tests/test_timetable.py::test_timetable_csv_generates_reservations PASSED                                        [100%]
```


### Dodatkowe uwagi

W projekcie brakuje pliku `main.py`, ale to tylko szkielet demonstracyjny.
Tak samo, baza danych oraz implementacja ui na ten moment jest pusta, ale struktura projektu oddaje założoną architerkturę do zaimplementowania.

 Dodatkowo, logika `TimeSlot -- reservation` (godzina akademicka, rezerwacja) jest do dopracowania.


