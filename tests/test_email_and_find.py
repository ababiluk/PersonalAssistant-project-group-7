import pytest
from rich.table import Table
from models.fields import Email
from models.record import Record
from models.address_book import AddressBook
from handlers.contact_handlers import add_email, find_contact


def make_book(*contacts):
    book = AddressBook()
    for name, phone in contacts:
        r = Record(name)
        r.add_phone(phone)
        book.add_record(r)
    return book


# =============================================================================
# Email field
# =============================================================================

def test_email_valid():
    e = Email("user@example.com")
    assert e.value == "user@example.com"

def test_email_valid_with_dots():
    e = Email("first.last@mail.org")
    assert e.value == "first.last@mail.org"

def test_email_valid_with_plus():
    e = Email("user+tag@example.com")
    assert e.value == "user+tag@example.com"

def test_email_valid_subdomain():
    e = Email("user@sub.domain.com")
    assert e.value == "user@sub.domain.com"

def test_email_no_at_raises():
    with pytest.raises(ValueError):
        Email("userexample.com")

def test_email_no_domain_raises():
    with pytest.raises(ValueError):
        Email("user@")

def test_email_no_local_part_raises():
    with pytest.raises(ValueError):
        Email("@example.com")

def test_email_no_tld_raises():
    with pytest.raises(ValueError):
        Email("user@example")

def test_email_empty_raises():
    with pytest.raises(ValueError):
        Email("")

def test_email_spaces_raises():
    with pytest.raises(ValueError):
        Email("user @example.com")

def test_email_double_at_raises():
    with pytest.raises(ValueError):
        Email("user@@example.com")

def test_email_str():
    assert str(Email("a@b.com")) == "a@b.com"


# =============================================================================
# Record.add_email
# =============================================================================

def test_record_add_email():
    r = Record("Alice")
    r.add_email("alice@example.com")
    assert r.email.value == "alice@example.com"

def test_record_add_email_invalid_raises():
    r = Record("Alice")
    with pytest.raises(ValueError):
        r.add_email("not-an-email")

def test_record_add_email_overwrites():
    r = Record("Alice")
    r.add_email("old@example.com")
    r.add_email("new@example.com")
    assert r.email.value == "new@example.com"


# =============================================================================
# add_email handler
# =============================================================================

def test_add_email_success():
    book = make_book(("Alice", "1234567890"))
    result = add_email(["Alice", "alice@example.com"], book)
    assert result == "Email added."
    assert book.find("Alice").email.value == "alice@example.com"

def test_add_email_contact_not_found():
    result = add_email(["Nobody", "x@x.com"], AddressBook())
    assert result == "Error: Contact not found."

def test_add_email_invalid_format():
    book = make_book(("Alice", "1234567890"))
    result = add_email(["Alice", "not-an-email"], book)
    assert "Error" in result

def test_add_email_missing_args():
    book = make_book(("Alice", "1234567890"))
    result = add_email(["Alice"], book)
    assert "Error" in result

def test_add_email_no_args():
    result = add_email([], AddressBook())
    assert "Error" in result

def test_add_email_overwrites_existing():
    book = make_book(("Alice", "1234567890"))
    add_email(["Alice", "old@example.com"], book)
    add_email(["Alice", "new@example.com"], book)
    assert book.find("Alice").email.value == "new@example.com"


# =============================================================================
# find_contact handler
# =============================================================================

def test_find_contact_by_exact_name():
    book = make_book(("Alice", "1234567890"))
    result = find_contact(["Alice"], book)
    assert isinstance(result, Table)

def test_find_contact_by_partial_name():
    book = make_book(("Alice", "1234567890"), ("Bob", "0987654321"))
    result = find_contact(["Ali"], book)
    assert isinstance(result, Table)

def test_find_contact_case_insensitive():
    book = make_book(("Alice", "1234567890"))
    result = find_contact(["alice"], book)
    assert isinstance(result, Table)

def test_find_contact_by_phone():
    book = make_book(("Alice", "1234567890"))
    result = find_contact(["123456"], book)
    assert isinstance(result, Table)

def test_find_contact_by_partial_phone():
    book = make_book(("Alice", "1234567890"))
    result = find_contact(["7890"], book)
    assert isinstance(result, Table)

def test_find_contact_no_match():
    book = make_book(("Alice", "1234567890"))
    result = find_contact(["Zzz"], book)
    assert result == "No contacts found."

def test_find_contact_empty_book():
    result = find_contact(["Alice"], AddressBook())
    assert result == "No contacts found."

def test_find_contact_multiple_results():
    book = make_book(("Alice", "1234567890"), ("Alicia", "0987654321"))
    result = find_contact(["Ali"], book)
    assert isinstance(result, Table)

def test_find_contact_no_args():
    result = find_contact([], AddressBook())
    assert "Error" in result
