import csv
import json
import os
from datetime import datetime
from decorators import input_error
from models import AddressBook

EXPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "exported_files")


# Convert a Record object into a dictionary for export
def _record_to_dict(record):
    return {
        "name": record.name.value,
        "phones": [p.value for p in record.phones],
        "email": str(record.email) if record.email else "",
        "birthday": str(record.birthday) if record.birthday else "",
        "address": str(record.address) if record.address else "",
        "notes": [
            {"id": note.id, "text": note.value, "tags": note.tags}
            for note in record.notes
        ],
    }


# Generate a timestamped default filename
def _default_filename(fmt):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"address_book_{timestamp}.{fmt}"


# Resolve export path and create export directory if needed
def _resolve_path(filename, fmt):
    if not filename.endswith(f".{fmt}"):
        filename += f".{fmt}"
    if os.path.isabs(filename) or os.sep in filename or "/" in filename:
        return filename
    os.makedirs(EXPORT_DIR, exist_ok=True)
    return os.path.join(EXPORT_DIR, filename)


# Export address book data to JSON format
def _export_json(book, filepath):
    data = [_record_to_dict(r) for r in book.data.values()]
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# Export address book data to CSV format
def _export_csv(book, filepath):
    fieldnames = [
        "name",
        "phones",
        "email",
        "birthday",
        "address",
        "note_id",
        "note_text",
        "note_tags",
    ]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for record in book.data.values():
            base = {
                "name": record.name.value,
                "phones": "; ".join(p.value for p in record.phones),
                "email": str(record.email) if record.email else "",
                "birthday": str(record.birthday) if record.birthday else "",
                "address": str(record.address) if record.address else "",
            }
            if record.notes:
                for note in record.notes:
                    writer.writerow(
                        {
                            **base,
                            "note_id": note.id,
                            "note_text": note.value,
                            "note_tags": "; ".join(note.tags),
                        }
                    )
            else:
                writer.writerow(
                    {**base, "note_id": "", "note_text": "", "note_tags": ""}
                )


# Export address book to a file in CSV or JSON format
@input_error
def export_book(args, book: AddressBook):
    if not book.data:
        return "Address book is empty — nothing to export."

    fmt = args[0].lower() if args else ""
    if fmt not in ("csv", "json"):
        return "Error: Usage: export-book [csv|json] [optional: path/filename]"

    custom_path = args[1] if len(args) > 1 else None
    if custom_path:
        filepath = (
            custom_path if custom_path.endswith(f".{fmt}") else custom_path + f".{fmt}"
        )
    else:
        filepath = _resolve_path(_default_filename(fmt), fmt)

    if fmt == "json":
        _export_json(book, filepath)
    else:
        _export_csv(book, filepath)

    return f"Address book exported to '{filepath}' ({len(book.data)} contacts)."