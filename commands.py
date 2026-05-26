from handlers.contact_handlers import (
    add_contact,
    change_contact,
    delete_contact,
    remove_phone,
    # find_contact
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
    "birthdays": display_birthdays
    # "find": find_contact,
}