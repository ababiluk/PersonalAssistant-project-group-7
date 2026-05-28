"""
Handler and model tests organised by command group.
Covers: Record model, AddressBook model, all command handlers,
        input parsing, and data persistence.
"""
import pytest
from datetime import date, timedelta
from unittest.mock import patch
from rich.table import Table

import ast
import csv
import json
from pathlib import Path

from prompt_toolkit.document import Document

from models.record import Record
from models.address_book import AddressBook
from handlers.command_meta import COMMAND_META
from handlers.command_hints import CommandCompleter
from handlers.export_handlers import (
    export_book, _record_to_dict, _resolve_path, _export_json, _export_csv,
)
from handlers.contact_handlers import (
    add_contact, change_contact, delete_contact,
    remove_phone, add_email, find_contact,
)
from handlers.birthday_handlers import add_birthday, show_birthday
from handlers.display import (
    display_all, display_phone, display_birthday,
    display_birthdays, show_help, hello_message,
)
from handlers.note_handlers import (
    add_note, edit_note, delete_note,
    show_notes, show_all_notes, all_with_notes,
    find_notes, add_tag, find_by_tag, sort_by_tags,
)
from handlers.utils import parse_input, save_data, load_data


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _make_book(*contacts):
    """Build an AddressBook populated with (name, phone) pairs."""
    book = AddressBook()
    for name, phone in contacts:
        r = Record(name)
        r.add_phone(phone)
        book.add_record(r)
    return book


# =============================================================================
# Record model
# =============================================================================

class TestRecord:

    def test_add_and_find_phone(self):
        r = Record("Alice")
        r.add_phone("1234567890")
        assert r.find_phone("1234567890") is not None

    def test_multiple_phones_stored(self):
        r = Record("Alice")
        r.add_phone("1234567890")
        r.add_phone("0987654321")
        assert len(r.phones) == 2

    def test_remove_phone(self):
        r = Record("Alice")
        r.add_phone("1234567890")
        r.remove_phone("1234567890")
        assert r.find_phone("1234567890") is None

    def test_remove_nonexistent_phone_raises(self):
        with pytest.raises(ValueError):
            Record("Alice").remove_phone("1234567890")

    def test_edit_phone(self):
        r = Record("Alice")
        r.add_phone("1234567890")
        r.edit_phone("1234567890", "0987654321")
        assert r.find_phone("0987654321") is not None
        assert r.find_phone("1234567890") is None

    def test_edit_nonexistent_phone_raises(self):
        with pytest.raises(ValueError):
            Record("Alice").edit_phone("1234567890", "0987654321")

    def test_find_phone_missing_returns_none(self):
        assert Record("Alice").find_phone("1234567890") is None

    def test_add_birthday(self):
        r = Record("Alice")
        r.add_birthday("01.01.1990")
        assert str(r.birthday) == "01.01.1990"

    def test_add_email(self):
        r = Record("Alice")
        r.add_email("alice@example.com")
        assert str(r.email) == "alice@example.com"

    def test_add_note(self):
        r = Record("Alice")
        r.add_note("Buy milk", 1)
        assert r.notes[0].value == "Buy milk"

    def test_edit_note(self):
        r = Record("Alice")
        r.add_note("Old text", 1)
        r.edit_note(1, "New text")
        assert r.notes[0].value == "New text"

    def test_edit_note_wrong_id_raises(self):
        r = Record("Alice")
        r.add_note("text", 1)
        with pytest.raises(IndexError):
            r.edit_note(99, "new")

    def test_delete_note(self):
        r = Record("Alice")
        r.add_note("text", 1)
        r.delete_note(1)
        assert r.notes == []

    def test_delete_note_wrong_id_raises(self):
        with pytest.raises(IndexError):
            Record("Alice").delete_note(99)

    def test_add_tag_to_note(self):
        r = Record("Alice")
        r.add_note("task", 1)
        r.add_tag_to_note(1, "work")
        assert "work" in r.notes[0].tags

    def test_add_tag_wrong_id_raises(self):
        with pytest.raises(IndexError):
            Record("Alice").add_tag_to_note(99, "work")

    def test_str_includes_name_and_phone(self):
        r = Record("Alice")
        r.add_phone("1234567890")
        s = str(r)
        assert "Alice" in s
        assert "1234567890" in s

    def test_str_no_phones_shows_label(self):
        assert "No phones" in str(Record("Alice"))


# =============================================================================
# AddressBook model
# =============================================================================

