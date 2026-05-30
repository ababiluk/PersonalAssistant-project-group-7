from decorators import input_error
from models import AddressBook, Birthday
from handlers.shared import _require_record, _split_name_and_value


def _prompt_birthday():
    while True:
        value = input("Enter birthday (DD.MM.YYYY): ").strip()
        try:
            Birthday(value)
            return value
        except ValueError as e:
            print(f"Error: {e}")


@input_error
def add_birthday(args, book: AddressBook):
    # Date may be inline or prompted; refuses to clobber an existing birthday so
    # the user goes through edit-birthday instead.
    if not args:
        return "Error: Usage: add-birthday [name] [optional DD.MM.YYYY]"
    name_parts, bday = _split_name_and_value(args)
    name = " ".join(name_parts)
    record = _require_record(book, name)
    if record.birthday:
        return f"Error: '{name}' already has a birthday. Use edit-birthday."
    if bday is None:
        bday = _prompt_birthday()
    record.add_birthday(bday)
    return f"Birthday {bday} added to '{name}'."


@input_error
def edit_birthday(args, book: AddressBook):
    # Single-valued, so editing is just a validated overwrite of the existing one.
    if not args:
        return "Error: Usage: edit-birthday [name] [optional DD.MM.YYYY]"
    name_parts, bday = _split_name_and_value(args)
    name = " ".join(name_parts)
    record = _require_record(book, name)
    if not record.birthday:
        return f"Error: '{name}' has no birthday. Use add-birthday."
    if bday is None:
        bday = _prompt_birthday()
    record.add_birthday(bday)
    return f"Birthday updated to {bday} for '{name}'."


@input_error
def delete_birthday(args, book: AddressBook):
    if not args:
        return "Error: Usage: delete-birthday [name]"
    name = " ".join(args)
    record = _require_record(book, name)
    if not record.birthday:
        return f"Error: '{name}' has no birthday."
    record.remove_birthday()
    return f"Birthday removed from '{name}'."


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
