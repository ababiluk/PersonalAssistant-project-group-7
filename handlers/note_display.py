from decorators import input_error
from models import AddressBook
from rich.table import Table
from handlers.display import show_paginated_table


# Show all notes for a specific contact
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
    table.add_column("Tags", style="yellow")  # add Tags column

    for note in record.notes:
        tags_str = ", ".join(note.tags) if note.tags else "—"
        table.add_row(str(note.id), note.value, tags_str)
    return table


# Display all contacts with notes and tags
@input_error
def all_with_notes(args, book: AddressBook):
    if not book.data:
        return "No contacts saved."

    columns = [
        ("Name", {"style": "green"}),
        ("Phones", {}),
        ("Email", {}),
        ("Birthday", {}),
        ("Address", {}),
        ("Notes", {}),
        ("Tags", {"style": "yellow"}),
    ]
    rows = []
    for record in book.data.values():
        phones = "; ".join(p.value for p in record.phones) or "—"
        email = str(record.email) if record.email else "—"
        birthday = str(record.birthday) if record.birthday else "—"
        address = str(record.address) if record.address else "—"

        notes_list = []
        all_tags = []
        for n in record.notes:
            notes_list.append(f"[{n.id}] {n.value}")
            all_tags.extend(n.tags)

        notes_text = "\n".join(notes_list) or "—"
        tags_text = ", ".join(dict.fromkeys(all_tags)) or "—"
        rows.append(
            (record.name.value, phones, email, birthday, address, notes_text, tags_text)
        )

    return show_paginated_table("All Contacts", columns, rows)


# Show every note from all contacts
@input_error
def show_all_notes(args, book: AddressBook):
    rows = []
    for record in book.data.values():
        for note in record.notes:
            tags_str = ", ".join(note.tags) if note.tags else "—"
            rows.append((record.name.value, str(note.id), note.value, tags_str))

    if not rows:
        return "No notes saved."

    columns = [
        ("Contact", {"style": "green"}),
        ("ID", {"style": "dim", "width": 6}),
        ("Note", {"style": "white"}),
        ("Tags", {"style": "yellow"}),
    ]
    return show_paginated_table("All Notes", columns, rows)
