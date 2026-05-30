"""Cross-cutting helpers shared by the per-field handler modules.

Kept separate so each field module (contact/phone/email/address/birthday) can
reuse lookup, argument-splitting and interactive prompts without importing one
another, which previously caused a contact<->birthday cross-import.
"""

from models import Phone, Email, Birthday, Name
from handlers.exceptions import FinishContactInput


def _check_cancel(value):
    # Allow the user to type "cancel" at any interactive prompt to stop gracefully
    # instead of Ctrl+C, so already-entered data can be saved.
    if value.strip().lower() == "cancel":
        raise FinishContactInput()


def _validate_name(name):
    # Delegate to the Name model so the rules live in one place; return the
    # message (for re-prompting in interactive entry) instead of raising.
    try:
        Name(name)
        return None
    except ValueError as e:
        return f"Error: {e}"


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


def _choose_many(items, render, prompt):
    # Like _choose_from but for multi-delete: the user can enter several numbers
    # (comma/space separated) or 'all'. Returns the chosen items (de-duplicated,
    # order preserved), or an empty list on blank/invalid input.
    for i, item in enumerate(items, 1):
        print(f"  [{i}] {render(item)}")
    raw = input(prompt).strip().lower()
    if not raw:
        return []
    if raw == "all":
        return list(items)
    chosen = []
    for token in raw.replace(",", " ").split():
        try:
            idx = int(token) - 1
        except ValueError:
            continue
        if 0 <= idx < len(items) and items[idx] not in chosen:
            chosen.append(items[idx])
    return chosen


def _get_mandatory_name():
    while True:
        name_input = input("Enter name and surname (or 'cancel'): ").strip()
        _check_cancel(name_input)
        full_name = name_input.title()
        if not full_name:
            print("Error: Name is mandatory.")
            continue
        error = _validate_name(full_name)
        if not error:
            return full_name
        print(error)


def _get_mandatory_phone(label="Enter phone"):
    # Tell the user exactly what to type and how it will be shown, since the stored
    # value is normalized to a +38(0XX)XXX-XX-XX mask on output. The label is
    # parameterized so edit-phone can ask for the "new phone".
    prompt = f"{label} - 10 digits, e.g. 0991234567 -> +38(099)123-45-67 (or 'cancel'): "
    while True:
        phone = input(prompt).strip()
        _check_cancel(phone)
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
        email = input("Enter email (optional, or 'cancel' to stop): ").strip()
        if email.lower() == "cancel":
            raise FinishContactInput()
        if not email:
            return None
        try:
            Email(email)
            return email
        except ValueError as e:
            print(f"Error: {e}")


def _get_mandatory_email(prompt="Enter email: "):
    # Prompt is parameterized so edit-email can ask for the "new email" instead.
    while True:
        email = input(prompt).strip()
        _check_cancel(email)
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
        birthday = input("Enter birthday (DD.MM.YYYY, optional, or 'cancel' to stop): ").strip()
        if birthday.lower() == "cancel":
            raise FinishContactInput()
        if not birthday:
            return None
        try:
            Birthday(birthday)
            return birthday
        except ValueError as e:
            print(f"Error: {e}")


def _get_address_details():
    # Cancel at any field saves what was already entered instead of discarding it.
    print("Address details (type 'cancel' at any step to stop and save):")
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

    address_parts = [country, city, street, house]
    if apt and apt.lower() != "cancel":
        address_parts.append(f"apt. {apt}")
    if zip_code and zip_code.lower() != "cancel":
        address_parts.append(zip_code)

    return ", ".join(filter(None, address_parts))


def _get_optional_note():
    # Prompted during interactive add so the user can attach a note in one flow.
    note = input("Enter note (optional, or 'cancel' to stop): ").strip()
    if note.lower() == "cancel":
        raise FinishContactInput()
    return note if note else None


def _get_optional_tags():
    # Comma-separated tags for the note collected during interactive add.
    tags = input("Enter tags, comma-separated (optional, or 'cancel' to stop): ").strip()
    if tags.lower() == "cancel":
        raise FinishContactInput()
    if not tags:
        return []
    return [tag.strip() for tag in tags.split(",") if tag.strip()]
