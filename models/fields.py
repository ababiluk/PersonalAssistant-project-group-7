import re
from datetime import datetime


# Base class for all contact fields
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


# Stores contact name
class Name(Field):
    pass


# Stores and validates phone numbers
class Phone(Field):
    def __init__(self, value):
        cleaned_value = re.sub(r"\D", "", value)
        if len(cleaned_value) != 10:
            raise ValueError(
                f"Phone number must contain exactly 10 digits: {cleaned_value}"
            )
        super().__init__(cleaned_value)

    def __str__(self):
        v = self.value
        return f"+38({v[:3]}){v[3:6]}-{v[6:8]}-{v[8:]}"


# Stores and validates birthday dates
class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")


# Stores and validates email addresses
class Email(Field):
    def __init__(self, value):
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(pattern, value):
            raise ValueError("Invalid email format. Example: user@example.com")
        super().__init__(value)


# Stores contact address
class Address(Field):
    pass


# Stores notes and associated tags
class Note(Field):
    def __init__(self, value, note_id):
        if not value.strip():
            raise ValueError("Note cannot be empty.")
        super().__init__(value.strip())
        self.id = note_id
        self.tags = [] # initialize tags list for the note

    
    def add_tag(self, tag):
        if tag not in self.tags:
            self.tags.append(tag) # prevent duplicate tags
