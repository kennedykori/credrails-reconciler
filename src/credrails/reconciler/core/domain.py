"""Core domain interfaces.

Unless otherwise specified, all the classes defined in this module are
interfaces with no behaviors attached to them. They exist solely to
define the API of a simple reconciler tool.
"""
from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Iterable


# =============================================================================
# CORE DOMAIN INTERFACES
# =============================================================================


class Diff[T](metaclass=ABCMeta):
    """The results of a comparison between two objects.

    Each ``Diff``/Delta instance describes a difference found after a
    comparison between two objects.
    """

    __slots__ = ()

    @property
    @abstractmethod
    def expected(self) -> T:
        """The expected value."""
        ...

    @property
    @abstractmethod
    def found(self) -> Any:  # noqa: ANN401
        """The value found."""
        ...

    @property
    @abstractmethod
    def kind(self) -> str:
        """The type of this diff."""
        ...


class Differ[ST, TT, DT](metaclass=ABCMeta):
    """Comparator of items to find differences.

    Produces the :class:`diffs<Diff>` describing their differences. Differs
    are technically not required by :class:`reconcilers<Reconciler>` but they
    serve as useful components for composing and re-using comparison
    behaviors.
    """

    __slots__ = ()

    @abstractmethod
    def compare(self, source: ST, target: TT, **kwargs) -> Iterable[Diff[DT]]:
        """Compare two items and return the resulting differences.

        :param source: The source object to compare the target against.
        :param target: The target object to check for changes on.

        :return: An ``Iterable`` of the resulting differences as ``Diff``
            objects.
        """
        ...


class DiffWriter[DT](metaclass=ABCMeta):
    """Consumer of :class:`diffs<Diff>` produced by a :class:`Reconciler`.

    Use cases can include persisting diffs or displaying the diffs on a UI.
    """

    __slots__ = ()

    @abstractmethod
    def write(self, diffs: Iterable[Diff[DT]]) -> None:
        """Consume the given :class:`diffs<Diff>` objects.

        :param diffs: An ``Iterable`` of the diffs to consume.

        :return: None.
        """
        ...


class Reconciler[DT](metaclass=ABCMeta):
    """Comparator of items to find differences.

    Produces the :class:`diffs<Diff>` describing their differences. A
    ``Reconciler`` can outsource some or all of the required comparisons to
    :class:`Differ` instances or perform all the comparisons itself.
    """

    __slots__ = ()

    @abstractmethod
    def reconcile(self) -> Iterable[Diff[DT]]:
        """Return the differences two between objects/datasets.

        :return: An ``Iterable`` of the resulting differences as ``Diff``
            objects.
        """
        ...
