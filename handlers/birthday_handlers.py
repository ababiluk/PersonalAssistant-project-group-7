from decorators import input_error
from models import AddressBook


@input_error
def add_birthday(args, book: AddressBook):
    name, bday = args
    record = book.find(name)
    if not record:
        raise KeyError(name)
    record.add_birthday(bday)
    return "Birthday added."


@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if not record:
        raise KeyError(name)
    if not record.birthday:
        return f"{name} has no birthday set."
    return str(record.birthday)


@input_error
def birthdays(book: AddressBook):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No birthdays in the next 7 days."
    return "\n".join(f"{e['name']}: {e['congratulation_date']}" for e in upcoming)
