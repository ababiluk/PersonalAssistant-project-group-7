"""
End-to-end happy-path scenario.

Simulates a complete user session against the real handlers:
empty book → add contacts with all fields → exercise every command group →
save and reload. State is asserted at every step, so a failure pinpoints
exactly where the lifecycle breaks.
"""
from datetime import date, timedelta
from unittest.mock import patch

from rich.table import Table

from models.address_book import AddressBook
from models.record import Record
from handlers.contact_handlers import add_contact, delete_contact, find_contact
from handlers.phone_handlers import change_contact, add_phone, remove_phone
from handlers.email_handlers import add_email
from handlers.birthday_handlers import add_birthday
from handlers.display import display_all, display_birthdays, display_phone, display_birthday
from handlers.note_handlers import (
    add_note, edit_note, delete_note, show_notes, show_all_notes,
    all_with_notes, find_notes, add_tag, find_by_tag, sort_by_tags,
)
from handlers.utils import save_data, load_data


class TestHappyPath:
    """One linear scenario covering the full lifecycle in a single test."""

    def test_full_session(self, tmp_path):

        # ------------------------------------------------------------------
        # 1. App starts: empty address book
        # ------------------------------------------------------------------
        book = AddressBook()
        assert len(book.data) == 0

        # ------------------------------------------------------------------
        # 2. Add Alice (email + birthday) and Bob (phone only) interactively.
        #    Prompts: name, phone, email, birthday, "add address?" (n), note
        # ------------------------------------------------------------------
        with patch("builtins.input", side_effect=[
            "Alice", "1234567890", "alice@example.com", "15.06.1990", "n", ""
        ]):
            assert "Error" not in add_contact([], book)
        assert book.find("Alice") is not None

        with patch("builtins.input", side_effect=["Bob", "0987654321", "", "", "n", ""]):
            assert "Error" not in add_contact([], book)
        assert book.find("Bob") is not None
        assert len(book.data) == 2

        # ------------------------------------------------------------------
        # 3. Alice's optional fields persisted immediately
        # ------------------------------------------------------------------
        alice = book.find("Alice")
        assert alice.find_email("alice@example.com") is not None
        assert str(alice.birthday) == "15.06.1990"
        assert alice.find_phone("1234567890") is not None

        # ------------------------------------------------------------------
        # 4. edit-phone: replace Alice's only phone (interactive new number)
        # ------------------------------------------------------------------
        with patch("builtins.input", side_effect=["1111111111"]):
            assert "Error" not in change_contact(["Alice"], book)
        assert alice.find_phone("1111111111") is not None
        assert alice.find_phone("1234567890") is None

        # ------------------------------------------------------------------
        # 5. add-phone then delete-phone (inline)
        # ------------------------------------------------------------------
        add_phone(["Alice", "2222222222"], book)
        assert alice.find_phone("2222222222") is not None
        remove_phone(["Alice", "2222222222"], book)
        assert alice.find_phone("2222222222") is None

        # ------------------------------------------------------------------
        # 6. add-birthday and add-email to Bob (inline)
        # ------------------------------------------------------------------
        add_birthday(["Bob", "20.03.1985"], book)
        assert str(book.find("Bob").birthday) == "20.03.1985"
        add_email(["Bob", "bob@example.com"], book)
        assert book.find("Bob").find_email("bob@example.com") is not None

        # ------------------------------------------------------------------
        # 7. show-birthday / phone display tables (values verified in steps 3 & 6)
        # ------------------------------------------------------------------
        assert isinstance(display_birthday(["Alice"], book), Table)
        assert isinstance(display_birthday(["Bob"], book), Table)
        assert isinstance(display_phone(["Alice"], book), Table)

        # ------------------------------------------------------------------
        # 8. find-contact — partial name (case-insensitive) and by phone
        # ------------------------------------------------------------------
        assert isinstance(find_contact(["alice"], book), Table)
        assert isinstance(find_contact(["1111"], book), Table)
        assert "No contacts found" in find_contact(["zzz"], book)

        # ------------------------------------------------------------------
        # 9. add-note to both contacts (IDs globally unique)
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
        # 10. add-tag to Alice's first note and Bob's note (by note id)
        # ------------------------------------------------------------------
        with patch("builtins.input", side_effect=["work"]):
            assert "work" in add_tag([str(alice_note_1_id)], book)
        assert "work" in alice.notes[0].tags

        with patch("builtins.input", side_effect=["personal"]):
            add_tag([str(bob_note_id)], book)
        assert "personal" in book.find("Bob").notes[0].tags

        # ------------------------------------------------------------------
        # 11. find-notes (text + exact-tag search)
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
        # 13. Aggregate views
        # ------------------------------------------------------------------
        assert isinstance(display_all([], book), Table)
        assert isinstance(show_notes(["Alice"], book), Table)
        assert isinstance(show_all_notes([], book), Table)
        assert isinstance(all_with_notes([], book), Table)

        # ------------------------------------------------------------------
        # 14. upcoming-birthdays (must not crash regardless of today's date)
        # ------------------------------------------------------------------
        display_birthdays([], book)           # default 7-day window
        display_birthdays(["365"], book)      # one-year window

        imminent = AddressBook()
        r = Record("Soon")
        r.add_phone("5555555555")
        # Past-year birthday with tomorrow's month/day — Birthday() rejects future
        # dates, but get_upcoming_birthdays compares only month/day.
        tomorrow = date.today() + timedelta(days=1)
        r.add_birthday(date(2000, tomorrow.month, tomorrow.day).strftime("%d.%m.%Y"))
        imminent.add_record(r)
        assert isinstance(display_birthdays([], imminent), Table)

        # ------------------------------------------------------------------
        # 15. edit-note: update Alice's first note — tags must survive
        # ------------------------------------------------------------------
        with patch("builtins.input", side_effect=["Meeting moved to Friday"]):
            assert "updated" in edit_note([str(alice_note_1_id)], book)
        assert alice.notes[0].value == "Meeting moved to Friday"
        assert "work" in alice.notes[0].tags, "edit-note must preserve tags"

        # ------------------------------------------------------------------
        # 16. delete-note: remove Alice's second note (by id)
        # ------------------------------------------------------------------
        assert "deleted" in delete_note([str(alice_note_2_id)], book)
        assert len(alice.notes) == 1
        assert alice.notes[0].id == alice_note_1_id

        # ------------------------------------------------------------------
        # 17. delete-contact: remove Bob entirely
        # ------------------------------------------------------------------
        assert "deleted" in delete_contact(["Bob"], book)
        assert book.find("Bob") is None
        assert len(book.data) == 1

        # ------------------------------------------------------------------
        # 18. Persist and reload — full state must survive a round-trip
        # ------------------------------------------------------------------
        save_path = str(tmp_path / "addressbook.pkl")
        save_data(book, save_path)

        reloaded_alice = load_data(save_path).find("Alice")
        assert reloaded_alice is not None
        assert reloaded_alice.find_phone("1111111111") is not None
        assert reloaded_alice.find_email("alice@example.com") is not None
        assert str(reloaded_alice.birthday) == "15.06.1990"
        assert len(reloaded_alice.notes) == 1
        assert reloaded_alice.notes[0].value == "Meeting moved to Friday"
        assert reloaded_alice.notes[0].tags == ["work"]
        assert load_data(save_path).find("Bob") is None
