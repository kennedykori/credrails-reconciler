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
    """Run a ``Reconciler`` and write it's output to the given ``writable``.

    Uses the
    :attr:`~credrails.reconciler.app._config.Config.reconciler_factory` and
    :attr:`~credrails.reconciler.app._config.Config.diff_writer_factory`
    properties of the active :attr:`config<credrails.reconciler.app.conf>` to
    create a :class:`~credrails.reconciler.core.domain.Reconciler` and
    :class:`~credrails.reconciler.core.domain.DiffWriter` respectively. The
    created `Reconciler` is then used t

    :param source:
    :param target:
    :param writable:
    :return:

    .. _reconciler: credrails.reconciler.core.Reconciler
    """
    from credrails.reconciler import app

    reconciler: Reconciler[Any] = app.conf.reconciler_factory(source, target)
    writer: DiffWriter[Any] = app.conf.diff_writer_factory(writable)

    writer.write(reconciler.reconcile())
