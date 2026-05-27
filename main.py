from handlers.display import (
    show_help,
    _print
)
from commands import commands
from handlers import (
    parse_input,
    save_data, 
    load_data
)

def main():
    book = load_data()  # getting data from file on load
    _print("[bold cyan]Welcome to the assistant bot![/bold cyan] Type [green]help[/green] for the command list.")

    while True:
        try:
            user_input = input("Enter a command: ").strip()
            if not user_input:
                continue

            command, *args = parse_input(user_input)
            if command in ["close", "exit"]:
                    save_data(book)
                    print("Good bye!")
                    break
            handler = commands.get(command)
                
            if handler:
                result = handler(args, book)

                if result:
                    _print(result)
            else:
                _print(
                    "[yellow]Invalid command.[/yellow] "
                    "Type [green]help[/green] for the command list."
                )
        except KeyboardInterrupt:
            print("\nCommand has been interrupted. Try again.")
            continue 
        
if __name__ == "__main__":
    main()
