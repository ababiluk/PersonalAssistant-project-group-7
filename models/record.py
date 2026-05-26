from .fields import Name, Phone, Birthday, Email


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
        self.email = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        if not self.find_phone(phone):  # check phone exists first
            raise ValueError(f"There is no such phone to remove: {phone}")
        self.phones = [p for p in self.phones if p.value != phone]  # remove if phone exists

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

    def add_email(self, email):
        self.email = Email(email)  # Функція для додавання пошти

    def __str__(self):
        birthday = str(self.birthday) if self.birthday else "N/A"
        email = str(self.email) if self.email else "N/A"
        phones = "; ".join(p.value for p in self.phones)
        return f"Contact name: {self.name.value}, phones: {phones}, email: {email}, birthday: {birthday}"