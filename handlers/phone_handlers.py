import re

from decorators import input_error
from models import AddressBook
from handlers.shared import (
    _require_record,
    _split_name_and_value,
    _choose_from,
    _choose_many,
    _get_mandatory_phone,
)


@input_error
def change_contact(args, book: AddressBook):  # edit-phone
    # Same flow as edit-email: pick the phone (auto if one, choose if several),
    # then prompt for the new number.
    if not args:
        return "Error: Usage: edit-phone [name]"
    name = " ".join(args)
    record = _require_record(book, name)
    if not record.phones:
        return f"Error: '{name}' has no phones."

    if len(record.phones) == 1:
        target = record.phones[0]
    else:
        target = _choose_from(record.phones, str, "Which phone to edit (number): ")
        if target is None:
            return "Operation cancelled."

    new_phone = _get_mandatory_phone("Enter new phone")
    record.edit_phone(target.value, new_phone)
    return f"Phone updated to {new_phone} for '{name}'."


@input_error
def add_phone(args, book: AddressBook):
    # Lets users grow an existing contact's phone list; the number can be passed
    # inline or entered interactively when only the name is given.
    if not args:
        return "Error: Usage: add-phone [name] [optional phone]"
    name_parts, phone = _split_name_and_value(args)
    name = " ".join(name_parts)
    record = _require_record(book, name)
    if phone is None:
        phone = _get_mandatory_phone()
    record.add_phone(phone)  # Phone() validates the number
    return f"Phone {phone} added to '{name}'."


@input_error
def remove_phone(args, book: AddressBook):
    # Deleting by name alone is allowed: one phone is removed directly, while with
    # several the user can pick one or many (so they needn't retype the numbers).
    if not args:
        return "Error: Usage: delete-phone [name] [optional phone]"
    name_parts, phone = _split_name_and_value(args)
    name = " ".join(name_parts)
    record = _require_record(book, name)

    if not record.phones:
        return f"Error: '{name}' has no phones."

    if phone is not None:
        record.remove_phone(re.sub(r"\D", "", phone)[-10:])
        return f"Phone removed from '{name}'."

    if len(record.phones) == 1:
        targets = [record.phones[0]]
    else:
        targets = _choose_many(
            record.phones, str,
            "Which phone(s) to delete (numbers, comma-separated, or 'all'): ",
        )
        if not targets:
            return "Operation cancelled."

    for target in targets:
        record.remove_phone(target.value)
    return f"Removed {len(targets)} phone(s) from '{name}'."
