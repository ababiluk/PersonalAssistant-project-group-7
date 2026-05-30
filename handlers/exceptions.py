class OperationCancelled(Exception):
    """User cancelled interactive operation."""
    pass


class FinishContactInput(Exception):
    """Stop optional contact input and save entered data."""
    pass
