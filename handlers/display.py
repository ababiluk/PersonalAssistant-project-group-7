import random

from rich.table import Table
from decorators import input_error
from models import AddressBook
from rich.console import Console
from handlers.command_meta import COMMAND_META

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
        phones = "; ".join(str(p) for p in record.phones) or "—"
        birthday = str(record.birthday) if record.birthday else "—"
        email = str(record.email) if record.email else "—"
        address = str(record.address) if record.address else "—"
        table.add_row(record.name.value, phones, birthday, email, address)

    return table


@input_error
def display_phone(args, book: AddressBook):  # show contact phones as table
    name = " ".join(args)
    record = book.find(name)
    if not record:
        raise KeyError(name)

    table = Table(title=f"Phones: {name}", header_style="bold cyan")
    table.add_column("Name", style="green")
    table.add_column("Phones")

    phones = "; ".join(str(p) for p in record.phones) or "—"
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
    days = int(args[0]) if args else 7
    upcoming = book.get_upcoming_birthdays(days=days)
    if not upcoming:
        return f"No birthdays in the next {days} days."

    table = Table(
        title=f"Upcoming Birthdays (next {days} days)", header_style="bold cyan"
    )
    table.add_column("Name", style="green")
    table.add_column("Congratulation Date")

    for entry in upcoming:
        table.add_row(entry["name"], entry["congratulation_date"])

    return table


_GREETINGS = [
    "Hi! How can I help you?",
    "Hello! What can I do for you?",
    "Hey there! What do you need?",
    "Greetings! How may I assist you?",
    "Hi! Ready to help. What's up?",
]

_REPEAT_GREETINGS = [
    "We already said hello, but hi again!",
    "Again? Well, hello once more!",
    "You greeted me already, but I don't mind — hello!",
    "Second hello? Why not — hi!",
]

_hello_count = 0


def hello_message(_args, _book):  # greeting message from the bot
    global _hello_count
    _hello_count += 1
    if _hello_count > 1:
        return random.choice(_REPEAT_GREETINGS)
    return random.choice(_GREETINGS)


def show_help(_args, _book):
    table = Table(
        title="Available commands", show_header=True, header_style="bold cyan"
    )
    table.add_column("Command", style="green")
    table.add_column("Description")

    for cmd, (args, desc) in COMMAND_META.items():
        if cmd == "exit":
            continue
        if cmd == "close":
            table.add_row("close / exit", desc)
            continue
        args_escaped = args.replace("[", "\\[")
        table.add_row(f"{cmd} {args_escaped}".strip(), desc)

    return table
