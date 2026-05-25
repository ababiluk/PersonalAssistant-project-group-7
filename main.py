from rich.console import Console
from rich.table import Table

from handlers import (
    parse_input, save_data, load_data,
    add_contact, change_contact, delete_contact, remove_phone,
    add_birthday,
    display_all, display_phone, display_birthday, display_birthdays,
)

console = Console()


def show_help():
    table = Table(title="Available commands", show_header=True, header_style="bold cyan")
    table.add_column("Command", style="green")
    table.add_column("Description")

    table.add_row("hello", "Greet the bot")
    table.add_row("add [name] [phone]", "Add or update a contact")
    table.add_row("change [name] [old] [new]", "Change phone number")
    table.add_row("phone [name]", "Show phone number(s)")
    table.add_row("all", "Show all contacts")
    table.add_row("delete [name]", "Delete a contact")
    table.add_row("remove-phone [name] [phone]", "Remove a specific phone")
    table.add_row("add-birthday [name] [DD.MM.YYYY]", "Add birthday")
    table.add_row("show-birthday [name]", "Show birthday")
    table.add_row("birthdays", "Upcoming birthdays (next 7 days)")
    table.add_row("help", "Show this message")
    table.add_row("close / exit", "Quit the bot")

    console.print(table)


def _print(result):
    if isinstance(result, str) and result.startswith("Error"):
        console.print(f"[bold red]{result}[/bold red]")
    else:
        console.print(result)


def main():
    book = load_data()  # getting data from file on load
    console.print("[bold cyan]Welcome to the assistant bot![/bold cyan] Type [green]help[/green] for the command list.")

    while True:
        user_input = input("Enter a command: ").strip()
        if not user_input:
            continue

        command, *args = parse_input(user_input)

        match command:
            case "close" | "exit":
                save_data(book)  # saving data to file on exit
                console.print("[bold]Good bye![/bold]")
                break
            case "help":
                show_help()
            case "hello":
                console.print("How can I help you?")
            case "add":
                _print(add_contact(args, book))
            case "change":
                _print(change_contact(args, book))
            case "phone":
                _print(display_phone(args, book))
            case "all":
                _print(display_all(book))
            case "delete":
                _print(delete_contact(args, book))
            case "remove-phone":
                _print(remove_phone(args, book))
            case "add-birthday":
                _print(add_birthday(args, book))
            case "show-birthday":
                _print(display_birthday(args, book))
            case "birthdays":
                _print(display_birthdays(book))
            case _:
                console.print("[yellow]Invalid command.[/yellow] Type [green]help[/green] for the command list.")


if __name__ == "__main__":
    main()
