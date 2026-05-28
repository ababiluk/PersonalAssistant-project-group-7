"""
End-to-end happy-path scenario.
Simulates a complete user session: empty book → add contacts with all fields
→ use every command → save and reload. Each step asserts state before moving on.
"""
import pytest
from datetime import date, timedelta
from unittest.mock import patch
from rich.table import Table

from models.address_book import AddressBook
from models.record import Record
from handlers.contact_handlers import (
    add_contact, change_contact, delete_contact,
    remove_phone, add_email, find_contact,
)
from handlers.birthday_handlers import add_birthday, show_birthday
from handlers.display import display_all, display_birthdays, display_phone, display_birthday
from handlers.note_handlers import (
    add_note, edit_note, delete_note,
    show_notes, show_all_notes, all_with_notes,
    find_notes, add_tag, find_by_tag, sort_by_tags,
)
from handlers.utils import save_data, load_data


class TestHappyPath:
    """
    One linear scenario covering the full lifecycle.
    The entire session is a single test so intermediate state is verified
    at every step — a failure pinpoints exactly where the flow breaks.
    """

    def test_full_session(self, tmp_path):

        # ------------------------------------------------------------------
        # 1. App starts: empty address book
        # ------------------------------------------------------------------
        book = AddressBook()
        assert len(book.data) == 0

        # ------------------------------------------------------------------
        # 2. Add Alice (with email + birthday) and Bob (phone only)
        # ------------------------------------------------------------------
        # inputs: name → phone → email → birthday → no address
        with patch("builtins.input", side_effect=["Alice", "1234567890", "alice@example.com", "15.06.1990", "n"]):
            result = add_contact([], book)
        assert "Error" not in result
        assert book.find("Alice") is not None

        with patch("builtins.input", side_effect=["Bob", "0987654321", "", "", "n"]):
            result = add_contact([], book)
        assert "Error" not in result
        assert book.find("Bob") is not None

        assert len(book.data) == 2

        # ------------------------------------------------------------------
        # 3. Verify Alice's optional fields persisted immediately
        # ------------------------------------------------------------------
        alice = book.find("Alice")
        assert str(alice.email) == "alice@example.com"
        assert str(alice.birthday) == "15.06.1990"
        assert alice.find_phone("1234567890") is not None

        # ------------------------------------------------------------------
        # 4. change: replace Alice's phone number
        # ------------------------------------------------------------------
        assert change_contact(["Alice", "1234567890", "1111111111"], book) == "Contact updated."
        assert alice.find_phone("1111111111") is not None
        assert alice.find_phone("1234567890") is None

        # ------------------------------------------------------------------
        # 5. add (existing contact): attach a second phone, then remove it
        # ------------------------------------------------------------------
        with patch("builtins.input", side_effect=["Alice", "2222222222", "1", "", "", "n"]):
            add_contact([], book)
        assert alice.find_phone("2222222222") is not None

        assert remove_phone(["Alice", "2222222222"], book) == "Phone removed."
        assert alice.find_phone("2222222222") is None

        # ------------------------------------------------------------------
        # 6. add-birthday and add-email to Bob
        # ------------------------------------------------------------------
        assert add_birthday(["Bob", "20.03.1985"], book) == "Birthday added."
        assert str(book.find("Bob").birthday) == "20.03.1985"

        assert add_email(["Bob", "bob@example.com"], book) == "Email added."
        assert str(book.find("Bob").email) == "bob@example.com"

        # ------------------------------------------------------------------
        # 7. show-birthday / phone display
        # ------------------------------------------------------------------
        assert show_birthday(["Alice"], book) == "15.06.1990"
        assert show_birthday(["Bob"], book) == "20.03.1985"
        assert isinstance(display_phone(["Alice"], book), Table)
        assert isinstance(display_birthday(["Bob"], book), Table)

        # ------------------------------------------------------------------
        # 8. find — by name (partial, case-insensitive) and by phone
        # ------------------------------------------------------------------
        assert isinstance(find_contact(["alice"], book), Table)
        assert isinstance(find_contact(["1111"], book), Table)
        assert "No contacts found" in find_contact(["zzz"], book)

        # ------------------------------------------------------------------
        # 9. add-note to both contacts (IDs must be globally unique)
        # ------------------------------------------------------------------
        add_note(["Alice", "Meeting", "on", "Monday"], book)
        add_note(["Alice", "Call", "the", "dentist"], book)
        add_note(["Bob", "Buy", "groceries"], book)

        all_ids = [n.id for r in book.data.values() for n in r.notes]
        assert len(all_ids) == len(set(all_ids)), "Note IDs must be globally unique"

        alice_note_1_id = alice.notes[0].id
        alice_note_2_id = alice.notes[1].id
        bob_note_id = book.find("Bob").notes[0].id

        # ------------------------------------------------------------------
        # 10. add-tag to Alice's first note and Bob's note
        # ------------------------------------------------------------------
        with patch("builtins.input", side_effect=[str(alice_note_1_id), "work"]):
            result = add_tag(["Alice"], book)
        assert "work" in result
        assert "work" in alice.notes[0].tags

        with patch("builtins.input", side_effect=[str(bob_note_id), "personal"]):
            add_tag(["Bob"], book)
        assert "personal" in book.find("Bob").notes[0].tags

        # ------------------------------------------------------------------
        # 11. find-notes (text search and tag search)
        # ------------------------------------------------------------------
        assert isinstance(find_notes(["meeting"], book), Table)
        assert isinstance(find_notes(["work"], book), Table)      # tag exact-match
        assert "No notes found" in find_notes(["xyznotexist"], book)

        # ------------------------------------------------------------------
        # 12. find-by-tag and sort-by-tags
        # ------------------------------------------------------------------
        assert isinstance(find_by_tag(["work"], book), Table)
        assert isinstance(find_by_tag(["personal"], book), Table)
        assert "No notes found" in find_by_tag(["nonexistent"], book)
        assert isinstance(sort_by_tags([], book), Table)

        # ------------------------------------------------------------------
        # 13. Aggregate views: all / show-notes / show-all-notes / all-with-notes
        # ------------------------------------------------------------------
        assert isinstance(display_all([], book), Table)
        assert isinstance(show_notes(["Alice"], book), Table)
        assert isinstance(show_all_notes([], book), Table)
        assert isinstance(all_with_notes([], book), Table)

        # ------------------------------------------------------------------
        # 14. birthdays command (should not crash regardless of today's date)
        # ------------------------------------------------------------------
        display_birthdays([], book)           # default 7-day window
        display_birthdays(["365"], book)      # one-year window

        # Verify upcoming detection works when a birthday is imminent
        imminent_book = AddressBook()
        r = Record("Soon")
        r.add_phone("5555555555")
        r.add_birthday((date.today() + timedelta(days=1)).strftime("%d.%m.%Y"))
        imminent_book.add_record(r)
        assert isinstance(display_birthdays([], imminent_book), Table)

        # ------------------------------------------------------------------
        # 15. edit-note: update Alice's first note
        # ------------------------------------------------------------------
        with patch("builtins.input", side_effect=[str(alice_note_1_id), "Meeting moved to Friday"]):
            result = edit_note(["Alice"], book)
        assert "updated" in result
        assert alice.notes[0].value == "Meeting moved to Friday"
        # NOTE: tags are lost after edit (known bug — see test_commands.py::test_edit_note_preserves_tags)

        # ------------------------------------------------------------------
        # 16. delete-note: remove Alice's second note
        # ------------------------------------------------------------------
        with patch("builtins.input", return_value=str(alice_note_2_id)):
            result = delete_note(["Alice"], book)
        assert "deleted" in result
        assert len(alice.notes) == 1
        assert alice.notes[0].id == alice_note_1_id

        # ------------------------------------------------------------------
        # 17. delete-contact: remove Bob entirely
        # ------------------------------------------------------------------
        result = delete_contact(["Bob"], book)
        assert "deleted" in result
        assert book.find("Bob") is None
        assert len(book.data) == 1

        # ------------------------------------------------------------------
        # 18. Persist and reload — full state must survive a round-trip
        # ------------------------------------------------------------------
        save_path = str(tmp_path / "addressbook.pkl")
        save_data(book, save_path)

        reloaded = load_data(save_path)
        reloaded_alice = reloaded.find("Alice")

        assert reloaded_alice is not None
        assert reloaded_alice.find_phone("1111111111") is not None
        assert str(reloaded_alice.email) == "alice@example.com"
        assert str(reloaded_alice.birthday) == "15.06.1990"

        assert len(reloaded_alice.notes) == 1
        assert reloaded_alice.notes[0].value == "Meeting moved to Friday"
        # tags are dropped by edit_note (known bug) so we do not assert them here

        assert reloaded.find("Bob") is None