class TestAddressBook:

    def test_add_and_find_record(self):
        book = AddressBook()
        r = Record("Bob")
        book.add_record(r)
        assert book.find("Bob") is r

    def test_find_missing_returns_none(self):
        assert AddressBook().find("Nobody") is None

    def test_delete_record(self):
        book = _make_book(("Alice", "1234567890"))
        book.delete("Alice")
        assert book.find("Alice") is None

    def test_delete_missing_is_silent(self):
        AddressBook().delete("Nobody")  # must not raise

    def test_multiple_records_stored(self):
        book = _make_book(("Alice", "1111111111"), ("Bob", "2222222222"))
        assert len(book.data) == 2

    # --- get_upcoming_birthdays ---

    def test_birthday_inside_default_window_included(self):
        book = AddressBook()
        r = Record("Alice")
        r.add_birthday((date.today() + timedelta(days=3)).strftime("%d.%m.%Y"))
        book.add_record(r)
        assert any(e["name"] == "Alice" for e in book.get_upcoming_birthdays())

    def test_birthday_outside_window_excluded(self):
        book = AddressBook()
        r = Record("Alice")
        r.add_birthday((date.today() + timedelta(days=10)).strftime("%d.%m.%Y"))
        book.add_record(r)
        assert not book.get_upcoming_birthdays()

    def test_birthday_today_included(self):
        book = AddressBook()
        r = Record("Alice")
        r.add_birthday(date.today().strftime("%d.%m.%Y"))
        book.add_record(r)
        assert any(e["name"] == "Alice" for e in book.get_upcoming_birthdays())

    def test_no_birthday_excluded(self):
        assert _make_book(("Alice", "1234567890")).get_upcoming_birthdays() == []

    def test_custom_window(self):
        book = AddressBook()
        r = Record("Alice")
        r.add_birthday((date.today() + timedelta(days=14)).strftime("%d.%m.%Y"))
        book.add_record(r)
        assert not book.get_upcoming_birthdays(days=7)
        assert book.get_upcoming_birthdays(days=14)

    def test_saturday_birthday_shifted_to_monday(self):
        book = AddressBook()
        today = date.today()
        days_to_sat = (5 - today.weekday()) % 7 or 7
        saturday = today + timedelta(days=days_to_sat)
        if days_to_sat <= 7:
            r = Record("Alice")
            r.add_birthday(saturday.strftime("%d.%m.%Y"))
            book.add_record(r)
            result = book.get_upcoming_birthdays()
            if result:
                expected = (saturday + timedelta(days=2)).strftime("%d.%m.%Y")
                assert result[0]["congratulation_date"] == expected


# =============================================================================
# add command  (fully interactive — all prompts are mocked)
# =============================================================================

class TestAddContactCommand:

    def test_new_contact_created(self):
        book = AddressBook()
        # inputs: name, phone, email (skip), birthday (skip), no address
        with patch("builtins.input", side_effect=["Alice", "1234567890", "", "", "n"]):
            result = add_contact([], book)
        assert book.find("Alice") is not None
        assert "Error" not in result

    def test_new_contact_with_all_optional_fields(self):
        book = AddressBook()
        inputs = ["John", "0987654321", "john@example.com", "15.06.1990", "n"]
        with patch("builtins.input", side_effect=inputs):
            add_contact([], book)
        r = book.find("John")
        assert r is not None
        assert str(r.email) == "john@example.com"
        assert str(r.birthday) == "15.06.1990"

    def test_multi_word_name_accepted(self):
        book = AddressBook()
        with patch("builtins.input", side_effect=["Mary Jane", "1234567890", "", "", "n"]):
            result = add_contact([], book)
        # _validate_name splits on spaces — "Mary Jane" should be valid
        assert book.find("Mary Jane") is not None
        assert "Error" not in result

    def test_existing_contact_add_phone(self):
        book = _make_book(("Alice", "1234567890"))
        # inputs: name → phone → choice 1 (add) → no email → no birthday → no address
        with patch("builtins.input", side_effect=["Alice", "0987654321", "1", "", "", "n"]):
            add_contact([], book)
        assert book.find("Alice").find_phone("0987654321") is not None

    def test_existing_contact_cancel(self):
        book = _make_book(("Alice", "1234567890"))
        with patch("builtins.input", side_effect=["Alice", "0987654321", "3"]):
            result = add_contact([], book)
        assert "cancel" in result.lower()
        assert book.find("Alice").find_phone("0987654321") is None


# =============================================================================
# change command
# =============================================================================

class TestChangeContactCommand:

    def test_phone_updated(self):
        book = _make_book(("Bob", "1234567890"))
        assert change_contact(["Bob", "1234567890", "0987654321"], book) == "Contact updated."
        assert book.find("Bob").find_phone("0987654321") is not None

    def test_contact_not_found(self):
        assert "Error" in change_contact(["Ghost", "1234567890", "0987654321"], AddressBook())

    def test_wrong_old_phone(self):
        book = _make_book(("Bob", "1234567890"))
        assert "Error" in change_contact(["Bob", "0000000000", "0987654321"], book)

    def test_missing_new_phone_arg(self):
        book = _make_book(("Bob", "1234567890"))
        assert "Error" in change_contact(["Bob", "1234567890"], book)

    def test_invalid_new_phone_format(self):
        book = _make_book(("Bob", "1234567890"))
        assert "Error" in change_contact(["Bob", "1234567890", "123"], book)


