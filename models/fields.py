import re
from datetime import datetime


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        cleaned_value = re.sub(r"\D", "", value)
        if len(cleaned_value) != 10:
            raise ValueError(f"Phone number must contain exactly 10 digits: {cleaned_value}")
        super().__init__(cleaned_value)
    
    def __str__(self):
        v=self.value
        return f"+38({v[:3]}){v[3:6]}-{v[6:8]}-{v[8:]}"


class Birthday(Field):
    def __init__(self, value):
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
        
class Address(Field):
    pass

class Note(Field):
    def __init__(self, value, note_id):
        if not value.strip():
            raise ValueError("Note cannot be empty.")
        super().__init__(value.strip())
        self.id = note_id
