import pytest
from datetime import date, timedelta
from unittest.mock import patch
from models.address_book import AddressBook
from models.record import Record
from handlers.contact_handlers import add_contact, change_contact, delete_contact, remove_phone
from handlers.birthday_handlers import add_birthday, show_birthday, birthdays
from handlers.utils import parse_input, save_data, load_data


def make_book(*contacts):
    book = AddressBook()
    for name, phone in contacts:
        r = Record(name)
        r.add_phone(phone)
        book.add_record(r)
    return book


# =============================================================================
# add_contact
# =============================================================================

def test_add_contact_new():
    book = AddressBook()
    assert add_contact(["Alice", "1234567890"], book) == "Contact added."
    assert book.find("Alice") is not None

def test_add_contact_invalid_name():
    result = add_contact(["Alice1", "1234567890"], AddressBook())
    assert "Error" in result

# BUG: isalpha() отклоняет "Mary Jane" — имена с пробелом должны приниматься
def test_add_contact_name_with_space():
    result = add_contact(["Mary Jane", "1234567890"], AddressBook())
    assert result == "Contact added."  # падает: код возвращает Error

def test_add_contact_invalid_phone():
    result = add_contact(["Alice", "123"], AddressBook())
    assert "Error" in result

def test_add_contact_missing_args():
    assert "Error" in add_contact(["Alice"], AddressBook())

def test_add_contact_no_args():
    assert "Error" in add_contact([], AddressBook())

def test_add_contact_existing_add_phone():
    book = make_book(("Alice", "1234567890"))
    with patch("builtins.input", side_effect=["1"]):
        result = add_contact(["Alice", "0987654321"], book)
    assert result == "Phone added."
    assert book.find("Alice").find_phone("0987654321") is not None

def test_add_contact_existing_replace_phone():
    book = make_book(("Alice", "1234567890"))
    with patch("builtins.input", side_effect=["2", "1"]):
        result = add_contact(["Alice", "0987654321"], book)
    assert result == "Contact updated."
    assert book.find("Alice").find_phone("0987654321") is not None
    assert book.find("Alice").find_phone("1234567890") is None

def test_add_contact_existing_replace_invalid_index():
    book = make_book(("Alice", "1234567890"))
    with patch("builtins.input", side_effect=["2", "abc"]):
        assert "Error" in add_contact(["Alice", "0987654321"], book)

def test_add_contact_existing_replace_out_of_range():
    book = make_book(("Alice", "1234567890"))
    with patch("builtins.input", side_effect=["2", "99"]):
        assert "Error" in add_contact(["Alice", "0987654321"], book)

def test_add_contact_existing_no_phones_choice2():
    book = AddressBook()
    book.add_record(Record("Alice"))
    with patch("builtins.input", side_effect=["2"]):
        assert add_contact(["Alice", "0987654321"], book) == "Phone added."

def test_add_contact_existing_cancel():
    book = make_book(("Alice", "1234567890"))
    with patch("builtins.input", side_effect=["3"]):
        assert add_contact(["Alice", "0987654321"], book) == "Operation cancelled."


# =============================================================================
# change_contact
# =============================================================================

def test_change_contact():
    book = make_book(("Bob", "1234567890"))
    assert change_contact(["Bob", "1234567890", "0987654321"], book) == "Contact updated."
    assert book.find("Bob").find_phone("0987654321") is not None

def test_change_contact_not_found():
    assert change_contact(["Bob", "1234567890", "0987654321"], AddressBook()) == "Error: Contact not found."

def test_change_contact_wrong_old_phone():
    book = make_book(("Bob", "1234567890"))
    assert "Error" in change_contact(["Bob", "0000000000", "0987654321"], book)

def test_change_contact_missing_args():
    book = make_book(("Bob", "1234567890"))
    assert "Error" in change_contact(["Bob", "1234567890"], book)

def test_change_contact_new_phone_invalid():
    book = make_book(("Bob", "1234567890"))
    assert "Error" in change_contact(["Bob", "1234567890", "123"], book)


# =============================================================================
# delete_contact
# =============================================================================

def test_delete_contact():
    book = make_book(("Carol", "1234567890"))
    assert delete_contact(["Carol"], book) == "Contact 'Carol' deleted."
    assert book.find("Carol") is None

def test_delete_contact_not_found():
    assert delete_contact(["Carol"], AddressBook()) == "Error: Contact not found."

def test_delete_contact_missing_args():
    assert "Error" in delete_contact([], AddressBook())


# =============================================================================
# remove_phone
# =============================================================================

