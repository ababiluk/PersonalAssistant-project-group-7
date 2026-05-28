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
    table.add_column("Tags", style="yellow")  # add Tags column
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
    # command to attach a tag to a specific note
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
    table.add_column("Tags", style="yellow")  # add Tags column
    
    for note in record.notes:
        tags_str = ", ".join(note.tags) if note.tags else "—"
        table.add_row(str(note.id), note.value, tags_str)
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
        
        notes_list = []
        for n in record.notes:
            tag_str = f" [#{', #'.join(n.tags)}]" if n.tags else ""
            notes_list.append(f"[{n.id}] {n.value}{tag_str}")
            
        notes_text = "\n".join(notes_list) or "—"
        table.add_row(record.name.value, phones, email, birthday, notes_text)

    return table


@input_error
def show_all_notes(args, book: AddressBook):
    results = []
    for record in book.data.values():
        for note in record.notes:
            results.append((record.name.value, note.id, note.value, note.tags))

    if not results:
        return "No notes saved."

    table = Table(title="All Notes", header_style="bold cyan")
    table.add_column("Contact", style="green")
    table.add_column("ID", style="dim", width=6)
    table.add_column("Note", style="white")
    table.add_column("Tags", style="yellow")

    for contact_name, note_id, text, tags in results:
        tags_str = ", ".join(tags) if tags else "—"
        table.add_row(contact_name, str(note_id), text, tags_str)

    return table


@input_error
def find_notes(args, book: AddressBook):
    if not args:
        return "Error: Usage: find-notes [query]"
    query = " ".join(args).lower()
    results = []

    for record in book.data.values():
        for note in record.notes:
            # search in text and in tags
            in_text = query in note.value.lower()
            in_tags = any(query == t.lower() for t in note.tags)
            
            if in_text or in_tags:
                results.append((record.name.value, note.id, note.value, note.tags))

    if not results:
        return f"No notes found for query '{query}'."

    table = Table(title=f"Notes matching '{query}'", header_style="bold cyan")
    table.add_column("Contact", style="green")
    table.add_column("ID", style="dim", width=6)
    table.add_column("Note", style="white")
    table.add_column("Tags", style="yellow")

    for contact_name, note_id, text, tags in results:
        tags_str = ", ".join(tags) if tags else "—"
        table.add_row(contact_name, str(note_id), text, tags_str)

    return table


@input_error
def find_by_tag(args, book: AddressBook):
    # filter notes by a specific tag
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

    table = Table(title=f"Notes with tag '{tag_query}'", header_style="bold cyan")
    table.add_column("Contact", style="green")
    table.add_column("ID", style="dim", width=6)
    table.add_column("Note", style="white")
    table.add_column("Tags", style="yellow")

    for contact_name, note_id, text, tags in results:
        tags_str = ", ".join(tags)
        table.add_row(contact_name, str(note_id), text, tags_str)

    return table


@input_error
def sort_by_tags(args, book: AddressBook):
    # group and sort notes by tags alphabetically
    results = []
    for record in book.data.values():
        for note in record.notes:
            if note.tags:
                results.append((record.name.value, note.id, note.value, note.tags))

    if not results:
        return "No notes with tags found."

    # sort by the first tag alphabetically
    results.sort(key=lambda x: x[3][0].lower())

    table = Table(title="Notes Sorted by Tags", header_style="bold cyan")
    table.add_column("Contact", style="green")
    table.add_column("ID", style="dim", width=6)
    table.add_column("Note", style="white")
    table.add_column("Tags", style="yellow")

    for contact_name, note_id, text, tags in results:
        tags_str = ", ".join(tags)
        table.add_row(contact_name, str(note_id), text, tags_str)

    return table