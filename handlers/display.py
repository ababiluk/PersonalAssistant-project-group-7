import random

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
    table.add_column("Email")
    table.add_column("Birthday")

    for record in book.data.values():
        phones = "; ".join(p.value for p in record.phones) or "—"
        email = str(record.email) if record.email else "—"
        birthday = str(record.birthday) if record.birthday else "—"
        table.add_row(record.name.value, phones, email, birthday)

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
    days = int(args[0]) if args else 7
    upcoming = book.get_upcoming_birthdays(days=days)
    if not upcoming:
        return f"No birthdays in the next {days} days."

    table = Table(title=f"Upcoming Birthdays (next {days} days)", header_style="bold cyan")
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
    table = Table(title="Available commands", show_header=True, header_style="bold cyan")
    table.add_column("Command", style="green")
    table.add_column("Description")

    table.add_row("hello", "Greet the bot")
    table.add_row("add \\[name] \\[phone]", "Add or update a contact")
    table.add_row("change \\[name] \\[old] \\[new]", "Change phone number")
    table.add_row("phone \\[name]", "Show phone number(s)")
    table.add_row("all", "Show all contacts")
    table.add_row("delete-contact \\[name]", "Delete a contact")
    table.add_row("delete-phone \\[name] \\[phone]", "Remove a specific phone")
    table.add_row("add-email \\[name] \\[email]", "Add email to a contact")
    table.add_row("add-birthday \\[name] \\[DD.MM.YYYY]", "Add birthday")
    table.add_row("show-birthday \\[name]", "Show birthday")
    table.add_row("birthdays \\[days]", "Upcoming birthdays (default: 7 days)")
    table.add_row("find \\[query]", "Search contacts by name or phone")
    table.add_row("add-note \\[name] \\[text]", "Add a note to a contact")
    table.add_row("edit-note \\[name] \\[#] \\[new text]", "Edit a note by index")
    table.add_row("delete-note \\[name] \\[#]", "Delete a note by index")
    table.add_row("show-notes \\[name]", "Show all notes for a contact")
    table.add_row("show-all-notes", "Show all notes across all contacts")
    table.add_row("all-with-notes", "Show all contacts with all fields including notes")
    table.add_row("find-notes \\[query]", "Search notes across all contacts")
    table.add_row("help", "Show this message")
    table.add_row("close / exit", "Quit the bot")

    console.print(table)