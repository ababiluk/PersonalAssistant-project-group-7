from decorators import input_error
from models import AddressBook
from rich.table import Table
from rich.console import Console

console = Console()


def _next_note_id(book):
    all_ids = [note.id for record in book.data.values() for note in record.notes]
    return max(all_ids, default=0) + 1


def _print_notes_table(record):
    table = Table(header_style="bold cyan")
    table.add_column("ID", style="dim", width=6)
    table.add_column("Note", style="white")
    for note in record.notes:
        table.add_row(str(note.id), note.value)
    console.print(table)


@input_error
def add_note(args, book: AddressBook):
    if not args:
        return "Error: Usage: add-note [name] [text]"
    name = args[0]
    record = book.find(name)
    if not record:
        return f"Error: Contact '{name}' not found."
    if len(args) < 2:
        return "Error: Usage: add-note [name] [text]"
    text = " ".join(args[1:])
    note_id = _next_note_id(book)
    record.add_note(text, note_id)
    return f"Note #{note_id} added to '{name}'."


@input_error
def edit_note(args, book: AddressBook):
    if not args:
        return "Error: Usage: edit-note [name]"
    name = args[0]
    record = book.find(name)
    if not record:
        return f"Error: Contact '{name}' not found."
    if not record.notes:
        return f"Error: '{name}' has no notes."

    _print_notes_table(record)
    try:
        note_id = int(input("Enter note ID to edit: ").strip())
    except ValueError:
        return "Error: ID must be a number."
    new_text = input("Enter new text: ").strip()
    if not new_text:
        return "Error: Note text cannot be empty."
    record.edit_note(note_id, new_text)
    return f"Note #{note_id} updated."


@input_error
def delete_note(args, book: AddressBook):
    if not args:
        return "Error: Usage: delete-note [name]"
    name = args[0]
    record = book.find(name)
    if not record:
        return f"Error: Contact '{name}' not found."
    if not record.notes:
        return f"Error: '{name}' has no notes."

    _print_notes_table(record)
    try:
        note_id = int(input("Enter note ID to delete: ").strip())
    except ValueError:
        return "Error: ID must be a number."
    record.delete_note(note_id)
    return f"Note #{note_id} deleted."


@input_error
def show_notes(args, book: AddressBook):
    if not args:
        return "Error: Usage: show-notes [name]"
    name = args[0]
    record = book.find(name)
    if not record:
        return f"Error: Contact '{name}' not found."
    if not record.notes:
        return f"No notes for '{name}'."

    table = Table(title=f"Notes: {name}", header_style="bold cyan")
    table.add_column("ID", style="dim", width=6)
    table.add_column("Note", style="white")
    for note in record.notes:
        table.add_row(str(note.id), note.value)
    return table


@input_error
def all_with_notes(args, book: AddressBook):
    if not book.data:
        return "No contacts saved."

    table = Table(title="All Contacts", header_style="bold cyan")
    table.add_column("Name", style="green")
    table.add_column("Phones")
    table.add_column("Email")
    table.add_column("Birthday")
    table.add_column("Notes")

    for record in book.data.values():
        phones = "; ".join(p.value for p in record.phones) or "—"
        email = str(record.email) if record.email else "—"
        birthday = str(record.birthday) if record.birthday else "—"
        notes_text = "\n".join(f"[{n.id}] {n.value}" for n in record.notes) or "—"
        table.add_row(record.name.value, phones, email, birthday, notes_text)

    return table


@input_error
def show_all_notes(args, book: AddressBook):
    results = []
    for record in book.data.values():
        for note in record.notes:
            results.append((record.name.value, note.id, note.value))

    if not results:
        return "No notes saved."

    table = Table(title="All Notes", header_style="bold cyan")
    table.add_column("Contact", style="green")
    table.add_column("ID", style="dim", width=6)
    table.add_column("Note", style="white")

    for contact_name, note_id, text in results:
        table.add_row(contact_name, str(note_id), text)

    return table


@input_error
def find_notes(args, book: AddressBook):
    if not args:
        return "Error: Usage: find-notes [query]"
    query = " ".join(args).lower()
    results = []

    for record in book.data.values():
        for note in record.notes:
            if query in note.value.lower():
                results.append((record.name.value, note.id, note.value))

    if not results:
        return f"No notes found for query '{query}'."

    table = Table(title=f"Notes matching '{query}'", header_style="bold cyan")
    table.add_column("Contact", style="green")
    table.add_column("ID", style="dim", width=6)
    table.add_column("Note", style="white")

    for contact_name, note_id, text in results:
        table.add_row(contact_name, str(note_id), text)

    return table