# =============================================================================
# delete-contact command
# =============================================================================

class TestDeleteContactCommand:

    def test_contact_deleted(self):
        book = _make_book(("Carol", "1234567890"))
        result = delete_contact(["Carol"], book)
        assert "deleted" in result
        assert book.find("Carol") is None

    def test_contact_not_found(self):
        assert "Error" in delete_contact(["Ghost"], AddressBook())

    def test_missing_name_arg(self):
        assert "Error" in delete_contact([], AddressBook())


# =============================================================================
# phone / delete-phone commands
# =============================================================================

class TestPhoneCommands:

    def test_display_phone_returns_table(self):
        book = _make_book(("Dave", "1234567890"))
        assert isinstance(display_phone(["Dave"], book), Table)

    def test_display_phone_contact_not_found(self):
        assert "Error" in display_phone(["Ghost"], AddressBook())

    def test_remove_phone_success(self):
        book = _make_book(("Dave", "1234567890"))
        assert remove_phone(["Dave", "1234567890"], book) == "Phone removed."
        assert book.find("Dave").find_phone("1234567890") is None

    def test_remove_phone_contact_not_found(self):
        assert "Error" in remove_phone(["Ghost", "1234567890"], AddressBook())

    def test_remove_phone_wrong_number(self):
        book = _make_book(("Dave", "1234567890"))
        assert "Error" in remove_phone(["Dave", "0000000000"], book)

    def test_remove_phone_missing_phone_arg(self):
        book = _make_book(("Dave", "1234567890"))
        assert "Error" in remove_phone(["Dave"], book)


# =============================================================================
# add-email command
# =============================================================================

class TestEmailCommands:

    def test_email_added(self):
        book = _make_book(("Eve", "1234567890"))
        result = add_email(["Eve", "eve@example.com"], book)
        assert result == "Email added."
        assert str(book.find("Eve").email) == "eve@example.com"

    def test_invalid_email_format(self):
        book = _make_book(("Eve", "1234567890"))
        assert "Error" in add_email(["Eve", "not-an-email"], book)

    def test_contact_not_found(self):
        assert "Error" in add_email(["Ghost", "x@example.com"], AddressBook())

    def test_missing_email_arg(self):
        book = _make_book(("Eve", "1234567890"))
        assert "Error" in add_email(["Eve"], book)


# =============================================================================
# add-birthday / show-birthday / birthdays commands
# =============================================================================

class TestBirthdayCommands:

    def test_birthday_added(self):
        book = _make_book(("Frank", "1234567890"))
        assert add_birthday(["Frank", "01.01.1990"], book) == "Birthday added."
        assert str(book.find("Frank").birthday) == "01.01.1990"

    def test_birthday_overwrites_existing(self):
        book = _make_book(("Frank", "1234567890"))
        add_birthday(["Frank", "01.01.1990"], book)
        add_birthday(["Frank", "20.07.1991"], book)
        assert str(book.find("Frank").birthday) == "20.07.1991"

    def test_birthday_invalid_format(self):
        book = _make_book(("Frank", "1234567890"))
        assert "Error" in add_birthday(["Frank", "1990-01-01"], book)

    def test_birthday_impossible_date(self):
        book = _make_book(("Frank", "1234567890"))
        assert "Error" in add_birthday(["Frank", "30.02.2000"], book)

    def test_birthday_contact_not_found(self):
        assert "Error" in add_birthday(["Ghost", "01.01.1990"], AddressBook())

    def test_birthday_missing_date_arg(self):
        book = _make_book(("Frank", "1234567890"))
        assert "Error" in add_birthday(["Frank"], book)

    def test_show_birthday_returns_date_string(self):
        book = _make_book(("Frank", "1234567890"))
        add_birthday(["Frank", "01.01.1990"], book)
        assert show_birthday(["Frank"], book) == "01.01.1990"

    def test_show_birthday_not_set(self):
        book = _make_book(("Frank", "1234567890"))
        assert "no birthday" in show_birthday(["Frank"], book)

    def test_show_birthday_contact_not_found(self):
        assert "Error" in show_birthday(["Ghost"], AddressBook())

    def test_display_birthdays_no_upcoming(self):
        result = display_birthdays([], _make_book(("Frank", "1234567890")))
        assert "No birthdays" in result

    def test_display_birthdays_upcoming_returns_table(self):
        book = _make_book(("Frank", "1234567890"))
        soon = (date.today() + timedelta(days=2)).strftime("%d.%m.%Y")
        add_birthday(["Frank", soon], book)
        assert isinstance(display_birthdays([], book), Table)

    def test_display_birthdays_custom_window(self):
        book = _make_book(("Frank", "1234567890"))
        far = (date.today() + timedelta(days=20)).strftime("%d.%m.%Y")
        add_birthday(["Frank", far], book)
        assert "No birthdays" in display_birthdays([], book)          # default 7 days
        assert isinstance(display_birthdays(["30"], book), Table)     # 30-day window


