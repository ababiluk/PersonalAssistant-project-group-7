# Personal Assistant

A console-based personal assistant for managing an **address book** and **notes**.
It runs as an interactive command-line REPL: you type commands, the assistant
processes them, and your data is saved to disk so nothing is lost between runs.

## Features

- **Contacts** with a name, multiple phone numbers, multiple emails, a birthday, and an address.
- **Quick or guided contact creation** — `add Name [phone]` for a one-liner, or bare `add` for a step-by-step interactive flow.
- **Per-field commands** — add / edit / delete for phones, emails, birthdays and addresses.
- **Birthday reminders** — list upcoming birthdays within N days, with weekend birthdays shifted to the following Monday.
- **Notes** with text, plus **tags**: add, edit, delete, search, and group notes by tag.
- **Search** contacts (by name or phone) and notes (by text or tag).
- **Validation** of phone numbers and emails on input, with friendly error messages instead of crashes.
- **Export** the whole address book to **CSV** or **JSON**.
- **Persistence** — data is stored in `addressbook.pkl` and auto-saved on exit.
- **Convenience** — command autocompletion while typing, and a grouped help table shown at startup.

## Requirements

- **Python 3.10+**
- Dependencies (installed via `requirements.txt`):
  - [`rich`](https://pypi.org/project/rich/) — formatted tables and colored output
  - [`prompt_toolkit`](https://pypi.org/project/prompt-toolkit/) — interactive prompt with autocompletion

## Installation

Clone the repository and install the dependencies. Using a virtual environment is recommended.

### Windows (PowerShell)

```powershell
git clone https://github.com/konstantine-ivanov/PersonalAssistant-project-group-7.git
cd PersonalAssistant-project-group-7
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### macOS / Linux

```bash
git clone https://github.com/konstantine-ivanov/PersonalAssistant-project-group-7.git
cd PersonalAssistant-project-group-7
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running

From the project root, with the virtual environment activated:

```bash
# Windows
python main.py

# macOS / Linux
python3 main.py
```

> Run it in a real terminal (not through a pipe), since the interactive prompt
> needs a proper console.

## Usage

On startup the assistant prints a welcome message and the full command list,
then waits for input at the `Enter a command:` prompt.

- Start typing a command to see **autocompletion** suggestions.
- Commands are **case-insensitive**; names and values keep their case.
- If you mistype a command, the assistant **suggests the closest match** or lets you pick from a short list.
- Type `help` at any time to show the command list again.
- Type `close` or `exit` to **save and quit**.

## Commands

### General

| Command         | Description                  |
|-----------------|------------------------------|
| `hello`         | Greet the bot                |
| `help`          | Show all available commands  |
| `close` / `exit`| Save data and quit           |

### Contacts

| Command                   | Description                                                        |
|---------------------------|-------------------------------------------------------------------|
| `add [name] [phone]`      | Add by name (+optional phone), or `add` alone for full interactive entry |
| `show-contacts`           | Show all contacts                                                  |
| `show-contacts-full`      | Show all contacts with all fields, including notes                |
| `find-contact [query]`    | Search contacts by name or phone                                  |
| `delete-contact [name]`   | Delete a contact                                                   |

### Phones

| Command                       | Description                                          |
|-------------------------------|------------------------------------------------------|
| `add-phone [name] [phone]`    | Add a phone to a contact (prompts if no number)      |
| `edit-phone [name]`           | Edit a phone (auto-picks if one, choose if several)  |
| `show-phone [name]`           | Show phone number(s)                                  |
| `delete-phone [name] [phone]` | Remove phone(s) — pick one or many when several      |

### Emails

| Command                       | Description                                          |
|-------------------------------|------------------------------------------------------|
| `add-email [name] [email]`    | Add an email to a contact (prompts if none given)    |
| `edit-email [name]`           | Edit an email (choose if several)                    |
| `delete-email [name] [email]` | Remove email(s) — pick one or many when several      |

### Birthdays

| Command                          | Description                          |
|----------------------------------|--------------------------------------|
| `add-birthday [name] [DD.MM.YYYY]`| Add a birthday                      |
| `edit-birthday [name] [DD.MM.YYYY]`| Edit a birthday                    |
| `delete-birthday [name]`         | Remove a birthday                    |
| `show-birthday [name]`           | Show a birthday                      |
| `upcoming-birthdays [days]`      | Upcoming birthdays (default: 7 days) |

### Addresses

| Command                 | Description                    |
|-------------------------|--------------------------------|
| `add-address [name]`    | Add an address (guided entry)  |
| `edit-address [name]`   | Edit the address (guided entry)|
| `delete-address [name]` | Remove the address             |

### Notes

| Command                 | Description                                           |
|-------------------------|-------------------------------------------------------|
| `add-note [name] [text]`| Add a note to a contact                               |
| `edit-note [name\|id]`  | Edit a note's text (by note ID or contact; tags kept) |
| `delete-note [name\|id]`| Delete a note (by note ID or contact)                 |
| `show-notes [name]`     | Show all notes for a contact                           |
| `show-all-notes`        | Show all notes across all contacts                    |
| `find-notes [query]`    | Search notes across all contacts                      |

> Commands that take `[name|id]` accept either a note ID or a contact name; if the
> contact has several notes you'll be asked which one.

### Tags

| Command                | Description                                        |
|------------------------|----------------------------------------------------|
| `add-tag [name\|id]`   | Add one or more comma-separated tags to a note     |
| `edit-tag [name\|id]`  | Replace a note's whole tag list                    |
| `delete-tag [name\|id]`| Remove tag(s) from a note — pick one or many       |
| `find-by-tag [tag]`    | Search notes by a specific tag                     |
| `show-notes-by-tag`    | Show all notes grouped by tags                     |

### Data

| Command                      | Description                            |
|------------------------------|----------------------------------------|
| `export-book [csv\|json] [path]`| Export the address book to CSV or JSON |

## Data storage

- All contacts and notes are saved to **`addressbook.pkl`** in the project root when you `close`/`exit`. On the next launch the data is loaded automatically; if the file is missing, the assistant starts with an empty book.
- Exports created with `export-book` (without an explicit path) are written to the **`exported_files/`** directory with a timestamped filename.

## Authors

Group 7 — **Midnight Commit** — Neoversity Python Programming project.

- Konstantine Ivanov ([@konstantine-ivanov](https://github.com/konstantine-ivanov))
- Victoria Lytvyn [@ToryLit](https://github.com/ToryLit)
- Dmytro Kulibaba [@ababiluk](https://github.com/ababiluk)
