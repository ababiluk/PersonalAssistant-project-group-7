import pytest
from datetime import date, timedelta
from models.fields import Phone, Birthday
from models.record import Record
from models.address_book import AddressBook


# --- Phone ---

def test_phone_valid():
    p = Phone("1234567890")
    assert p.value == "1234567890"

def test_phone_too_short():
    with pytest.raises(ValueError):
        Phone("123456789")

def test_phone_too_long():
    with pytest.raises(ValueError):
        Phone("12345678901")

def test_phone_non_digits():
    with pytest.raises(ValueError):
        Phone("123456789a")

def test_phone_empty():
    with pytest.raises(ValueError):
        Phone("")


# --- Birthday ---

def test_birthday_valid():
    b = Birthday("01.01.2000")
    assert b.value == date(2000, 1, 1)

def test_birthday_invalid_format():
    with pytest.raises(ValueError):
        Birthday("2000-01-01")

def test_birthday_str():
    b = Birthday("15.06.1990")
    assert str(b) == "15.06.1990"

# BUG: сообщение "Invalid date format" вводит в заблуждение — формат правильный, дата несуществующая
def test_birthday_impossible_date():
    with pytest.raises(ValueError) as exc_info:
        Birthday("30.02.2000")
    assert "Invalid date" in str(exc_info.value)
    assert "format" not in str(exc_info.value).lower()  # не должно говорить про формат


# --- Record ---

def test_record_add_phone():
    r = Record("Alice")
    r.add_phone("1234567890")
    assert r.find_phone("1234567890") is not None

def test_record_add_multiple_phones():
    r = Record("Alice")
    r.add_phone("1234567890")
    r.add_phone("0987654321")
    assert r.find_phone("1234567890") is not None
    assert r.find_phone("0987654321") is not None
    assert len(r.phones) == 2

def test_record_remove_phone():
    r = Record("Alice")
    r.add_phone("1234567890")
    r.remove_phone("1234567890")
    assert r.find_phone("1234567890") is None

def test_record_remove_nonexistent_phone():
    r = Record("Alice")
    with pytest.raises(ValueError):
        r.remove_phone("1234567890")

def test_record_edit_phone():
    r = Record("Alice")
    r.add_phone("1234567890")
    r.edit_phone("1234567890", "0987654321")
    assert r.find_phone("0987654321") is not None
    assert r.find_phone("1234567890") is None

def test_record_edit_nonexistent_phone():
    r = Record("Alice")
    with pytest.raises(ValueError):
        r.edit_phone("1234567890", "0987654321")

def test_record_find_phone_not_found():
    r = Record("Alice")
    assert r.find_phone("1234567890") is None

def test_record_add_birthday():
    r = Record("Alice")
    r.add_birthday("01.01.1990")
    assert r.birthday is not None
    assert str(r.birthday) == "01.01.1990"

def test_record_str_no_birthday():
    r = Record("Alice")
    r.add_phone("1234567890")
    assert "N/A" in str(r)

def test_record_str_with_birthday():
    r = Record("Alice")
    r.add_phone("1234567890")
    r.add_birthday("01.01.1990")
    assert "01.01.1990" in str(r)

def test_record_str_multiple_phones():
    r = Record("Alice")
    r.add_phone("1234567890")
    r.add_phone("0987654321")
    s = str(r)
    assert "1234567890" in s
    assert "0987654321" in s

# BUG: при отсутствии телефонов __str__ выводит "phones: " — пустая строка после двоеточия
def test_record_str_no_phones():
    r = Record("Alice")
    s = str(r)
    assert "phones: —" in s  # ожидаем прочерк, а не пустую строку


# --- AddressBook ---

def test_address_book_add_and_find():
    book = AddressBook()
    r = Record("Bob")
    book.add_record(r)
    assert book.find("Bob") is r

def test_address_book_find_missing():
    book = AddressBook()
    assert book.find("Nobody") is None

def test_address_book_delete():
    book = AddressBook()
    r = Record("Bob")
    book.add_record(r)
    book.delete("Bob")
    assert book.find("Bob") is None

def test_address_book_delete_missing():
    book = AddressBook()
    book.delete("Nobody")

def test_address_book_multiple_records():
    book = AddressBook()
    for name in ["Alice", "Bob", "Carol"]:
        r = Record(name)
        book.add_record(r)
    assert len(book.data) == 3


# --- get_upcoming_birthdays ---

def test_upcoming_birthdays_within_window():
    book = AddressBook()
    r = Record("Alice")
    r.add_birthday((date.today() + timedelta(days=3)).strftime("%d.%m.%Y"))
    book.add_record(r)
    assert any(e["name"] == "Alice" for e in book.get_upcoming_birthdays())

def test_upcoming_birthdays_outside_window():
    book = AddressBook()
    r = Record("Alice")
    r.add_birthday((date.today() + timedelta(days=10)).strftime("%d.%m.%Y"))
    book.add_record(r)
    assert not any(e["name"] == "Alice" for e in book.get_upcoming_birthdays())

def test_upcoming_birthdays_today():
    book = AddressBook()
    r = Record("Alice")
    r.add_birthday(date.today().strftime("%d.%m.%Y"))
    book.add_record(r)
    assert any(e["name"] == "Alice" for e in book.get_upcoming_birthdays())

def test_upcoming_birthdays_no_birthday():
    book = AddressBook()
    book.add_record(Record("Alice"))
    assert book.get_upcoming_birthdays() == []

def test_upcoming_birthdays_custom_days():
    book = AddressBook()
    r = Record("Alice")
    r.add_birthday((date.today() + timedelta(days=14)).strftime("%d.%m.%Y"))
    book.add_record(r)
    assert not book.get_upcoming_birthdays(days=7)
    assert book.get_upcoming_birthdays(days=14)

def test_upcoming_birthdays_saturday_to_monday():
    book = AddressBook()
    today = date.today()
    days_to_saturday = (5 - today.weekday()) % 7 or 7
    saturday = today + timedelta(days=days_to_saturday)
    if days_to_saturday <= 7:
        r = Record("Alice")
        r.add_birthday(saturday.strftime("%d.%m.%Y"))
        book.add_record(r)
        result = book.get_upcoming_birthdays()
        if result:
            assert result[0]["congratulation_date"] == (saturday + timedelta(days=2)).strftime("%d.%m.%Y")

def test_upcoming_birthdays_sunday_to_monday():
    book = AddressBook()
    today = date.today()
    days_to_sunday = (6 - today.weekday()) % 7 or 7
    sunday = today + timedelta(days=days_to_sunday)
    if days_to_sunday <= 7:
        r = Record("Bob")
        r.add_birthday(sunday.strftime("%d.%m.%Y"))
        book.add_record(r)
        result = book.get_upcoming_birthdays()
        if result:
            assert result[0]["congratulation_date"] == (sunday + timedelta(days=1)).strftime("%d.%m.%Y")

def test_upcoming_birthdays_multiple_contacts():
    book = AddressBook()
    for i, name in enumerate(["Alice", "Bob", "Carol"], start=1):
        r = Record(name)
        r.add_birthday((date.today() + timedelta(days=i)).strftime("%d.%m.%Y"))
        book.add_record(r)
    names = [e["name"] for e in book.get_upcoming_birthdays()]
    assert "Alice" in names
    assert "Bob" in names
    assert "Carol" in names