# =============================================================================
# Note commands
# =============================================================================

class TestNoteCommands:

    def test_add_note_success(self):
        book = _make_book(("Grace", "1234567890"))
        result = add_note(["Grace", "Buy", "groceries"], book)
        assert "added" in result
        assert book.find("Grace").notes[0].value == "Buy groceries"

    def test_add_note_contact_not_found(self):
        assert "Error" in add_note(["Ghost", "text"], AddressBook())

    def test_add_note_missing_text(self):
        book = _make_book(("Grace", "1234567890"))
        assert "Error" in add_note(["Grace"], book)

    def test_add_note_missing_name(self):
        assert "Error" in add_note([], AddressBook())

    def test_note_ids_are_globally_unique(self):
        book = _make_book(("Grace", "1234567890"), ("Henry", "0987654321"))
        add_note(["Grace", "first"], book)
        add_note(["Henry", "second"], book)
        all_ids = [n.id for r in book.data.values() for n in r.notes]
        assert len(all_ids) == len(set(all_ids))

    def test_edit_note_success(self):
        book = _make_book(("Grace", "1234567890"))
        add_note(["Grace", "original"], book)
        note_id = book.find("Grace").notes[0].id
        with patch("builtins.input", side_effect=[str(note_id), "updated text"]):
            result = edit_note(["Grace"], book)
        assert "updated" in result
        assert book.find("Grace").notes[0].value == "updated text"

    @pytest.mark.xfail(
        reason="edit_note replaces the Note object with Note(new_text, id), discarding all tags",
        strict=True,
    )
    def test_edit_note_preserves_tags(self):
        book = _make_book(("Grace", "1234567890"))
        add_note(["Grace", "task"], book)
        note_id = book.find("Grace").notes[0].id
        with patch("builtins.input", side_effect=[str(note_id), "work"]):
            add_tag(["Grace"], book)
        with patch("builtins.input", side_effect=[str(note_id), "updated task"]):
            edit_note(["Grace"], book)
        assert "work" in book.find("Grace").notes[0].tags

    def test_edit_note_no_notes(self):
        book = _make_book(("Grace", "1234567890"))
        assert "Error" in edit_note(["Grace"], book)

    def test_delete_note_success(self):
        book = _make_book(("Grace", "1234567890"))
        add_note(["Grace", "to delete"], book)
        note_id = book.find("Grace").notes[0].id
        with patch("builtins.input", return_value=str(note_id)):
            result = delete_note(["Grace"], book)
        assert "deleted" in result
        assert book.find("Grace").notes == []

    def test_show_notes_returns_table(self):
        book = _make_book(("Grace", "1234567890"))
        add_note(["Grace", "some note"], book)
        assert isinstance(show_notes(["Grace"], book), Table)

    def test_show_notes_contact_has_none(self):
        book = _make_book(("Grace", "1234567890"))
        assert "No notes" in show_notes(["Grace"], book)

    def test_show_all_notes_returns_table(self):
        book = _make_book(("Grace", "1234567890"))
        add_note(["Grace", "note"], book)
        assert isinstance(show_all_notes([], book), Table)

    def test_show_all_notes_empty_book(self):
        assert "No notes" in show_all_notes([], AddressBook())

    def test_find_notes_by_text(self):
        book = _make_book(("Grace", "1234567890"))
        add_note(["Grace", "buy milk"], book)
        assert isinstance(find_notes(["milk"], book), Table)

    def test_find_notes_no_match(self):
        book = _make_book(("Grace", "1234567890"))
        add_note(["Grace", "buy milk"], book)
        assert "No notes found" in find_notes(["coffee"], book)


# =============================================================================
# Tag commands
# =============================================================================

