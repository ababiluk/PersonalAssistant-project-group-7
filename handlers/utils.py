import pickle
from models import AddressBook
import difflib
from commands import commands
from handlers.display import show_help, _print


def parse_input(user_input):
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
        return AddressBook()

def suggest_command(user_input): #guess command of user input
    matches = difflib.get_close_matches(user_input, commands, n=1, cutoff=0.5)
    
    if matches:
        return f"Invalid command. Maybe you meant '{matches}'? Type 'help' for all commands."
    else:
        return "Invalid command. Type 'help' for the command list."
    
def get_validated_command(user_command, available_commands, args, book):
    if user_command in available_commands:
        return user_command
    matches = difflib.get_close_matches(
        user_command, available_commands, n=5, cutoff=0.6
    )
    if len(matches) == 1:
        suggested_command = matches[0]
        confirm = input(f"Did you mean '{suggested_command}' (y/n)").strip().lower()
        if confirm in ["y", "yes"]:
            return suggested_command
        _print(show_help(args, book))
    elif len(matches) > 1:
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