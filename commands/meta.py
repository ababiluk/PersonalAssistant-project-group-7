# Display order of help sections; show_help renders groups in this sequence.
GROUP_ORDER = [
    "General",
    "Contacts",
    "Phones",
    "Emails",
    "Birthdays",
    "Addresses",
    "Notes",
    "Tags",
    "Data",
]

COMMAND_META: dict[str, tuple[str, str, str]] = {
    #  command           args hint              description                                          group
    "hello":          ("",                    "Greet the bot",                                      "General"),
    "help":           ("",                    "Show all available commands",                        "General"),
    "close":          ("",                    "Quit the bot",                                       "General"),
    "exit":           ("",                    "Quit the bot",                                       "General"),

    "add":            ("[name] [phone]",       "Add by name (+optional phone), or 'add' alone for full interactive entry", "Contacts"),
    "show-contacts":  ("",                    "Show all contacts",                                  "Contacts"),
    "find-contact":   ("[query]",              "Search contacts by name or phone",                   "Contacts"),
    "delete-contact": ("[name]",               "Delete a contact",                                   "Contacts"),

    "add-phone":      ("[name] [phone]",       "Add a phone to a contact (prompts if no number)",    "Phones"),
    "edit-phone":     ("[name] [old] [new]",   "Change phone number",                                "Phones"),
    "show-phone":     ("[name]",               "Show phone number(s)",                               "Phones"),
    "delete-phone":   ("[name] [phone]",       "Remove a phone (prompts/auto-picks if no number)",   "Phones"),

    "add-email":      ("[name] [email]",       "Add an email to a contact (prompts if none)",        "Emails"),
    "edit-email":     ("[name]",               "Edit an email (choose if several)",                  "Emails"),
    "delete-email":   ("[name] [email]",       "Remove an email (prompts/auto-picks if none)",       "Emails"),

    "add-birthday":   ("[name] [DD.MM.YYYY]",  "Add birthday",                                       "Birthdays"),
    "edit-birthday":  ("[name] [DD.MM.YYYY]",  "Edit birthday",                                      "Birthdays"),
    "delete-birthday":("[name]",               "Remove birthday",                                    "Birthdays"),
    "show-birthday":  ("[name]",               "Show birthday",                                      "Birthdays"),
    "upcoming-birthdays":("[days]",            "Upcoming birthdays (default: 7 days)",               "Birthdays"),

    "add-address":    ("[name]",               "Add an address (guided entry)",                      "Addresses"),
    "edit-address":   ("[name]",               "Edit the address (guided entry)",                    "Addresses"),
    "delete-address": ("[name]",               "Remove the address",                                 "Addresses"),

    "add-note":       ("[name] [text]",        "Add a note to a contact",                            "Notes"),
    "edit-note":      ("[name]",               "Edit a note by ID",                                  "Notes"),
    "delete-note":    ("[name]",               "Delete a note by ID",                                "Notes"),
    "show-notes":     ("[name]",               "Show all notes for a contact",                       "Notes"),
    "show-all-notes": ("",                    "Show all notes across all contacts",                 "Notes"),
    "show-contacts-full": ("",                "Show all contacts with all fields including notes",  "Notes"),
    "find-notes":     ("[query]",              "Search notes across all contacts",                   "Notes"),

    "add-tag":        ("[name]",               "Add a tag to a contact's note",                      "Tags"),
    "find-by-tag":    ("[tag]",                "Search notes by a specific tag",                     "Tags"),
    "show-notes-by-tag":("",                   "Show all notes grouped by tags",                     "Tags"),

    "export-book":    ("[csv|json] [path]",   "Export address book to CSV or JSON file",            "Data"),
}
