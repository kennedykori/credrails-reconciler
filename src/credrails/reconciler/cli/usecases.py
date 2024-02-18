"""Application Use cases."""

from __future__ import annotations

from typing import IO, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Iterable

    from credrails.reconciler.core import DiffWriter, Reconciler


def run(
    source: Iterable[Any],
    target: Iterable[Any],
    writable: IO[Any],
) -> None:
    """Run a :class:`Reconciler` and consume its output.

    :param source:
    :param target:
    :param writable:
    :return:
    """
    from credrails.reconciler import app

    reconciler: Reconciler[Any] = app.conf.reconciler_factory(source, target)
    writer: DiffWriter[Any] = app.conf.diff_writer_factory(writable)

    writer.write(reconciler.reconcile())
