from decorators import input_error
from models import AddressBook, Phone, Record, Email, Birthday
from rich.table import Table
from handlers.display import show_paginated_table
from handlers.exceptions import OperationCancelled, FinishContactInput
import re


# Validate full name: only letters and spaces are allowed
def _validate_name(name):
    parts = name.split()
    if not parts:
        return "Error: Name is required."

    for part in parts:
        if not part.isalpha():
            return f"Error: '{part}' must contain only letters."
    return None


# Check if user wants to cancel current operation
def _check_cancel(value):
    if value.lower() == "cancel":
        raise OperationCancelled()


# Handle adding a phone to an existing contact
# Allows user to add a new phone or replace an existing one
def _handle_existing_contact(record, new_phone):
    print(f"Contact '{record.name.value}' already exists.")

    if record.phones:
        print(f"  Current phones: {'; '.join(p.value for p in record.phones)}")

    print("1 - Add as new phone\n2 - Replace existing phone\n3 - Cancel")
    choice = input("Your choice: ").strip()
    _check_cancel(choice)

    if choice == "1":
        record.add_phone(new_phone)
        return "New phone added."
    elif choice == "2":
        if not record.phones:
            record.add_phone(new_phone)
            return "Phone added."

        print("Which phone to replace?")
        for i, p in enumerate(record.phones, 1):
            print(f"    [{i}] {p.value}")

        idx = input("Number: ").strip()
        _check_cancel(idx)
        try:
            old_phone = record.phones[int(idx) - 1].value
            record.edit_phone(old_phone, new_phone)
            return f"Phone {old_phone} replaced with {new_phone}."
        except (ValueError, IndexError):
            raise ValueError("Invalid choice. Phone update canceled.")

    return None


# Request and validate mandatory contact name
def _get_mandatory_name():
    while True:
        name_input = input("Enter name and surname: ").strip()

        _check_cancel(name_input)

        full_name = name_input.title()

        if not full_name:
            print("Error: Name is mandatory.")
            continue

        error = _validate_name(full_name)
        if not error:
            return full_name
        print(error)


# Request and validate mandatory phone number
def _get_mandatory_phone():
    while True:
        phone = input("Enter phone (10 digits, mandatory): ").strip()

        _check_cancel(phone)
        if not phone:
            print("Error: Phone number is mandatory.")
            continue
        try:
            Phone(phone)
            return phone
        except ValueError as e:
            print(f"Error: {e}")


# Request optional email
# Returns None if skipped
def _get_optional_email():
    while True:
        email = input("Enter email (optional): ").strip()

        if email.lower() == "cancel":
            raise FinishContactInput()
        if not email:
            return None

        try:
            Email(email)
            return email
        except ValueError as e:
            print(f"Error: {e}")


# Request optional birthday
# Returns None if skipped
def _get_optional_birthday():
    while True:
        birthday = input("Enter birthday (DD.MM.YYYY, optional): ").strip()

        if birthday.lower() == "cancel":
            raise FinishContactInput()
        if not birthday:
            return None

        try:
            Birthday(birthday)
            return birthday
        except ValueError as e:
            print(f"Error: {e}")


# Collect address information step by step
# Save already entered address data if user stops input with 'cancel'
def _get_address_details():
    print("Address details:")
    while True:
        country = input("  Enter Country: ").strip()
        if country.lower() == "cancel":
            raise FinishContactInput()
        if country:
            break

        print("Error: Country is mandatory.")
    while True:
        city = input("  Enter City: ").strip()
        if city.lower() == "cancel":
            raise FinishContactInput()
        if city:
            break

        print("Error: City is mandatory.")

    street = input("  Enter Street: ").strip()

    if street.lower() == "cancel":
        return ", ".join(filter(None, [country, city]))
    
    
    house = input("  Enter House number: ").strip()

    if house.lower() == "cancel":
        return ", ".join(filter(None, [country, city, street]))

    apt = input("  Enter Apartment number (optional): ").strip()

    if apt.lower() == "cancel":
        return ", ".join(filter(None, [country, city, street, house]))
    
    zip_code = input("  Enter Zip code (optional): ").strip()

    if zip_code.lower() == "cancel":
        address_parts = [country, city, street, house]

        if apt:
            address_parts.append(f"apt. {apt}")

        return ", ".join(filter(None, address_parts))
    
    address_parts = [country, city, street, house]

    if apt:
        address_parts.append(f"apt. {apt}")

    if zip_code:
        address_parts.append(zip_code)

    return ", ".join(filter(None, address_parts))


# Interactive contact creation:
# 1. Get mandatory data (name, phone)
# 2. Create or update contact
# 3. Collect optional data (email, birthday, address)
# 4. Save entered information
@input_error
def add_contact(args, book: AddressBook):
    try:
        full_name = _get_mandatory_name()

        record = book.find(full_name)

        phone_input = _get_mandatory_phone()
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
        # Save address if provided
        if add_address in ["y", "yes"]:
            address_string = _get_address_details()

        
        if address_string:
            record.add_address(address_string)

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
    name, email = args
    record = book.find(name)
    if not record:
        raise KeyError(name)
    record.add_email(email)
    return "Email added."


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
    ]
    rows = []
    for record in found_records:
        phones = "; ".join(p.value for p in record.phones) or "—"
        email = str(record.email) if record.email else "—"
        birthday = str(record.birthday) if record.birthday else "—"
        address = str(record.address) if record.address else "—"
        rows.append((record.name.value, phones, email, birthday, address))

    return show_paginated_table(f"Search Results for '{args[0]}'", columns, rows)
