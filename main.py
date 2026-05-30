from commands.hints import create_session
from handlers.display import _print, show_help
from commands import commands
from handlers import parse_input, save_data, load_data, get_validated_command


def main():
    # Restore previously saved contacts so data survives between runs (ТЗ: must
    # persist on disk); a missing file just yields an empty book.
    book = load_data()
    _print(
        "[bold cyan]Welcome to the assistant bot![/bold cyan] "
        "Type [green]help[/green] for the command list."
    )
    # Show the command list up front so new users see what's available without
    # having to know that "help" exists.
    _print(show_help([], book))
    session = create_session()
    available_commands = list(commands.keys())
    while True:
        try:
            user_input = session.prompt("Enter a command: ").strip()
            if not user_input:
                continue

            command, *args = parse_input(user_input)
            if command in ["close", "exit"]:
                # Persist only on a clean exit so the latest changes are saved.
                save_data(book)
                print("Good bye!")
                break

            target_command = get_validated_command(command, available_commands)

            if target_command:
                handler = commands.get(target_command)
                result = handler(args, book)

                if result:
                    _print(result)

        except KeyboardInterrupt:
            # Ctrl+C aborts the current command only, keeping the app alive so an
            # accidental interrupt doesn't drop the session (use close/exit to quit).
            print("\nCommand has been interrupted. Try again.")
            continue


if __name__ == "__main__":
    main()
