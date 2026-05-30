from decorators import input_error
from models import AddressBook

# Add birthday to an existing contact
@input_error
def add_birthday(args, book: AddressBook):
    bday = args[-1]
    name = " ".join(args[:-1])
    record = book.find(name)
    if not record:
        raise KeyError(name)
    record.add_birthday(bday)
    return "Birthday added."

# Show birthday for a specific contact
@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if not record:
        raise KeyError(name)
    if not record.birthday:
        return f"{name} has no birthday set."
    return str(record.birthday)

# Show birthdays occurring within the next 7 days
@input_error
def birthdays(book: AddressBook):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No birthdays in the next 7 days."
    return "\n".join(f"{e['name']}: {e['congratulation_date']}" for e in upcoming)

# Edit birthday for an existing contact
@input_error
def edit_birthday(args, book: AddressBook):
    bday = args[-1]
    name = " ".join(args[:-1])

    record = book.find(name)

    if not record:
        raise KeyError(name)

    record.edit_birthday(bday)
    return "Birthday updated."

# Delete birthday from a contact
@input_error
def delete_birthday(args, book: AddressBook):
    name = " ".join(args)

    record = book.find(name)

    if not record:
        raise KeyError(name)

    if not record.birthday:
        return f"{name} has no birthday to delete."

    record.delete_birthday()
    return "Birthday deleted."