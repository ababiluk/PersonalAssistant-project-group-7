from handlers.contact_handlers import (
    add_contact,
    change_contact,
    delete_contact,
    remove_phone,
    find_contact,
    add_email,
    edit_email,
    delete_email,
)
from handlers.birthday_handlers import (
    add_birthday,
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
    add_tag,
)
from handlers.note_display import (
    show_notes,
    show_all_notes,
    all_with_notes,
)
from handlers.note_search import (
    find_notes,
    find_by_tag,
    sort_by_tags,
)
from handlers.export_handlers import export_book

commands = {
    "hello": hello_message,
    "help": show_help,
    "add": add_contact,
    "change": change_contact,
    "phone": display_phone,
    "all": display_all,
    "delete-contact": delete_contact,
    "delete-phone": remove_phone,
    "add-birthday": add_birthday,
    "show-birthday": display_birthday,
    "birthdays": display_birthdays,
    "find": find_contact,
    "add-email": add_email,
    "edit-email": edit_email,
    "delete-email": delete_email,
    "add-note": add_note,
    "edit-note": edit_note,
    "delete-note": delete_note,
    "show-notes": show_notes,
    "show-all-notes": show_all_notes,
    "all-with-notes": all_with_notes,
    "find-notes": find_notes,
    "add-tag": add_tag,
    "find-by-tag": find_by_tag,
    "sort-by-tags": sort_by_tags,
    "export-book": export_book,
}