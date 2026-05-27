from decorators import input_error
from models import AddressBook, Phone, Record, Email, Birthday
from rich.table import Table


def _validate_name(name):
    parts = name.split()
    if len(parts) == 0:
        return "Error: Name is required."

    for part in parts:
        if not part.isalpha():
            return f"Error: '{part}' must contain only letters."
        if not part.istitle():
            return "Error: Name parts must start with a capital letter."

    return None


def _handle_existing_contact(
    record, new_phone
):  # interactive prompt when contact already exists
    print(f"Contact '{record.name.value}' already exists.")

    if record.phones:
        print(f"  Current phones: {'; '.join(p.value for p in record.phones)}")

    print("1 - Add as new phone\n2 - Replace existing phone\n3 - Cancel")
    choice = input("Your choice: ").strip()

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
        try:
            old_phone = record.phones[int(idx) - 1].value
            record.edit_phone(old_phone, new_phone)
            return f"Phone {old_phone} replaced with {new_phone}."
        except (ValueError, IndexError):
            raise ValueError("Invalid choice. Phone update canceled.")

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


@input_error
def add_contact(args, book: AddressBook):
    full_name = _get_mandatory_name()

    record = book.find(full_name)

    phone_input = _get_mandatory_phone()

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

    email = _get_optional_email()
    birthday = _get_optional_birthday()
    address_string = None

    add_address = input("Add address? (y/n): ").strip().lower()

    if add_address in ["y", "yes"]:
        address_string = _get_address_details()

    if email:
        record.add_email(email)
    if birthday:
        record.add_birthday(birthday)
    if address_string:
        record.add_address(address_string)

    return f"{message} All details saved."


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
    name = args[0]
    record = book.find(name)
    if not record:
        raise KeyError(name)
    return "; ".join(p.value for p in record.phones)


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
    name, phone = args
    record = book.find(name)
    if not record:
        raise KeyError(name)
    record.remove_phone(phone)
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
        
    table = Table(title=f"Search Results for '{args[0]}'", header_style="bold cyan")
    table.add_column("Name", style="green")
    table.add_column("Phones")
    table.add_column("Email")
    table.add_column("Birthday")
    
    for record in found_records:
        phones = "; ".join(p.value for p in record.phones) or "—"
        email = str(record.email) if record.email else "—"
        birthday = str(record.birthday) if record.birthday else "—"
        table.add_row(record.name.value, phones, email, birthday)
        
    return table