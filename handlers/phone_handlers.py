import re

from decorators import input_error
from models import AddressBook
from handlers.shared import (
    _require_record,
    _split_name_and_value,
    _choose_from,
    _get_mandatory_phone,
)


@input_error
def change_contact(args, book: AddressBook):  # edit-phone: replace one number with another
    name, old_phone, new_phone = args
    record = _require_record(book, name)
    record.edit_phone(old_phone, new_phone)
    return "Contact updated."


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
    # Deleting by name alone is allowed: with one phone we remove it directly,
    # with several we let the user pick, so they needn't retype the number.
    if not args:
        return "Error: Usage: delete-phone [name] [optional phone]"
    name_parts, phone = _split_name_and_value(args)
    name = " ".join(name_parts)
    record = _require_record(book, name)

    if not record.phones:
        return f"Error: '{name}' has no phones."

    if phone is not None:
        phone_value = re.sub(r"\D", "", phone)[-10:]
    elif len(record.phones) == 1:
        phone_value = record.phones[0].value
    else:
        target = _choose_from(record.phones, str, "Which phone to delete (number): ")
        if target is None:
            return "Operation cancelled."
        phone_value = target.value

    record.remove_phone(phone_value)
    return f"Phone removed from '{name}'."
