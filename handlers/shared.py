"""Cross-cutting helpers shared by the per-field handler modules.

Kept separate so each field module (contact/phone/email/address/birthday) can
reuse lookup, argument-splitting and interactive prompts without importing one
another, which previously caused a contact<->birthday cross-import.
"""

from models import Phone, Email, Birthday


def _validate_name(name):
    parts = name.split()
    if not parts:
        return "Error: Name is required."

    for part in parts:
        if not part.isalpha():
            return f"Error: '{part}' must contain only letters."
    return None


def _split_name_and_value(args):
    # A name may be several words, so we can't assume a fixed position for a
    # trailing value (phone, birthday): it's only a value when it carries digits
    # (names never do, since _validate_name forbids them).
    # Returns (name_parts: list[str], value: str | None).
    if len(args) >= 2 and any(ch.isdigit() for ch in args[-1]):
        return args[:-1], args[-1]
    return args, None


def _split_name_and_email(args):
    # Emails carry no digits requirement but always contain '@', so that marks
    # the trailing value and keeps a multi-word name intact.
    # Returns (name_parts: list[str], email: str | None).
    if len(args) >= 2 and "@" in args[-1]:
        return args[:-1], args[-1]
    return args, None


def _require_record(book, name):
    # Centralizes the "look up or fail" step so every field command reports a
    # missing contact the same way (KeyError -> friendly message via input_error).
    record = book.find(name)
    if not record:
        raise KeyError(name)
    return record


def _choose_from(items, render, prompt):
    # Shared picker for multi-valued fields (phones, emails) so the user can
    # select an entry by number instead of retyping it.
    # items: list of objects; render: callable(item)->str. Returns the chosen
    # item, or None if the input was cancelled or invalid.
    for i, item in enumerate(items, 1):
        print(f"  [{i}] {render(item)}")
    choice = input(prompt).strip()
    try:
        idx = int(choice) - 1
    except ValueError:
        return None
    if 0 <= idx < len(items):
        return items[idx]
    return None


def _get_mandatory_name():
    while True:
        name_input = input("Enter name and surname: ").strip()

        full_name = name_input.title()

        if not full_name:
            print("Error: Name is mandatory.")
            continue

        error = _validate_name(full_name)
        if not error:
            return full_name
        print(error)


def _get_mandatory_phone():
    while True:
        phone = input("Enter phone (10 digits, mandatory): ").strip()
        if not phone:
            print("Error: Phone number is mandatory.")
            continue
        try:
            Phone(phone)
            return phone
        except ValueError as e:
            print(f"Error: {e}")


def _get_optional_email():
    while True:
        email = input("Enter email (optional): ").strip()

        if not email:
            return None

        try:
            Email(email)
            return email
        except ValueError as e:
            print(f"Error: {e}")


def _get_mandatory_email():
    while True:
        email = input("Enter email: ").strip()
        if not email:
            print("Error: Email is mandatory.")
            continue
        try:
            Email(email)
            return email
        except ValueError as e:
            print(f"Error: {e}")


def _get_optional_birthday():
    while True:
        birthday = input("Enter birthday (DD.MM.YYYY, optional): ").strip()

        if not birthday:
            return None

        try:
            Birthday(birthday)
            return birthday
        except ValueError as e:
            print(f"Error: {e}")


def _get_address_details():
    print("Address details:")
    while True:
        country = input("  Enter Country: ").strip()
        if country:
            break

        print("Error: Country is mandatory.")
    while True:
        city = input("  Enter City: ").strip()
        if city:
            break

        print("Error: City is mandatory.")

    street = input("  Enter Street: ").strip()
    house = input("  Enter House number: ").strip()

    apt = input("  Enter Apartment number (optional): ").strip()
    zip_code = input("  Enter Zip code (optional): ").strip()

    address_parts = [country, city, street, house]
    if apt:
        address_parts.append(f"apt. {apt}")
    if zip_code:
        address_parts.append(zip_code)

    return ", ".join(filter(None, address_parts))
