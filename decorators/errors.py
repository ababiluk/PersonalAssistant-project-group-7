import functools

from handlers.exceptions import FinishContactInput, OperationCancelled


# Handle common command errors and return user-friendly messages
def input_error(func):
    # Wrap command handlers so expected user mistakes become a returned message
    # instead of a traceback that would crash the REPL loop. Each exception type
    # maps to the typical cause: bad value, unknown contact, missing argument.
    @functools.wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (FinishContactInput, OperationCancelled):
            # A 'cancel' typed at a mandatory prompt (name/phone/email) bubbles up
            # here when the handler doesn't absorb it itself; treat it as a clean
            # abort instead of letting it crash the REPL loop.
            return "Operation cancelled."
        except ValueError as e:
            return f"Error: {e}"
        except KeyError:
            return "Error: Contact not found."
        except IndexError:
            return "Error: Enter the argument for the command."
    return inner
