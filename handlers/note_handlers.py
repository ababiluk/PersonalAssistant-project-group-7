from decorators import input_error
from models import AddressBook
from rich.table import Table
from rich.console import Console

console = Console()


# Generate the next unique note ID
def _next_note_id(book):
    all_ids = [note.id for record in book.data.values() for note in record.notes]
    return max(all_ids, default=0) + 1


# Display all notes of a contact in a formatted table
def _print_notes_table(record):
    table = Table(header_style="bold cyan")
    table.add_column("ID", style="dim", width=6)
    table.add_column("Note", style="white")
    table.add_column("Tags", style="yellow")  # add Tags column
    for note in record.notes:
        tags_str = ", ".join(note.tags) if note.tags else "—"
        table.add_row(str(note.id), note.value, tags_str)
    console.print(table)


# Add a new note to an existing contact
@input_error
def add_note(args, book: AddressBook):
    if not args:
        return (
            "Usage: add-note [name] | [text]\n"
            "Or run without arguments for interactive mode."
        )

    full_input = " ".join(args)

    if "|" not in full_input:
        return "Error: Use format: add-note [name] | [text]"

    name, text = full_input.split("|", 1)

    name = name.strip()
    text = text.strip()

    if not text:
        return "Error: Note text cannot be empty."

    record = book.find(name)
    if not record:
        return f"Error: Contact '{name}' not found."

    note_id = _next_note_id(book)
    record.add_note(text, note_id)
    return f"Note #{note_id} added to '{name}'."


# Edit an existing note by its ID
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


# Delete a note by its ID
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


# Command to attach a tag to a specific note
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