class TestTagCommands:

    def _book_with_tagged_note(self, name, note_text, tag):
        book = _make_book((name, "1234567890"))
        add_note([name, note_text], book)
        note_id = book.find(name).notes[0].id
        with patch("builtins.input", side_effect=[str(note_id), tag]):
            add_tag([name], book)
        return book

    def test_add_tag_success(self):
        book = _make_book(("Ivan", "1234567890"))
        add_note(["Ivan", "work task"], book)
        note_id = book.find("Ivan").notes[0].id
        with patch("builtins.input", side_effect=[str(note_id), "work"]):
            result = add_tag(["Ivan"], book)
        assert "work" in result
        assert "work" in book.find("Ivan").notes[0].tags

    def test_add_tag_contact_has_no_notes(self):
        book = _make_book(("Ivan", "1234567890"))
        assert "Error" in add_tag(["Ivan"], book)

    def test_find_by_tag_returns_table(self):
        book = self._book_with_tagged_note("Ivan", "task", "urgent")
        assert isinstance(find_by_tag(["urgent"], book), Table)

    def test_find_by_tag_no_match(self):
        book = _make_book(("Ivan", "1234567890"))
        add_note(["Ivan", "task"], book)
        assert "No notes found" in find_by_tag(["nonexistent"], book)

    def test_sort_by_tags_returns_table(self):
        book = self._book_with_tagged_note("Ivan", "task", "work")
        assert isinstance(sort_by_tags([], book), Table)

    def test_sort_by_tags_no_tagged_notes(self):
        assert "No notes" in sort_by_tags([], AddressBook())

    def test_find_notes_matches_by_exact_tag(self):
        # find-notes searches both note text and tags (exact tag match)
        book = self._book_with_tagged_note("Ivan", "my task", "work")
        assert isinstance(find_notes(["work"], book), Table)


# =============================================================================
# Display commands
# =============================================================================

class TestDisplayCommands:

    def test_display_all_empty_book(self):
        assert "No contacts" in display_all([], AddressBook())

    def test_display_all_returns_table(self):
        assert isinstance(display_all([], _make_book(("Alice", "1234567890"))), Table)

    def test_find_contact_by_exact_name(self):
        book = _make_book(("Alice", "1234567890"))
        assert isinstance(find_contact(["Alice"], book), Table)

    def test_find_contact_partial_name_case_insensitive(self):
        book = _make_book(("Alice", "1234567890"), ("Albert", "0987654321"))
        assert isinstance(find_contact(["al"], book), Table)

    def test_find_contact_by_partial_phone(self):
        book = _make_book(("Alice", "1234567890"))
        assert isinstance(find_contact(["1234"], book), Table)

    def test_find_contact_no_results(self):
        assert "No contacts found" in find_contact(["xyz"], _make_book(("Alice", "1234567890")))

    def test_all_with_notes_empty_book(self):
        assert "No contacts" in all_with_notes([], AddressBook())

    def test_all_with_notes_returns_table(self):
        book = _make_book(("Alice", "1234567890"))
        add_note(["Alice", "test note"], book)
        assert isinstance(all_with_notes([], book), Table)

    def test_display_birthday_returns_table(self):
        book = _make_book(("Alice", "1234567890"))
        add_birthday(["Alice", "01.01.1990"], book)
        assert isinstance(display_birthday(["Alice"], book), Table)

    def test_show_help_returns_table(self):
        assert isinstance(show_help([], AddressBook()), Table)

    def test_show_help_row_count_matches_command_meta(self):
        # "exit" is merged with "close" → one fewer row than COMMAND_META entries
        expected = len(COMMAND_META) - 1
        assert show_help([], AddressBook()).row_count == expected

    def test_show_help_contains_known_commands(self):
        from io import StringIO
        from rich.console import Console
        table = show_help([], AddressBook())
        buf = StringIO()
        Console(file=buf, width=200, force_terminal=False).print(table)
        rendered = buf.getvalue()
        for cmd in ("add", "change", "find", "add-note", "add-tag", "birthdays"):
            assert cmd in rendered

    def test_hello_returns_non_empty_string(self):
        result = hello_message([], AddressBook())
        assert isinstance(result, str) and len(result) > 0


# =============================================================================
# Input parsing
# =============================================================================

class TestParseInput:

    def test_simple_command(self):
        assert parse_input("hello") == ("hello",)

    def test_command_with_args(self):
        cmd, *args = parse_input("add Alice 1234567890")
        assert cmd == "add"
        assert args == ["Alice", "1234567890"]

    def test_command_normalized_to_lowercase(self):
        cmd, *_ = parse_input("ADD Alice")
        assert cmd == "add"

    def test_leading_trailing_spaces_stripped(self):
        cmd, *args = parse_input("  add   Alice   1234567890  ")
        assert cmd == "add"
        assert args == ["Alice", "1234567890"]


# =============================================================================
# Data persistence
# =============================================================================

