import pytest
from unittest.mock import patch
from rich.table import Table
from models.fields import Note
from models.record import Record
from models.address_book import AddressBook
from handlers.note_handlers import (
    add_note, edit_note, delete_note,
    show_notes, show_all_notes, all_with_notes, find_notes,
    _next_note_id,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def make_book(*contacts):
    book = AddressBook()
    for name, phone in contacts:
        r = Record(name)
        r.add_phone(phone)
        book.add_record(r)
    return book


def add_notes_to(book, name, *texts):
    """Add notes via handler so IDs are assigned correctly."""
    for text in texts:
        add_note([name] + text.split(), book)


# =============================================================================
# Note field
# =============================================================================

def test_note_valid():
    n = Note("Buy milk", 1)
    assert n.value == "Buy milk"
    assert n.id == 1

def test_note_stripped():
    n = Note("  Buy milk  ", 1)
    assert n.value == "Buy milk"

def test_note_empty_raises():
    with pytest.raises(ValueError):
        Note("", 1)

def test_note_whitespace_only_raises():
    with pytest.raises(ValueError):
        Note("   ", 1)

def test_note_str():
    assert str(Note("hello", 5)) == "hello"


# =============================================================================
# Record.add_note / edit_note / delete_note  (ID-based API)
# =============================================================================

def test_record_add_note():
    r = Record("Alice")
    r.add_note("Call back", 1)
    assert len(r.notes) == 1
    assert r.notes[0].value == "Call back"
    assert r.notes[0].id == 1

def test_record_add_multiple_notes_different_ids():
    r = Record("Alice")
    r.add_note("First", 1)
    r.add_note("Second", 2)
    assert len(r.notes) == 2
    assert r.notes[0].id == 1
    assert r.notes[1].id == 2

def test_record_add_note_empty_raises():
    r = Record("Alice")
    with pytest.raises(ValueError):
        r.add_note("", 1)

def test_record_edit_note_by_id():
    r = Record("Alice")
    r.add_note("Old text", 42)
    r.edit_note(42, "New text")
    assert r.notes[0].value == "New text"
    assert r.notes[0].id == 42

def test_record_edit_note_wrong_id_raises():
    r = Record("Alice")
    r.add_note("Text", 1)
    with pytest.raises(IndexError):
        r.edit_note(99, "New")

def test_record_edit_note_empty_text_raises():
    r = Record("Alice")
    r.add_note("Text", 1)
    with pytest.raises(ValueError):
        r.edit_note(1, "")

def test_record_delete_note_by_id():
    r = Record("Alice")
    r.add_note("First", 1)
    r.add_note("Second", 2)
    r.delete_note(1)
    assert len(r.notes) == 1
    assert r.notes[0].id == 2

def test_record_delete_last_note():
    r = Record("Alice")
    r.add_note("Only", 1)
    r.delete_note(1)
    assert len(r.notes) == 0

def test_record_delete_note_wrong_id_raises():
    r = Record("Alice")
    r.add_note("Text", 1)
    with pytest.raises(IndexError):
        r.delete_note(99)


# =============================================================================
# _next_note_id
# =============================================================================

def test_next_note_id_empty_book():
    assert _next_note_id(AddressBook()) == 1

def test_next_note_id_after_one_note():
    book = make_book(("Alice", "1234567890"))
    add_note(["Alice", "hello"], book)
    assert _next_note_id(book) == 2

def test_next_note_id_across_contacts():
    book = make_book(("Alice", "1234567890"), ("Bob", "0987654321"))
    add_note(["Alice", "note one"], book)
    add_note(["Bob", "note two"], book)
    add_note(["Alice", "note three"], book)
    assert _next_note_id(book) == 4

def test_next_note_id_unique_after_delete():
    book = make_book(("Alice", "1234567890"))
    add_note(["Alice", "first"], book)
    add_note(["Alice", "second"], book)
    note_id = book.find("Alice").notes[0].id
    with patch("builtins.input", return_value=str(note_id)):
        delete_note(["Alice"], book)
    # ID продолжает расти, не переиспользуется
    assert _next_note_id(book) == 3


# =============================================================================
# add_note handler
# =============================================================================

def test_add_note_success():
    book = make_book(("Alice", "1234567890"))
    result = add_note(["Alice", "Buy", "milk"], book)
    assert "added" in result
    assert book.find("Alice").notes[0].value == "Buy milk"

def test_add_note_returns_correct_id():
    book = make_book(("Alice", "1234567890"))
    result = add_note(["Alice", "first"], book)
    assert "#1" in result
    result2 = add_note(["Alice", "second"], book)
    assert "#2" in result2

def test_add_note_ids_unique_across_contacts():
    book = make_book(("Alice", "1234567890"), ("Bob", "0987654321"))
    add_note(["Alice", "note A"], book)
    result = add_note(["Bob", "note B"], book)
    assert "#2" in result

def test_add_note_contact_not_found():
    result = add_note(["Nobody", "text"], AddressBook())
    assert "Error" in result

def test_add_note_missing_text():
    book = make_book(("Alice", "1234567890"))
    result = add_note(["Alice"], book)
    assert "Error" in result

def test_add_note_no_args():
    result = add_note([], AddressBook())
    assert "Error" in result

def test_add_note_whitespace_text():
    book = make_book(("Alice", "1234567890"))
    result = add_note(["Alice", "   "], book)
    assert "Error" in result


# =============================================================================
# edit_note handler (interactive via input())
# =============================================================================

def test_edit_note_success():
    book = make_book(("Alice", "1234567890"))
    add_note(["Alice", "Old text"], book)
    note_id = book.find("Alice").notes[0].id
    with patch("builtins.input", side_effect=[str(note_id), "New text"]):
        result = edit_note(["Alice"], book)
    assert "updated" in result
    assert book.find("Alice").notes[0].value == "New text"

def test_edit_note_contact_not_found():
    result = edit_note(["Nobody"], AddressBook())
    assert "Error" in result

def test_edit_note_no_notes():
    book = make_book(("Alice", "1234567890"))
    result = edit_note(["Alice"], book)
    assert "Error" in result

def test_edit_note_non_numeric_id():
    book = make_book(("Alice", "1234567890"))
    add_note(["Alice", "Some text"], book)
    with patch("builtins.input", side_effect=["abc"]):
        result = edit_note(["Alice"], book)
    assert "Error" in result

def test_edit_note_wrong_id():
    book = make_book(("Alice", "1234567890"))
    add_note(["Alice", "Text"], book)
    with patch("builtins.input", side_effect=["999", "New text"]):
        result = edit_note(["Alice"], book)
    assert "Error" in result

def test_edit_note_empty_new_text():
    book = make_book(("Alice", "1234567890"))
    add_note(["Alice", "Text"], book)
    note_id = book.find("Alice").notes[0].id
    with patch("builtins.input", side_effect=[str(note_id), ""]):
        result = edit_note(["Alice"], book)
    assert "Error" in result

def test_edit_note_no_args():
    result = edit_note([], AddressBook())
    assert "Error" in result


# =============================================================================
# delete_note handler (interactive via input())
# =============================================================================

def test_delete_note_success():
    book = make_book(("Alice", "1234567890"))
    add_note(["Alice", "To delete"], book)
    note_id = book.find("Alice").notes[0].id
    with patch("builtins.input", return_value=str(note_id)):
        result = delete_note(["Alice"], book)
    assert "deleted" in result
    assert len(book.find("Alice").notes) == 0

def test_delete_note_contact_not_found():
    result = delete_note(["Nobody"], AddressBook())
    assert "Error" in result

def test_delete_note_no_notes():
    book = make_book(("Alice", "1234567890"))
    result = delete_note(["Alice"], book)
    assert "Error" in result

def test_delete_note_non_numeric_id():
    book = make_book(("Alice", "1234567890"))
    add_note(["Alice", "Text"], book)
    with patch("builtins.input", return_value="abc"):
        result = delete_note(["Alice"], book)
    assert "Error" in result

def test_delete_note_wrong_id():
    book = make_book(("Alice", "1234567890"))
    add_note(["Alice", "Text"], book)
    with patch("builtins.input", return_value="999"):
        result = delete_note(["Alice"], book)
    assert "Error" in result

def test_delete_note_no_args():
    result = delete_note([], AddressBook())
    assert "Error" in result


# =============================================================================
# show_notes handler
# =============================================================================

def test_show_notes_returns_table():
    book = make_book(("Alice", "1234567890"))
    add_notes_to(book, "Alice", "First", "Second")
    assert isinstance(show_notes(["Alice"], book), Table)

def test_show_notes_no_notes():
    book = make_book(("Alice", "1234567890"))
    result = show_notes(["Alice"], book)
    assert "No notes" in result

def test_show_notes_contact_not_found():
    result = show_notes(["Nobody"], AddressBook())
    assert "Error" in result

def test_show_notes_no_args():
    result = show_notes([], AddressBook())
    assert "Error" in result


# =============================================================================
# show_all_notes handler
# =============================================================================

def test_show_all_notes_returns_table():
    book = make_book(("Alice", "1234567890"))
    add_notes_to(book, "Alice", "A note")
    assert isinstance(show_all_notes([], book), Table)

def test_show_all_notes_empty():
    result = show_all_notes([], AddressBook())
    assert "No notes" in result

def test_show_all_notes_multiple_contacts():
    book = make_book(("Alice", "1234567890"), ("Bob", "0987654321"))
    add_notes_to(book, "Alice", "Alice note")
    add_notes_to(book, "Bob", "Bob note")
    assert isinstance(show_all_notes([], book), Table)

def test_show_all_notes_no_notes_in_contacts():
    book = make_book(("Alice", "1234567890"), ("Bob", "0987654321"))
    result = show_all_notes([], book)
    assert "No notes" in result


# =============================================================================
# all_with_notes handler
# =============================================================================

def test_all_with_notes_returns_table():
    book = make_book(("Alice", "1234567890"))
    assert isinstance(all_with_notes([], book), Table)

def test_all_with_notes_empty_book():
    result = all_with_notes([], AddressBook())
    assert "No contacts" in result

def test_all_with_notes_includes_contacts_without_notes():
    book = make_book(("Alice", "1234567890"), ("Bob", "0987654321"))
    add_notes_to(book, "Alice", "Has a note")
    result = all_with_notes([], book)
    assert isinstance(result, Table)


# =============================================================================
# find_notes handler
# =============================================================================

def test_find_notes_match():
    book = make_book(("Alice", "1234567890"))
    add_notes_to(book, "Alice", "Buy milk")
    assert isinstance(find_notes(["milk"], book), Table)

def test_find_notes_no_match():
    book = make_book(("Alice", "1234567890"))
    add_notes_to(book, "Alice", "Buy milk")
    assert "No notes found" in find_notes(["dentist"], book)

def test_find_notes_case_insensitive():
    book = make_book(("Alice", "1234567890"))
    add_notes_to(book, "Alice", "Buy MILK")
    assert isinstance(find_notes(["milk"], book), Table)

def test_find_notes_partial_match():
    book = make_book(("Alice", "1234567890"))
    add_notes_to(book, "Alice", "Important meeting")
    assert isinstance(find_notes(["import"], book), Table)

def test_find_notes_multiword_query():
    book = make_book(("Alice", "1234567890"))
    add_notes_to(book, "Alice", "Buy milk tomorrow")
    assert isinstance(find_notes(["milk tomorrow"], book), Table)

def test_find_notes_multiple_contacts():
    book = make_book(("Alice", "1234567890"), ("Bob", "0987654321"))
    add_notes_to(book, "Alice", "Buy milk")
    add_notes_to(book, "Bob", "drink milk")
    assert isinstance(find_notes(["milk"], book), Table)

def test_find_notes_empty_book():
    assert "No notes found" in find_notes(["anything"], AddressBook())

def test_find_notes_no_args():
    assert "Error" in find_notes([], AddressBook())
