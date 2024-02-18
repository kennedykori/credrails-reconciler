"""Common implementations of the domain interfaces."""
from __future__ import annotations

from typing import IO, TYPE_CHECKING, Any, Never, Self, override

import click
from attrs import field, frozen, validators

from credrails.reconciler.core import (
    Diff,
    DiffWriter,
    Reconciler,
    ReconcilerError,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable


@frozen
class FailingDiffWriter(DiffWriter[Any]):
    """:class:`DiffWriter` that always fails.

    Whenever the :meth:`write` method of this ``Writer`` is invoked, it raises
    an exception. This is useful mostly for testing.
    """

    _exc_factory: Callable[[str | None], Exception] = field(
        alias="exc_factory",
        default=ReconcilerError,
        repr=False,
        validator=validators.is_callable(),
    )
    _err_message: str | None = field(
        alias="err_message",
        default=None,
        repr=False,
        validator=validators.optional(validators.instance_of(str)),
    )

    @override
    def write(self, diffs: Iterable[Diff[Any]]) -> Never:
        raise self._exc_factory(self._err_message)

    @classmethod
    def of(
        cls,
        writable: IO[Any],
        exc_factory: Callable[[str | None], Exception] | None = None,
        err_message: str | None = None,
    ) -> Self:
        """Create and return an instance of this class.

        :param writable: An object that can be written to such as a file.
        :param exc_factory: The factory to use to create the raised
            exceptions.
        :param err_message: The error message to use on the resulting
            exception.

        :return: An instance of ``NoOpDiffWriter``.
        """
        return cls(
            exc_factory=exc_factory or ReconcilerError,
            err_message=err_message or "Failed as it should!!!",
        )


@frozen
class NoOpDiffWriter(DiffWriter[Any]):
    """:class:`DiffWriter` that discards all the diffs it receives.

    This can be used as a placeholder in place of where a real ``DiffWriter``
    is  expected, but one is not yet available.
    """

    @override
    def write(self, diffs: Iterable[Diff[Any]]) -> None:
        for _ in diffs:
            # Do nothing. Discard all received diffs.
            ...

    @classmethod
    def of(cls, writable: IO[Any]) -> Self:
        """Create and return an instance of this class.

        :param writable: An object that can be written to such as a file.

        :return: An instance of ``NoOpDiffWriter``.
        """
        return cls()


@frozen
class NoOpReconciler(Reconciler[Any]):
    """:class:`Reconciler` that always resolves to no :class:`diffs<Diff>`.

    The :meth:`reconcile` method of this ``Reconciler`` always returns an empty
    ``Iterable`` regardless of what source and target were provided.
    """

    @override
    def reconcile(self) -> Iterable[Diff[Any]]:
        return ()  # Return an empty iterable

    @classmethod
    def of(cls, source: Iterable[Any], target: Iterable[Any]) -> Self:
        """Create and return an instance of this class.

        :param source: The source dataset to check for differences against.
        :param target: The target dataset to check for differences.

        :return: An instance of ``NoOpReconciler``.
        """
        return cls()


@frozen
class PrettyDiffWriter(DiffWriter[Any]):
    """:class:`DiffWriter` that prints diffs in an easy-to-read format.

    It is mostly optimized for printing the terminal. There's no guarantee the
    printed text will retain the same readability when printed on other IO
    devices.
    """

    _writable: IO[Any] = field(alias="writable", repr=False)

    @override
    def write(self, diffs: Iterable[Diff[Any]]) -> None:
        for diff in diffs:
            self._print_diff(diff)

    def _print_diff(self, diff: Diff[Any]) -> None:
        click.secho(
            diff.kind, dim=True, fg="yellow", file=self._writable, italic=True
        )
        click.secho(
            f"- {diff.expected}", bg="red", file=self._writable, italic=True
        )
        click.secho(
            f"+ {diff.found}", bg="green", file=self._writable, italic=True
        )
        click.secho(
            "--------------\n",
            dim=True,
            fg="yellow",
            file=self._writable,
            italic=True,
        )

    @classmethod
    def of(cls, writable: IO[Any]) -> Self:
        """Create and return an instance of this class.

        :param writable: An object that can be written to such as a file.

        :return: An instance of ``PrettyDiffWriter``.
        """
        return cls(writable=writable)
