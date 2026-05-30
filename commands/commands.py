from handlers.contact_handlers import (
    add_contact,
    delete_contact,
    find_contact,
)
from handlers.phone_handlers import (
    change_contact,
    add_phone,
    remove_phone,
)
from handlers.email_handlers import (
    add_email,
    edit_email,
    delete_email,
)
from handlers.address_handlers import (
    add_address,
    edit_address,
    delete_address,
)
from handlers.birthday_handlers import (
    add_birthday,
    edit_birthday,
    delete_birthday,
)
from handlers.display import (
    display_all,
    display_phone,
    display_birthday,
    display_birthdays,
    show_help,
    hello_message,
)
from handlers.note_handlers import (
    add_note,
    edit_note,
    delete_note,
    show_notes,
    show_all_notes,
    find_notes,
    all_with_notes,
    add_tag,
    find_by_tag,
    sort_by_tags,
)
from handlers.export_handlers import export_book

commands = {
    "hello": hello_message,
    "help": show_help,
    "add": add_contact,
    "edit-phone": change_contact,
    "show-phone": display_phone,
    "show-contacts": display_all,
    "delete-contact": delete_contact,
    "add-phone": add_phone,
    "delete-phone": remove_phone,
    "add-birthday": add_birthday,
    "edit-birthday": edit_birthday,
    "delete-birthday": delete_birthday,
    "show-birthday": display_birthday,
    "upcoming-birthdays": display_birthdays,
    "find-contact": find_contact,
    "add-email": add_email,
    "edit-email": edit_email,
    "delete-email": delete_email,
    "add-address": add_address,
    "edit-address": edit_address,
    "delete-address": delete_address,
    "add-note": add_note,
    "edit-note": edit_note,
    "delete-note": delete_note,
    "show-notes": show_notes,
    "show-all-notes": show_all_notes,
    "show-contacts-full": all_with_notes,
    "find-notes": find_notes,
    "add-tag": add_tag,
    "find-by-tag": find_by_tag,
    "show-notes-by-tag": sort_by_tags,
    "export-book": export_book,
}