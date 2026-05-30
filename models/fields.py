import re
from datetime import datetime


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


# No format rules enforced here by design: name checks currently live in the
# input layer (shared._validate_name), not the model. See ТЗ validation gap.
class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        # Store digits only (strip any formatting) so the same number always
        # compares equal regardless of how the user typed it.
        cleaned_value = re.sub(r"\D", "", value)
        if len(cleaned_value) != 10:
            raise ValueError(f"Phone number must contain exactly 10 digits: {cleaned_value}")
        super().__init__(cleaned_value)

    def __str__(self):
        # Render the bare digits as a Ukrainian-formatted number for display only.
        v=self.value
        return f"+38({v[:3]}){v[3:6]}-{v[6:8]}-{v[8:]}"


class Birthday(Field):
    def __init__(self, value):
        # Keep a real date object (not the string) so AddressBook can do date
        # arithmetic for upcoming-birthday calculations.
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")


class Email(Field):
    def __init__(self, value):
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(pattern, value):
            raise ValueError("Invalid email format. Example: user@example.com")
        super().__init__(value)
        

# Free-form text: no format rules (no address validation yet — ТЗ validation gap).
class Address(Field):
    pass


class Note(Field):
    def __init__(self, value, note_id):
        # Reject empty/whitespace notes so the list never holds blank entries.
        if not value.strip():
            raise ValueError("Note cannot be empty.")
        super().__init__(value.strip())
        self.id = note_id
        self.tags = []

    def edit_text(self, new_text):
        # Edit text in place (instead of rebuilding the Note) so the note keeps
        # its id and tags; reuse the same non-empty rule as creation.
        if not new_text.strip():
            raise ValueError("Note cannot be empty.")
        self.value = new_text.strip()

    def add_tag(self, tag):
        # Skip duplicates so the same tag can't pile up on one note.
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag):
        # Raise on a missing tag so the caller reports it instead of silently
        # doing nothing.
        if tag not in self.tags:
            raise ValueError(f"Note #{self.id} has no tag '{tag}'.")
        self.tags.remove(tag)

    def set_tags(self, tags):
        # Replace the whole tag list at once (used by edit-tag). De-duplicate and
        # drop blanks while preserving the given order.
        cleaned = []
        for tag in tags:
            tag = tag.strip()
            if tag and tag not in cleaned:
                cleaned.append(tag)
        self.tags = cleaned