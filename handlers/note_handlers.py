from decorators import input_error
from models import AddressBook
from rich.table import Table
from rich.console import Console
from handlers.display import show_paginated_table

console = Console()


def _next_note_id(book):
    # IDs are unique across the whole book (not per contact) so a note can be
    # referenced unambiguously; take max-so-far + 1 to avoid reusing a deleted id.
    all_ids = [note.id for record in book.data.values() for note in record.notes]
    return max(all_ids, default=0) + 1


def _print_notes_table(record):
    table = Table(header_style="bold cyan")
    table.add_column("ID", style="dim", width=6)
    table.add_column("Note", style="white")
    table.add_column("Tags", style="yellow")
    for note in record.notes:
        tags_str = ", ".join(note.tags) if note.tags else "—"
        table.add_row(str(note.id), note.value, tags_str)
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
def add_tag(args, book: AddressBook):
    if not args:
        return "Error: Usage: add-tag [name]"
    name = args[0]
    record = book.find(name)
    if not record:
        return f"Error: Contact '{name}' not found."
    if not record.notes:
        return f"Error: '{name}' has no notes."

    _print_notes_table(record)
    try:
        note_id = int(input("Enter note ID to add a tag: ").strip())
    except ValueError:
        return "Error: ID must be a number."
        
    tag = input("Enter tag (e.g. work, important): ").strip()
    if not tag:
        return "Error: Tag cannot be empty."
        
    try:
        record.add_tag_to_note(note_id, tag)
    except IndexError as e:
        return f"Error: {e}"
        
    return f"Tag '{tag}' added to note #{note_id}."


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
    table.add_column("Tags", style="yellow")
    
    for note in record.notes:
        tags_str = ", ".join(note.tags) if note.tags else "—"
        table.add_row(str(note.id), note.value, tags_str)
    return table


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
        email = "; ".join(e.value for e in record.emails) or "—"
        birthday = str(record.birthday) if record.birthday else "—"
        address = str(record.address) if record.address else "—"

        notes_list = []
        all_tags = []
        for n in record.notes:
            notes_list.append(f"[{n.id}] {n.value}")
            all_tags.extend(n.tags)

        notes_text = "\n".join(notes_list) or "—"
        tags_text = ", ".join(dict.fromkeys(all_tags)) or "—"
        rows.append((record.name.value, phones, email, birthday, address, notes_text, tags_text))

    return show_paginated_table("All Contacts", columns, rows)


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


@input_error
def find_notes(args, book: AddressBook):
    if not args:
        return "Error: Usage: find-notes [query]"
    query = " ".join(args).lower()
    results = []

    for record in book.data.values():
        for note in record.notes:
            # Match against both text and tags so a tag-only hit still surfaces the note.
            in_text = query in note.value.lower()
            in_tags = any(query == t.lower() for t in note.tags)
            
            if in_text or in_tags:
                results.append((record.name.value, note.id, note.value, note.tags))

    if not results:
        return f"No notes found for query '{query}'."

    columns = [
        ("Contact", {"style": "green"}),
        ("ID", {"style": "dim", "width": 6}),
        ("Note", {"style": "white"}),
        ("Tags", {"style": "yellow"}),
    ]
    rows = [(name, str(nid), text, ", ".join(tags) if tags else "—")
            for name, nid, text, tags in results]
    return show_paginated_table(f"Notes matching '{query}'", columns, rows)


@input_error
def find_by_tag(args, book: AddressBook):
    if not args:
        return "Error: Usage: find-by-tag [tag]"
    tag_query = args[0].lower()
    results = []

    for record in book.data.values():
        for note in record.notes:
            if any(tag_query == t.lower() for t in note.tags):
                results.append((record.name.value, note.id, note.value, note.tags))

    if not results:
        return f"No notes found with tag '{tag_query}'."

    columns = [
        ("Contact", {"style": "green"}),
        ("ID", {"style": "dim", "width": 6}),
        ("Note", {"style": "white"}),
        ("Tags", {"style": "yellow"}),
    ]
    rows = [(name, str(nid), text, ", ".join(tags))
            for name, nid, text, tags in results]
    return show_paginated_table(f"Notes with tag '{tag_query}'", columns, rows)


@input_error
def sort_by_tags(args, book: AddressBook):
    results = []
    for record in book.data.values():
        for note in record.notes:
            if note.tags:
                results.append((record.name.value, note.id, note.value, note.tags))

    if not results:
        return "No notes with tags found."

    # Order by the first tag (case-insensitive) so notes group under the same tag.
    results.sort(key=lambda x: x[3][0].lower())

    columns = [
        ("Contact", {"style": "green"}),
        ("ID", {"style": "dim", "width": 6}),
        ("Note", {"style": "white"}),
        ("Tags", {"style": "yellow"}),
    ]
    rows = [(name, str(nid), text, ", ".join(tags))
            for name, nid, text, tags in results]
    return show_paginated_table("Notes Sorted by Tags", columns, rows)