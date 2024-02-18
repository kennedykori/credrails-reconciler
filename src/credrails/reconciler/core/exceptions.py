"""Base exceptions for the project."""


class ReconcilerError(Exception):
    """Base exception for most non-builtin errors raised by this tool."""

    def __init__(self, message: str | None = None, *args):
        """Initialize a ``ReconcilerError`` with the given parameters.

        :param message: An optional error message.
        :param args: Optional args to forward to the base exception.
        """
        self._message: str | None = message
        super().__init__(self._message or "", *args)

    @property
    def message(self) -> str | None:
        """The error message associated with this exception if available.

        Return the error message passed to this exception at initialization
        or ``None`` if one was not given.

        :return: The error message passed to this exception at initialization
            or ``None`` if one wasn't given.
        """
        return self._message
