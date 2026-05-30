import pickle
from models import AddressBook
import difflib
from handlers.display import command_suggestions_table, _print


def parse_input(user_input):
    # Lower-case the command so input is case-insensitive, but leave args as-is
    # (names/values may be case-sensitive).
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        # First run (or moved/cleared data): start with an empty book rather
        # than crashing, so the app is usable out of the box.
        return AddressBook()


def get_validated_command(user_command, available_commands):
    # Resolve a typed command to a real one. On a typo we don't auto-run a guess
    # (it would execute with the args meant for the mistyped command); instead we
    # show the close matches as a help-style table so the user retypes correctly.
    # Returns a valid command name to run, or None when there was no exact match.
    if user_command in available_commands:
        return user_command

    matches = difflib.get_close_matches(
        user_command, available_commands, n=5, cutoff=0.6
    )
    if matches:
        _print(command_suggestions_table(matches))
    else:
        _print(
            "[yellow]Invalid command.[/yellow] "
            "Type [green]help[/green] for the command list."
        )
    return None
