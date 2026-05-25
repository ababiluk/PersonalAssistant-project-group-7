from rich.table import Table

from decorators import input_error
from models import AddressBook


@input_error
def display_all(book: AddressBook):  # show all contacts as table
    if not book.data:
        return "No contacts saved."

    table = Table(title="Address Book", header_style="bold cyan")
    table.add_column("Name", style="green")
    table.add_column("Phones")
    table.add_column("Birthday")

    for record in book.data.values():
        phones = "; ".join(p.value for p in record.phones) or "—"
        birthday = str(record.birthday) if record.birthday else "—"
        table.add_row(record.name.value, phones, birthday)

    return table


@input_error
def display_phone(args, book: AddressBook):  # show contact phones as table
    name = args[0]
    record = book.find(name)
    if not record:
        raise KeyError(name)

    table = Table(title=f"Phones: {name}", header_style="bold cyan")
    table.add_column("Name", style="green")
    table.add_column("Phones")

    phones = "; ".join(p.value for p in record.phones) or "—"
    table.add_row(name, phones)

    return table


@input_error
def display_birthday(args, book: AddressBook):  # show contact birthday as table
    name = args[0]
    record = book.find(name)
    if not record:
        raise KeyError(name)

    table = Table(title=f"Birthday: {name}", header_style="bold cyan")
    table.add_column("Name", style="green")
    table.add_column("Birthday")

    birthday = str(record.birthday) if record.birthday else "—"
    table.add_row(name, birthday)

    return table


@input_error
def display_birthdays(book: AddressBook):  # show upcoming birthdays as table
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No birthdays in the next 7 days."

    table = Table(title="Upcoming Birthdays", header_style="bold cyan")
    table.add_column("Name", style="green")
    table.add_column("Congratulation Date")

    for entry in upcoming:
        table.add_row(entry["name"], entry["congratulation_date"])

    return table