class TestPersistence:

    def test_save_and_reload(self, tmp_path):
        path = str(tmp_path / "book.pkl")
        book = _make_book(("Alice", "1234567890"))
        save_data(book, path)
        loaded = load_data(path)
        assert loaded.find("Alice").find_phone("1234567890") is not None

    def test_load_missing_file_returns_empty_book(self, tmp_path):
        loaded = load_data(str(tmp_path / "nonexistent.pkl"))
        assert isinstance(loaded, AddressBook)
        assert len(loaded.data) == 0

    def test_persistence_preserves_all_fields(self, tmp_path):
        path = str(tmp_path / "book.pkl")
        book = _make_book(("Alice", "1234567890"))
        add_birthday(["Alice", "01.06.1990"], book)
        add_email(["Alice", "alice@example.com"], book)
        add_note(["Alice", "a note"], book)
        save_data(book, path)
        r = load_data(path).find("Alice")
        assert str(r.birthday) == "01.06.1990"
        assert str(r.email) == "alice@example.com"
        assert r.notes[0].value == "a note"


# =============================================================================
# COMMAND_META contract
# =============================================================================

def _registered_commands():
    """
    Parse commands.py with AST to extract the keys of the 'commands' dict
    without importing the module (importing triggers a circular import via
    handlers/utils.py -> commands.py).
    """
    src = (Path(__file__).parent.parent / "commands.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == "commands" for t in node.targets)
            and isinstance(node.value, ast.Dict)
        ):
            return {
                k.value for k in node.value.keys
                if isinstance(k, ast.Constant)
            }
    return set()


class TestCommandMeta:

    def test_all_registered_commands_have_meta_entry(self):
        # Every command in commands.py must appear in COMMAND_META so that
        # tab-completion and help stay in sync when new commands are added.
        registered = _registered_commands()
        missing = registered - set(COMMAND_META.keys())
        assert missing == set(), f"Commands missing from COMMAND_META: {missing}"

    def test_each_entry_is_two_string_tuple(self):
        for cmd, value in COMMAND_META.items():
            assert isinstance(value, tuple) and len(value) == 2, \
                f"COMMAND_META['{cmd}'] should be a 2-tuple"
            args_hint, description = value
            assert isinstance(args_hint, str), f"args_hint for '{cmd}' must be str"
            assert isinstance(description, str) and description, \
                f"description for '{cmd}' must be a non-empty str"

    def test_no_duplicate_command_names(self):
        assert len(COMMAND_META) == len(set(COMMAND_META))


# =============================================================================
# CommandCompleter  (tab-completion logic)
# =============================================================================

class TestCommandCompleter:

    def _completions(self, text):
        """Return list of completion strings for the given input text."""
        doc = Document(text)
        return [c.text for c in CommandCompleter().get_completions(doc, None)]

    def test_empty_input_returns_all_commands(self):
        result = self._completions("")
        assert set(result) == set(COMMAND_META.keys())

    def test_prefix_filters_matching_commands(self):
        result = self._completions("ad")
        assert all(c.startswith("ad") for c in result)
        assert "add" in result
        assert "add-note" in result
        assert "add-birthday" in result

    def test_exact_prefix_returns_itself_and_longer_matches(self):
        result = self._completions("add")
        assert "add" in result
        assert "add-note" in result

    def test_unmatched_prefix_returns_empty(self):
        assert self._completions("xyz") == []

    def test_input_with_space_returns_empty(self):
        # Completer only handles the command word; stops after a space
        assert self._completions("add ") == []
        assert self._completions("add Alice") == []

    def test_matching_is_case_insensitive(self):
        lower = set(self._completions("add"))
        upper = set(self._completions("ADD"))
        assert lower == upper

    def test_completion_display_meta_contains_description(self):
        doc = Document("hello")
        completions = list(CommandCompleter().get_completions(doc, None))
        assert len(completions) == 1
        meta = str(completions[0].display_meta)
        assert "Greet" in meta


# =============================================================================
# Export: helper functions
# =============================================================================

