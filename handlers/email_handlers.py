from decorators import input_error
from models import AddressBook
from handlers.shared import (
    _require_record,
    _split_name_and_email,
    _choose_from,
    _get_mandatory_email,
)


@input_error
def add_email(args, book: AddressBook):
    # Emails are multi-valued, so add-email appends rather than overwrites; the
    # address can be inline or prompted when only the name is supplied.
    if not args:
        return "Error: Usage: add-email [name] [optional email]"
    name_parts, email = _split_name_and_email(args)
    name = " ".join(name_parts)
    record = _require_record(book, name)
    if email is None:
        email = _get_mandatory_email()
    if record.find_email(email):
        return f"Error: '{name}' already has email {email}."
    record.add_email(email)  # Email() validates the address
    return f"Email {email} added to '{name}'."


@input_error
def edit_email(args, book: AddressBook):
    # With several emails we ask which one to change so the right entry is replaced.
    if not args:
        return "Error: Usage: edit-email [name]"
    name = " ".join(args)
    record = _require_record(book, name)
    if not record.emails:
        return f"Error: '{name}' has no emails."

    if len(record.emails) == 1:
        target = record.emails[0]
    else:
        target = _choose_from(record.emails, lambda e: e.value, "Which email to edit (number): ")
        if target is None:
            return "Operation cancelled."

    new_email = _get_mandatory_email()
    record.edit_email(target.value, new_email)
    return f"Email updated to {new_email} for '{name}'."


@input_error
def delete_email(args, book: AddressBook):
    # Mirrors delete-phone: by name alone we auto-pick a lone email or let the
    # user choose, otherwise the inline email is removed.
    if not args:
        return "Error: Usage: delete-email [name] [optional email]"
    name_parts, email = _split_name_and_email(args)
    name = " ".join(name_parts)
    record = _require_record(book, name)

    if not record.emails:
        return f"Error: '{name}' has no emails."

    if email is None:
        if len(record.emails) == 1:
            email = record.emails[0].value
        else:
            target = _choose_from(record.emails, lambda e: e.value, "Which email to delete (number): ")
            if target is None:
                return "Operation cancelled."
            email = target.value

    record.remove_email(email)
    return f"Email removed from '{name}'."
