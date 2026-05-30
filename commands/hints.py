from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.styles import Style
from commands.meta import COMMAND_META

_STYLE = Style.from_dict({
    "completion-menu":                    "bg:#1e1e2e",
    "completion-menu.completion":         "bg:#1e1e2e fg:#cdd6f4",
    "completion-menu.completion.current": "bg:#313244 fg:#ffffff bold",
    "completion-menu.meta":               "bg:#1e1e2e fg:#6c7086",
    "completion-menu.meta.current":       "bg:#313244 fg:#89b4fa bold",
    "completion-menu.progress-bar":       "bg:#45475a",
    "completion-menu.progress-button":    "bg:#89b4fa",
})


# Autocomplete commands using metadata descriptions
class CommandCompleter(Completer):
    # Generate completion suggestions while user types
    def get_completions(self, document, _complete_event):
        text = document.text_before_cursor.lstrip().lower()
        # Only complete the command word itself; once the user types a space they
        # are entering arguments, which we can't meaningfully suggest.
        if " " in text:
            return
        for cmd, (args, desc, _group) in COMMAND_META.items():
            if cmd.startswith(text):
                display_meta = f"{args} — {desc}" if args else desc
                yield Completion(
                    cmd,
                    start_position=-len(text),
                    display_meta=display_meta,
                )


# Create interactive prompt session with history and autocomplete
def create_session() -> PromptSession:
    return PromptSession(
        history=InMemoryHistory(),
        completer=CommandCompleter(),
        complete_while_typing=True,
        style=_STYLE,
    )