def test_remove_phone():
    book = make_book(("Dave", "1234567890"))
    assert remove_phone(["Dave", "1234567890"], book) == "Phone removed."
    assert book.find("Dave").find_phone("1234567890") is None

def test_remove_phone_contact_not_found():
    assert remove_phone(["Dave", "1234567890"], AddressBook()) == "Error: Contact not found."

def test_remove_phone_wrong_number():
    book = make_book(("Dave", "1234567890"))
    assert "Error" in remove_phone(["Dave", "0000000000"], book)

def test_remove_phone_missing_args():
    book = make_book(("Dave", "1234567890"))
    assert "Error" in remove_phone(["Dave"], book)


# =============================================================================
# add_birthday / show_birthday / birthdays
# =============================================================================

def test_add_birthday():
    book = make_book(("Eve", "1234567890"))
    assert add_birthday(["Eve", "15.06.1990"], book) == "Birthday added."
    assert str(book.find("Eve").birthday) == "15.06.1990"

def test_add_birthday_invalid_format():
    book = make_book(("Eve", "1234567890"))
    assert "Error" in add_birthday(["Eve", "1990-06-15"], book)

def test_add_birthday_impossible_date():
    book = make_book(("Eve", "1234567890"))
    assert "Error" in add_birthday(["Eve", "30.02.2000"], book)

def test_add_birthday_contact_not_found():
    assert add_birthday(["Eve", "15.06.1990"], AddressBook()) == "Error: Contact not found."

def test_add_birthday_missing_args():
    book = make_book(("Eve", "1234567890"))
    assert "Error" in add_birthday(["Eve"], book)

def test_add_birthday_overwrites_existing():
    book = make_book(("Eve", "1234567890"))
    add_birthday(["Eve", "15.06.1990"], book)
    add_birthday(["Eve", "20.07.1991"], book)
    assert str(book.find("Eve").birthday) == "20.07.1991"

def test_show_birthday():
    book = make_book(("Eve", "1234567890"))
    add_birthday(["Eve", "15.06.1990"], book)
    assert show_birthday(["Eve"], book) == "15.06.1990"

def test_show_birthday_not_set():
    book = make_book(("Eve", "1234567890"))
    assert "no birthday" in show_birthday(["Eve"], book)

def test_show_birthday_contact_not_found():
    assert show_birthday(["Eve"], AddressBook()) == "Error: Contact not found."

def test_show_birthday_missing_args():
    assert "Error" in show_birthday([], AddressBook())

# BUG: birthdays() принимает только book без args — не соответствует сигнатуре handler(args, book)
def test_birthdays_no_upcoming():
    book = make_book(("Eve", "1234567890"))
    result = birthdays([], book)  # правильная сигнатура как у всех хендлеров — падает
    assert "No birthdays" in result

def test_birthdays_with_upcoming():
    book = make_book(("Eve", "1234567890"))
    soon = date.today() + timedelta(days=2)
    add_birthday(["Eve", soon.strftime("%d.%m.%Y")], book)
    result = birthdays([], book)  # правильная сигнатура как у всех хендлеров — падает
    assert "Eve" in result


# =============================================================================
# parse_input
# =============================================================================

def test_parse_input_simple():
    assert parse_input("hello") == ("hello",)

def test_parse_input_with_args():
    cmd, *args = parse_input("add Alice 1234567890")
    assert cmd == "add"
    assert args == ["Alice", "1234567890"]

def test_parse_input_uppercase_normalized():
    cmd, *_ = parse_input("ADD Alice 1234567890")
    assert cmd == "add"

def test_parse_input_extra_spaces():
    cmd, *args = parse_input("  add   Alice   1234567890  ")
    assert cmd == "add"
    assert args == ["Alice", "1234567890"]


# =============================================================================
# save_data / load_data
# =============================================================================

def test_save_and_load_data(tmp_path):
    filepath = str(tmp_path / "book.pkl")
    book = make_book(("Alice", "1234567890"))
    save_data(book, filepath)
    loaded = load_data(filepath)
    assert loaded.find("Alice").find_phone("1234567890") is not None

def test_load_data_file_not_found(tmp_path):
    result = load_data(str(tmp_path / "nonexistent.pkl"))
    assert isinstance(result, AddressBook)
    assert len(result.data) == 0

def test_save_and_load_preserves_birthday(tmp_path):
    filepath = str(tmp_path / "book.pkl")
    book = make_book(("Alice", "1234567890"))
    add_birthday(["Alice", "01.01.1990"], book)
    save_data(book, filepath)
    assert str(load_data(filepath).find("Alice").birthday) == "01.01.1990"
