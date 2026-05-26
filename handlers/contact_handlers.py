from decorators import input_error
from models import AddressBook, Record


def _validate_name(name):  # validation of name
    if not name.isalpha():
        return "Error: name must contain only letters."
    return None


def _handle_existing_contact(record, phone):  # interactive prompt when contact already exists
    print(f"Contact '{record.name.value}' already exists.")
    if record.phones:
        print(f"  Current phones: {'; '.join(p.value for p in record.phones)}")
    print("  [1] Add new phone  [2] Replace existing phone  [3] Cancel")
    choice = input("Your choice: ").strip()

    if choice == "1":
        record.add_phone(phone)
        return "Phone added."
    elif choice == "2":
        if not record.phones:
            record.add_phone(phone)
            return "Phone added."
        print("  Which phone to replace?")
        for i, p in enumerate(record.phones, 1):
            print(f"    [{i}] {p.value}")
        idx = input("Number: ").strip()
        try:
            old_phone = record.phones[int(idx) - 1].value
            record.edit_phone(old_phone, phone)
            return "Contact updated."
        except (ValueError, IndexError):
            return "Error: Invalid choice. Operation cancelled."
    return "Operation cancelled."


@input_error
def add_contact(args, book: AddressBook):  # adding contact to address book
    name, phone = args
    error = _validate_name(name)
    if error:
        return error
    record = book.find(name)
    if record is None:
        record = Record(name)
        record.add_phone(phone)
        book.add_record(record)
        return "Contact added."
    return _handle_existing_contact(record, phone)


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
def show_all(book: AddressBook):  # show all contacts
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
def find_contact(args, book: AddressBook):
    search_query = args[0].lower()
    found_records = []
    
    for record in book.data.values():
        if search_query in record.name.value.lower():
            found_records.append(str(record))
            continue
            
        for phone in record.phones:
            if search_query in phone.value:
                found_records.append(str(record))
                break
                
    if not found_records:
        return "No contacts found."
        
    return "\n".join(found_records)