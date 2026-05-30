from decorators import input_error
from models import AddressBook, Record
from handlers.display import show_paginated_table
from handlers.exceptions import OperationCancelled, FinishContactInput
from handlers.contact_input import (
    _get_mandatory_name,
    _get_mandatory_phone,
    _handle_existing_contact,
    _get_address_details,
    _get_optional_birthday,
    _get_optional_email,
    _get_optional_note,
    _get_optional_tags,
)
import re


# Interactive contact creation:
# 1. Get mandatory data (name, phone)
# 2. Create or update contact
# 3. Collect optional data (email, birthday, address)
# 4. Save entered information
@input_error
def add_contact(args, book: AddressBook):
    print(
        "Type 'cancel' at any stage to finish contact creation and save entered data."
    )
    if len(args) >= 2:
        phone_input = args[-1]
        full_name = " ".join(args[:-1])
    else:
        full_name = _get_mandatory_name()
        phone_input = _get_mandatory_phone()
    try:
        record = book.find(full_name)

        # Find existing contact or create a new one
        if not record:
            record = Record(full_name)
            record.add_phone(phone_input)
            book.add_record(record)
            message = f"Contact '{full_name}' created."
        else:
            phone_message = _handle_existing_contact(record, phone_input)

            if phone_message is None:
                return "Operation cancelled."
            message = f"Contact '{full_name}' updated. {phone_message}"
        # Collect optional contact information
        email = _get_optional_email()
        if email:
            record.add_email(email)
        birthday = _get_optional_birthday()
        if birthday:
            record.add_birthday(birthday)
        address_string = None

        add_address = input("Add address? (y/n): ").strip().lower()
        if add_address == "cancel":
            raise FinishContactInput()
        # Save address if provided
        if add_address in ["y", "yes"]:
            address_string = _get_address_details()
            if address_string:
                record.add_address(address_string)

        note_text = _get_optional_note()

        if note_text:
            note_id = (
                max(
                    [note.id for r in book.data.values() for note in r.notes], default=0
                )
                + 1
            )

            record.add_note(note_text, note_id)

            tags = _get_optional_tags()

            for tag in tags:
                record.add_tag_to_note(note_id, tag)

        return f"{message} All details saved."
    except OperationCancelled:
        return "Operation cancelled."
    except FinishContactInput:
        return f"{message} Additional fields skipped."


@input_error
def change_contact(args, book: AddressBook):  # changing existing contact
    name, old_phone, new_phone = args
    record = book.find(name)
    if not record:
        raise KeyError(name)
    record.edit_phone(old_phone, new_phone)
    return "Contact updated."


@input_error
def show_phone(args, book: AddressBook):  # showing existing contact phones

    name = " ".join(args)
    record = book.find(name)
    if not record:
        raise KeyError(name)
    return "; ".join(str(p).value for p in record.phones)


@input_error
def show_all(args, book: AddressBook):  # show all contacts
    if not book.data:
        return "No contacts saved."
    return "\n".join(str(r) for r in book.data.values())


@input_error
def delete_contact(args, book: AddressBook):  # delete contact from address book
    name = args[0]
    record = book.find(name)
    if not record:
        raise KeyError(name)
    book.delete(name)
    return f"Contact '{name}' deleted."


@input_error
def remove_phone(args, book: AddressBook):  # remove specific phone from contact
    if len(args) < 2:
        return "Error: Please provide both name and phone."
    phone = args[-1]
    name = " ".join(args[:-1])
    phone_to_delete = re.sub(r"\D", "", phone)[-10:]
    record = book.find(name)
    if not record:
        raise KeyError(name)
    record.remove_phone(phone_to_delete)
    return "Phone removed."


@input_error
def add_email(args, book: AddressBook):  # adding email to existing contact
    email = args[-1]
    name = " ".join(args[:-1])
    record = book.find(name)
    if not record:
        raise KeyError(name)
    record.add_email(email)
    return "Email added."


@input_error
def edit_email(args, book: AddressBook):  # editing email for existing contact
    if len(args) < 2:
        return "Error: Usage: edit-email [name] [new_email]"
    new_email = args[-1]
    name = " ".join(args[:-1])
    record = book.find(name)
    if not record:
        raise KeyError(name)
    record.edit_email(new_email)
    return f"Email for '{name}' updated to {new_email}."


@input_error
def delete_email(args, book: AddressBook):  # removing email from contact
    if not args:
        return "Error: Usage: delete-email [name]"
    name = " ".join(args)
    record = book.find(name)
    if not record:
        raise KeyError(name)
    if not record.email:
        return f"Contact '{name}' doesn't have an email to delete."

    record.delete_email()
    return f"Email for '{name}' deleted."


@input_error
def find_contact(args, book: AddressBook):  # finding contact by name or phone
    search_query = args[0].lower()
    found_records = []

    for record in book.data.values():
        if search_query in record.name.value.lower():
            found_records.append(record)
            continue

        for phone in record.phones:
            if search_query in phone.value:
                found_records.append(record)
                break

    if not found_records:
        return "No contacts found."

    columns = [
        ("Name", {"style": "green"}),
        ("Phones", {}),
        ("Email", {}),
        ("Birthday", {}),
        ("Address", {}),
        ("Notes", {}),
        ("Tags", {}),
    ]
    rows = []
    for record in found_records:
        phones = "; ".join(p.value for p in record.phones) or "—"
        email = str(record.email) if record.email else "—"
        birthday = str(record.birthday) if record.birthday else "—"
        address = str(record.address) if record.address else "—"
        notes = "; ".join(note.value for note in record.notes) if record.notes else "—"

        tags = (
            "; ".join(tag for note in record.notes for tag in note.tags)
            if record.notes
            else "—"
        )
        rows.append((record.name.value, phones, email, birthday, address, notes, tags))

    return show_paginated_table(f"Search Results for '{args[0]}'", columns, rows)


@input_error
def rename_contact(args, book: AddressBook):
    old_name = input("Enter current contact name: ").strip()
    new_name = input("Enter new contact name: ").strip()

    book.rename_contact(old_name, new_name)

    return f"Contact renamed to '{new_name}'."
