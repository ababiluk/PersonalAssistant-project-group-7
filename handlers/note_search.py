from decorators import input_error
from models import AddressBook
from handlers.display import show_paginated_table


# Search notes by text or tag
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

    columns = [
        ("Contact", {"style": "green"}),
        ("ID", {"style": "dim", "width": 6}),
        ("Note", {"style": "white"}),
        ("Tags", {"style": "yellow"}),
    ]
    rows = [
        (name, str(nid), text, ", ".join(tags) if tags else "—")
        for name, nid, text, tags in results
    ]
    return show_paginated_table(f"Notes matching '{query}'", columns, rows)


# Filter notes by a specific tag
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
    rows = [
        (name, str(nid), text, ", ".join(tags)) for name, nid, text, tags in results
    ]
    return show_paginated_table(f"Notes with tag '{tag_query}'", columns, rows)


# Group and sort notes by tags alphabetically
@input_error
def sort_by_tags(args, book: AddressBook):
    results = []
    for record in book.data.values():
        for note in record.notes:
            if note.tags:
                results.append((record.name.value, note.id, note.value, note.tags))

    if not results:
        return "No notes with tags found."

    results.sort(key=lambda x: x[3][0].lower())

    columns = [
        ("Contact", {"style": "green"}),
        ("ID", {"style": "dim", "width": 6}),
        ("Note", {"style": "white"}),
        ("Tags", {"style": "yellow"}),
    ]
    rows = [
        (name, str(nid), text, ", ".join(tags)) for name, nid, text, tags in results
    ]
    return show_paginated_table("Notes Sorted by Tags", columns, rows)
