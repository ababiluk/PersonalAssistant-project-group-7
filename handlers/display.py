from rich.table import Table
from decorators import input_error
from models import AddressBook
from rich.console import Console


console = Console()

def _print(result):
    if isinstance(result, str) and result.startswith("Error"):
        console.print(f"[bold red]{result}[/bold red]")
    else:
        console.print(result)

@input_error
def display_all(args, book: AddressBook):  # show all contacts as table
    if not book.data:
        return "No contacts saved."

    table = Table(title="Address Book", header_style="bold cyan")
    table.add_column("Name", style="green")
    table.add_column("Phones")
    table.add_column("Birthday")
    table.add_column("Email")
    table.add_column("Address")

    for record in book.data.values():
        phones = "; ".join(p.value for p in record.phones) or "—"
        birthday = str(record.birthday) if record.birthday else "—"
        email = str(record.email) if record.email else "—"
        address = str(record.address) if record.address else "—"
        table.add_row(record.name.value, phones, birthday, email, address)

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
def display_birthdays(args, book: AddressBook):  # show upcoming birthdays as table
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No birthdays in the next 7 days."

    table = Table(title="Upcoming Birthdays", header_style="bold cyan")
    table.add_column("Name", style="green")
    table.add_column("Congratulation Date")

    for entry in upcoming:
        table.add_row(entry["name"], entry["congratulation_date"])

    return table

def show_help(args, book):
    table = Table(title="Available commands", show_header=True, header_style="bold cyan")
    table.add_column("Command", style="green")
    table.add_column("Description")

    table.add_row("hello", "Greet the bot")
    table.add_row("add [name] [phone]", "Add or update a contact")
    table.add_row("change [name] [old] [new]", "Change phone number")
    table.add_row("phone [name]", "Show phone number(s)")
    table.add_row("all", "Show all contacts")
    table.add_row("delete [name]", "Delete a contact")
    table.add_row("remove-phone [name] [phone]", "Remove a specific phone")
    table.add_row("add-birthday [name] [DD.MM.YYYY]", "Add birthday")
    table.add_row("show-birthday [name]", "Show birthday")
    table.add_row("birthdays", "Upcoming birthdays (next 7 days)")
    table.add_row("help", "Show this message")
    table.add_row("close / exit", "Quit the bot")

    return table