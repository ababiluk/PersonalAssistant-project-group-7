from .fields import Name, Phone, Birthday, Email, Address, Note


# Store contact information and related data
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
        self.email = None
        self.address = None
        self.notes = []

    # Add a new phone number to the contact
    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    # Add address information
    def add_address(self, address):
        self.address = Address(address)

    # Remove a phone number from the contact
    def remove_phone(self, phone):
        if not self.find_phone(phone):  # check phone exists first
            raise ValueError(f"There is no such phone to remove: {phone}")
        self.phones = [
            p for p in self.phones if p.value != phone
        ]  # remove if phone exists

    # Replace an existing phone number
    def edit_phone(self, old_phone, new_phone):
        phone_obj = self.find_phone(old_phone)
        if not phone_obj:
            raise ValueError(f"Phone {old_phone} not found")
        idx = self.phones.index(phone_obj)
        self.phones[idx] = Phone(new_phone)

    # Find a phone object by number
    def find_phone(self, phone):
        return next((p for p in self.phones if p.value == phone), None)

    # Add birthday information
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    # Add email information
    def add_email(self, email):
        self.email = Email(email)

    # Create and attach a new note
    def add_note(self, text, note_id):
        self.notes.append(Note(text, note_id))

    # Update note text by note ID
    def edit_note(self, note_id, new_text):
        for i, note in enumerate(self.notes):
            if note.id == note_id:
                self.notes[i] = Note(new_text, note_id)
                return
        raise IndexError(f"Note with id {note_id} not found.")

    # Delete a note by note ID
    def delete_note(self, note_id):
        for i, note in enumerate(self.notes):
            if note.id == note_id:
                self.notes.pop(i)
                return
        raise IndexError(f"Note with id {note_id} not found.")

    # Add a tag to a specific note
    def add_tag_to_note(self, note_id, tag):
        for note in self.notes:  # find note by ID and add tag
            if note.id == note_id:
                note.add_tag(tag)
                return
        raise IndexError(f"Note with id {note_id} not found.")

    def __str__(self):
        birthday = str(self.birthday) if self.birthday else "N/A"
        email = str(self.email) if self.email else "N/A"
        address = str(self.address) if self.address else "N/A"

        phones = "; ".join(p.value for p in self.phones) if self.phones else "No phones"
        return f"Contact name: {self.name.value}, phones: {phones}, birthday: {birthday}, email: {email}, Address: {address}"