class TestRecordToDict:

    def _full_record(self):
        r = Record("Alice")
        r.add_phone("1234567890")
        r.add_phone("0987654321")
        r.add_email("alice@example.com")
        r.add_birthday("15.06.1990")
        r.add_address("Kyiv, Main St 1")
        r.add_note("Buy milk", 1)
        r.notes[0].add_tag("personal")
        r.add_note("Work task", 2)
        return r

    def test_name_exported(self):
        assert _record_to_dict(Record("Alice"))["name"] == "Alice"

    def test_phones_exported_as_list(self):
        r = Record("Alice")
        r.add_phone("1234567890")
        r.add_phone("0987654321")
        d = _record_to_dict(r)
        assert d["phones"] == ["1234567890", "0987654321"]

    def test_email_exported(self):
        r = Record("Alice")
        r.add_email("alice@example.com")
        assert _record_to_dict(r)["email"] == "alice@example.com"

    def test_email_empty_when_not_set(self):
        assert _record_to_dict(Record("Alice"))["email"] == ""

    def test_birthday_exported_as_string(self):
        r = Record("Alice")
        r.add_birthday("15.06.1990")
        assert _record_to_dict(r)["birthday"] == "15.06.1990"

    def test_birthday_empty_when_not_set(self):
        assert _record_to_dict(Record("Alice"))["birthday"] == ""

    def test_address_exported(self):
        r = Record("Alice")
        r.add_address("Kyiv, Main St 1")
        assert _record_to_dict(r)["address"] == "Kyiv, Main St 1"

    def test_notes_exported_with_id_text_tags(self):
        r = Record("Alice")
        r.add_note("Buy milk", 7)
        r.notes[0].add_tag("personal")
        notes = _record_to_dict(r)["notes"]
        assert len(notes) == 1
        assert notes[0] == {"id": 7, "text": "Buy milk", "tags": ["personal"]}

    def test_notes_empty_list_when_none(self):
        assert _record_to_dict(Record("Alice"))["notes"] == []

    def test_full_record_all_fields_present(self):
        d = _record_to_dict(self._full_record())
        assert d["name"] == "Alice"
        assert len(d["phones"]) == 2
        assert d["email"] == "alice@example.com"
        assert d["birthday"] == "15.06.1990"
        assert d["address"] == "Kyiv, Main St 1"
        assert len(d["notes"]) == 2


class TestResolvePath:

    def test_relative_name_gets_extension_added(self, tmp_path):
        import handlers.export_handlers as eh
        original = eh.EXPORT_DIR
        eh.EXPORT_DIR = str(tmp_path)
        try:
            result = _resolve_path("myfile", "json")
            assert result.endswith(".json")
        finally:
            eh.EXPORT_DIR = original

    def test_name_with_correct_extension_unchanged(self, tmp_path):
        import handlers.export_handlers as eh
        original = eh.EXPORT_DIR
        eh.EXPORT_DIR = str(tmp_path)
        try:
            result = _resolve_path("myfile.json", "json")
            assert result.endswith("myfile.json")
        finally:
            eh.EXPORT_DIR = original

    def test_absolute_path_returned_as_is(self, tmp_path):
        abs_path = str(tmp_path / "out.json")
        result = _resolve_path(abs_path, "json")
        assert result == abs_path

    def test_path_with_separator_returned_as_is(self, tmp_path):
        path_with_sep = str(tmp_path / "sub" / "out")
        result = _resolve_path(path_with_sep, "csv")
        assert path_with_sep + ".csv" == result or result.startswith(str(tmp_path))


# =============================================================================
# Export: JSON output
# =============================================================================

class TestExportJson:

    def _book(self):
        book = AddressBook()
        r = Record("Alice")
        r.add_phone("1234567890")
        r.add_email("alice@example.com")
        r.add_birthday("15.06.1990")
        r.add_note("Task one", 1)
        r.notes[0].add_tag("work")
        book.add_record(r)
        bob = Record("Bob")
        bob.add_phone("0987654321")
        book.add_record(bob)
        return book

    def test_creates_valid_json_file(self, tmp_path):
        path = str(tmp_path / "out.json")
        _export_json(self._book(), path)
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, list)

    def test_all_contacts_exported(self, tmp_path):
        path = str(tmp_path / "out.json")
        _export_json(self._book(), path)
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        names = [r["name"] for r in data]
        assert "Alice" in names and "Bob" in names

    def test_phones_serialized_as_list(self, tmp_path):
        path = str(tmp_path / "out.json")
        _export_json(self._book(), path)
        alice = next(r for r in json.loads(Path(path).read_text()) if r["name"] == "Alice")
        assert alice["phones"] == ["1234567890"]

    def test_notes_with_tags_serialized(self, tmp_path):
        path = str(tmp_path / "out.json")
        _export_json(self._book(), path)
        alice = next(r for r in json.loads(Path(path).read_text()) if r["name"] == "Alice")
        assert alice["notes"][0]["text"] == "Task one"
        assert alice["notes"][0]["tags"] == ["work"]

    def test_optional_fields_empty_string_when_not_set(self, tmp_path):
        path = str(tmp_path / "out.json")
        _export_json(self._book(), path)
        bob = next(r for r in json.loads(Path(path).read_text()) if r["name"] == "Bob")
        assert bob["email"] == ""
        assert bob["birthday"] == ""

    def test_file_is_utf8_encoded(self, tmp_path):
        book = AddressBook()
        r = Record("Олексій")
        r.add_phone("1234567890")
        book.add_record(r)
        path = str(tmp_path / "out.json")
        _export_json(book, path)
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        assert data[0]["name"] == "Олексій"


# =============================================================================
# Export: CSV output
# =============================================================================

