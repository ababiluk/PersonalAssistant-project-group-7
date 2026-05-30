from .fields import Name, Phone, Birthday, Email, Address, Note


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
        self.emails = []
        self.address = None
        self.notes = []

    def add_phone(self, phone):
        self.phones.append(Phone(phone))
    
    def add_address(self, address):
        self.address = Address(address)

    def remove_phone(self, phone):
        # Raise on a missing phone so the caller gets clear feedback instead of a
        # silent no-op that looks like success.
        if not self.find_phone(phone):
            raise ValueError(f"There is no such phone to remove: {phone}")
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        phone_obj = self.find_phone(old_phone)
        if not phone_obj:
            raise ValueError(f"Phone {old_phone} not found")
        idx = self.phones.index(phone_obj)
        self.phones[idx] = Phone(new_phone)

    def find_phone(self, phone):
        return next((p for p in self.phones if p.value == phone), None)

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def remove_birthday(self):
        # A contact has at most one birthday, so removal just clears the slot.
        self.birthday = None

    def remove_address(self):
        # Address is single-valued; clearing the slot is the whole operation.
        self.address = None

    # Emails mirror phones (a contact may have several), so they share the same
    # add/find/remove/edit shape rather than a single overwritten slot.
    def add_email(self, email):
        self.emails.append(Email(email))

    def find_email(self, email):
        return next((e for e in self.emails if e.value == email), None)

    def remove_email(self, email):
        if not self.find_email(email):
            raise ValueError(f"There is no such email to remove: {email}")
        self.emails = [e for e in self.emails if e.value != email]

    def edit_email(self, old_email, new_email):
        email_obj = self.find_email(old_email)
        if not email_obj:
            raise ValueError(f"Email {old_email} not found")
        idx = self.emails.index(email_obj)
        self.emails[idx] = Email(new_email)

    def add_note(self, text, note_id):
        self.notes.append(Note(text, note_id))

    def edit_note(self, note_id, new_text):
        for i, note in enumerate(self.notes):
            if note.id == note_id:
                self.notes[i] = Note(new_text, note_id)
                return
        raise IndexError(f"Note with id {note_id} not found.")

    def delete_note(self, note_id):
        for i, note in enumerate(self.notes):
            if note.id == note_id:
                self.notes.pop(i)
                return
        raise IndexError(f"Note with id {note_id} not found.")

    def add_tag_to_note(self, note_id, tag):
        for note in self.notes:
            if note.id == note_id:
                note.add_tag(tag)
                return
        raise IndexError(f"Note with id {note_id} not found.")

    def __str__(self):
        birthday = str(self.birthday) if self.birthday else "N/A"
        email = "; ".join(e.value for e in self.emails) if self.emails else "N/A"
        address = str(self.address) if self.address else "N/A"

        phones = "; ".join(p.value for p in self.phones) if self.phones else "No phones"
        return f"Contact name: {self.name.value}, phones: {phones}, birthday: {birthday}, email: {email}, Address: {address}"