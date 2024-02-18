# ruff: noqa: D100, D102
from __future__ import annotations

from unittest import TestCase

import pytest

from credrails.reconciler.lib.common import FailingDiffWriter, NoOpReconciler


class TestFailingDiffWriter(TestCase):
    """Tests for the :class:`FailingDiffWriter` class."""

    def setUp(self) -> None:
        super().setUp()
        self._instance: FailingDiffWriter = FailingDiffWriter(RuntimeError)

    def test_write(self) -> None:
        with pytest.raises(RuntimeError):
            self._instance.write(())


class TestNoOpReconciler(TestCase):
    """Tests for the :class:`NoOpReconciler` class."""

    def setUp(self) -> None:
        super().setUp()
        self._instance: NoOpReconciler = NoOpReconciler()

    def test_reconciler(self) -> None:
        diffs = self._instance.reconcile()

        assert diffs is not None
        assert len(list(diffs)) == 0