class TestExportCsv:

    def _book_with_notes(self):
        book = AddressBook()
        r = Record("Alice")
        r.add_phone("1234567890")
        r.add_phone("0987654321")
        r.add_email("alice@example.com")
        r.add_note("Task one", 1)
        r.notes[0].add_tag("work")
        r.notes[0].add_tag("urgent")
        r.add_note("Task two", 2)
        book.add_record(r)
        bob = Record("Bob")
        bob.add_phone("1111111111")
        book.add_record(bob)
        return book

    def _read_csv(self, path):
        with open(path, encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))

    def test_creates_csv_with_correct_header(self, tmp_path):
        path = str(tmp_path / "out.csv")
        _export_csv(_make_book(("Alice", "1234567890")), path)
        with open(path, encoding="utf-8", newline="") as f:
            header = next(csv.reader(f))
        expected = ["name", "phones", "email", "birthday", "address",
                    "note_id", "note_text", "note_tags"]
        assert header == expected

    def test_contact_without_notes_writes_one_row(self, tmp_path):
        path = str(tmp_path / "out.csv")
        _export_csv(_make_book(("Bob", "1111111111")), path)
        rows = self._read_csv(path)
        assert len(rows) == 1
        assert rows[0]["name"] == "Bob"
        assert rows[0]["note_text"] == ""

    def test_contact_with_two_notes_writes_two_rows(self, tmp_path):
        path = str(tmp_path / "out.csv")
        _export_csv(self._book_with_notes(), path)
        rows = [r for r in self._read_csv(path) if r["name"] == "Alice"]
        assert len(rows) == 2

    def test_multiple_phones_joined_with_semicolon(self, tmp_path):
        path = str(tmp_path / "out.csv")
        _export_csv(self._book_with_notes(), path)
        alice_row = next(r for r in self._read_csv(path) if r["name"] == "Alice")
        assert "1234567890" in alice_row["phones"]
        assert "0987654321" in alice_row["phones"]

    def test_note_tags_joined_with_semicolon(self, tmp_path):
        path = str(tmp_path / "out.csv")
        _export_csv(self._book_with_notes(), path)
        tagged = next(r for r in self._read_csv(path)
                      if r["name"] == "Alice" and r["note_text"] == "Task one")
        assert "work" in tagged["note_tags"]
        assert "urgent" in tagged["note_tags"]

    def test_note_without_tags_has_empty_tags_field(self, tmp_path):
        path = str(tmp_path / "out.csv")
        _export_csv(self._book_with_notes(), path)
        untagged = next(r for r in self._read_csv(path)
                        if r["name"] == "Alice" and r["note_text"] == "Task two")
        assert untagged["note_tags"] == ""


# =============================================================================
# Export: export-book command handler
# =============================================================================

class TestExportBookCommand:

    def test_empty_book_returns_message(self):
        result = export_book(["json"], AddressBook())
        assert "empty" in result.lower()

    def test_missing_format_returns_error(self):
        book = _make_book(("Alice", "1234567890"))
        result = export_book([], book)
        assert "Error" in result

    def test_invalid_format_returns_error(self):
        book = _make_book(("Alice", "1234567890"))
        result = export_book(["xml"], book)
        assert "Error" in result

    def test_export_json_to_custom_path(self, tmp_path):
        book = _make_book(("Alice", "1234567890"))
        path = str(tmp_path / "contacts.json")
        result = export_book(["json", path], book)
        assert Path(path).exists()
        assert "Alice" in result or "contacts" in result
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        assert any(r["name"] == "Alice" for r in data)

    def test_export_csv_to_custom_path(self, tmp_path):
        book = _make_book(("Alice", "1234567890"))
        path = str(tmp_path / "contacts.csv")
        result = export_book(["csv", path], book)
        assert Path(path).exists()
        rows = list(csv.DictReader(open(path, encoding="utf-8")))
        assert rows[0]["name"] == "Alice"

    def test_success_message_includes_contact_count(self, tmp_path):
        book = _make_book(("Alice", "1234567890"), ("Bob", "0987654321"))
        path = str(tmp_path / "out.json")
        result = export_book(["json", path], book)
        assert "2" in result

    def test_custom_path_without_extension_gets_extension_added(self, tmp_path):
        book = _make_book(("Alice", "1234567890"))
        path_no_ext = str(tmp_path / "myexport")
        export_book(["json", path_no_ext], book)
        assert Path(path_no_ext + ".json").exists()

    def test_export_json_produces_valid_structure(self, tmp_path):
        book = _make_book(("Alice", "1234567890"))
        path = str(tmp_path / "out.json")
        export_book(["json", path], book)
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        assert isinstance(data, list)
        assert set(data[0].keys()) >= {"name", "phones", "email", "birthday", "address", "notes"}
