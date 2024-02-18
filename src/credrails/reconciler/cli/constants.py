"""CLI Constants."""

from __future__ import annotations

from typing import Final

APP_AVAILABLE_DIFF_WRITERS: Final[str] = "credrails.reconciler.cli.writers"

APP_AVAILABLE_RECONCILERS: Final[str] = "credrails.reconciler.cli.reconcilers"

APP_STDOUT_TOGGLE_CONFIG_KEY: Final[
    str
] = "credrails.reconciler.cli.stdout.toggle"

APP_VERBOSITY_CONFIG_KEY: Final[str] = "credrails.reconciler.cli.verbosity"

DIFF_WRITERS_ENTRY_POINT_GROUP_NAME: Final[
    str
] = "credrails.reconciler.cli.diff_writer"

RECONCILERS_ENTRY_POINT_GROUP_NAME: Final[
    str
] = "credrails.reconciler.cli.reconciler"
