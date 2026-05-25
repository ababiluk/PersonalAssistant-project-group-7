# Personal Assistant Bot

A CLI address book bot with data persistence, birthday tracking, and a rich terminal interface.

## Features

- Add, update, and delete contacts
- Store multiple phone numbers per contact
- Track birthdays and get upcoming birthday reminders (next 7 days, weekend-adjusted)
- Data saved automatically on exit via pickle serialization
- Colored output and tables via [Rich](https://github.com/Textualize/rich)

## Project Structure

```
├── main.py
├── requirements.txt
├── models/
│   ├── fields.py        # Field, Name, Phone, Birthday
│   ├── record.py        # Record
│   └── address_book.py  # AddressBook
├── handlers/
│   ├── utils.py         # parse_input, save_data, load_data
│   ├── contact_handlers.py
│   ├── birthday_handlers.py
│   └── display.py       # Rich table renderers
└── decorators/
    └── errors.py        # input_error decorator
```

## Installation

**Windows**
```bash
python -m pip install -r requirements.txt
python main.py
```

**macOS / Linux**
```bash
pip3 install -r requirements.txt
python3 main.py
```

## Commands

| Command                        | Description                          |
|-------------------------------|--------------------------------------|
| `add <name> <phone>`          | Add a new contact or update existing |
| `change <name> <old> <new>`   | Change a phone number                |
| `phone <name>`                | Show phone number(s)                 |
| `all`                         | Show all contacts                    |
| `delete <name>`               | Delete a contact                     |
| `remove-phone <name> <phone>` | Remove a specific phone number       |
| `add-birthday <name> <date>`  | Add birthday (format: DD.MM.YYYY)    |
| `show-birthday <name>`        | Show birthday                        |
| `birthdays`                   | Upcoming birthdays in next 7 days    |
| `hello`                       | Greet the bot                        |
| `help`                        | Show command list                    |
| `close` / `exit`              | Save and quit                        |
