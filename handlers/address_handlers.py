from decorators import input_error
from models import AddressBook
from handlers.shared import _require_record, _get_address_details


@input_error
def add_address(args, book: AddressBook):
    # Reuses the guided address sequence; refuses when one exists so the user is
    # routed through edit-address rather than silently overwriting.
    if not args:
        return "Error: Usage: add-address [name]"
    name = " ".join(args)
    record = _require_record(book, name)
    if record.address:
        return f"Error: '{name}' already has an address. Use edit-address."
    record.add_address(_get_address_details())
    return f"Address added to '{name}'."


@input_error
def edit_address(args, book: AddressBook):
    # Same guided sequence as add, but requires an existing address to replace.
    if not args:
        return "Error: Usage: edit-address [name]"
    name = " ".join(args)
    record = _require_record(book, name)
    if not record.address:
        return f"Error: '{name}' has no address. Use add-address."
    record.add_address(_get_address_details())
    return f"Address updated for '{name}'."


@input_error
def delete_address(args, book: AddressBook):
    if not args:
        return "Error: Usage: delete-address [name]"
    name = " ".join(args)
    record = _require_record(book, name)
    if not record.address:
        return f"Error: '{name}' has no address."
    record.remove_address()
    return f"Address removed from '{name}'."
