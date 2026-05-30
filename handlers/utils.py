import pickle
from models import AddressBook
import difflib
from handlers.display import show_help, _print


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


def get_validated_command(user_command, available_commands, args, book):
    # Resolve a typed command to a real one, helping past typos.
    # Accepts the raw command, the list of known commands, and the current
    # args/book (needed to render help). Returns a valid command name to run, or
    # None when nothing was chosen. Uses fuzzy matching so a near-miss can be
    # confirmed or picked from a short list instead of just failing.
    if user_command in available_commands:
        return user_command
    matches = difflib.get_close_matches(
        user_command, available_commands, n=5, cutoff=0.6
    )
    if len(matches) == 1:
        # A single close match: offer it as a yes/no so an obvious typo is one keypress to fix.
        suggested_command = matches[0]
        confirm = input(f"Did you mean '{suggested_command}' (y/n)").strip().lower()
        if confirm in ["y", "yes"]:
            return suggested_command
        _print(show_help(args, book))
    elif len(matches) > 1:
        # Several candidates: let the user pick by number (or by name) to disambiguate.
        _print("\nPossible commands:")

        for i, match in enumerate(matches, 1):
            _print(f"{i}. {match}")

        choice = input("Choose command number (or type 'exit' to cancel): ").strip().lower()
        if choice in ["exit", "close", "cancel"]:
            return None

        if choice in matches:
            return choice

        try:
            return matches[int(choice) - 1]
        except (ValueError, IndexError):
            _print("[red]Invalid selection. Please enter a number from the list.[/red]")
    else:
        _print(
            "[yellow]Invalid command.[/yellow] "
            "Type [green]help[/green] for the command list."
        )
    return None