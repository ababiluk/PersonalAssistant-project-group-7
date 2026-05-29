from models import Phone, Email, Birthday
from handlers.exceptions import OperationCancelled, FinishContactInput


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
    print("Address details (type 'cancel' to stop and save entered data):")
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


# Request optional note
def _get_optional_note():
    note = input("Enter note (optional): ").strip()

    if note.lower() == "cancel":
        raise FinishContactInput()

    return note if note else None


# Request optional tags separated by commas
def _get_optional_tags():
    tags = input("Enter tags separated by comma (optional): ").strip()

    if tags.lower() == "cancel":
        raise FinishContactInput()

    if not tags:
        return []

    return [tag.strip() for tag in tags.split(",") if tag.strip()]


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
