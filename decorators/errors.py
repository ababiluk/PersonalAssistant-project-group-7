import functools


# Handle common command errors and return user-friendly messages
def input_error(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return f"Error: {e}"
        except KeyError:
            return "Error: Contact not found."
        except IndexError:
            return "Error: Enter the argument for the command."
    return inner
