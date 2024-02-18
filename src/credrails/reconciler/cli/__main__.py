"""Application entry point."""
from __future__ import annotations

import sys
from collections.abc import Callable, Iterable, Mapping
from typing import IO, Any

import click

from credrails.reconciler.core import DiffWriter, Reconciler

from . import constants
from ._utils import list_available_entry_point_names as lep
from ._utils import load_from_entrypoint

# =============================================================================
# TYPES
# =============================================================================


type DiffWriterFactory = Callable[[IO[Any]], DiffWriter[Any]]


type ReconcilerFactor = Callable[
    [Iterable[Any], Iterable[Any]], Reconciler[Any]
]


# =============================================================================
# HELPERS
# =============================================================================


def _select_primary_diff_writer(
    cli_option: str,
    available_diff_writers: Mapping[str, DiffWriterFactory],
) -> DiffWriterFactory | None:
    match cli_option:
        case "auto" if available_diff_writers:
            # pick the first reconciler loaded.
            return next(iter(available_diff_writers.values()))
        case "auto":
            return None
        case _:
            return available_diff_writers[cli_option]


def _select_primary_reconciler(
    cli_option: str,
    available_reconcilers: Mapping[str, ReconcilerFactor],
) -> ReconcilerFactor | None:
    match cli_option:
        case "auto" if available_reconcilers:
            # pick the first reconciler loaded.
            return next(iter(available_reconcilers.values()))
        case "auto":
            return None
        case _:
            return available_reconcilers[cli_option]


def _set_up_app(
    reconciler: str, writer: str, quiet: bool, verbosity: int
) -> None:
    try:
        from credrails.reconciler.app import Config, setup

        diff_writers: Mapping[str, DiffWriterFactory] = load_from_entrypoint(
            entrypoint_group_name=constants.DIFF_WRITERS_ENTRY_POINT_GROUP_NAME,
        )
        reconcilers: Mapping[str, ReconcilerFactor] = load_from_entrypoint(
            entrypoint_group_name=constants.RECONCILERS_ENTRY_POINT_GROUP_NAME,
        )

        primary_diff_writer: DiffWriterFactory | None
        primary_diff_writer = _select_primary_diff_writer(
            cli_option=writer,
            available_diff_writers=diff_writers,
        )
        primary_reconciler: ReconcilerFactor | None
        primary_reconciler = _select_primary_reconciler(
            cli_option=reconciler,
            available_reconcilers=reconcilers,
        )

        config: dict[str, Any] = {
            constants.APP_AVAILABLE_RECONCILERS: reconcilers,
            constants.APP_AVAILABLE_DIFF_WRITERS: diff_writers,
            constants.APP_STDOUT_TOGGLE_CONFIG_KEY: not quiet,
            constants.APP_VERBOSITY_CONFIG_KEY: verbosity,
        }
        setup(
            Config.of(
                diff_writer_factory=primary_diff_writer,
                reconciler_factory=primary_reconciler,
                config=config,
            )
        )
    except Exception as exp:  # noqa: BLE001
        _err_msg: str = (
            "Error setting up the application. The cause of the error was: "
            f"{exp!s}."
        )
        click.secho(_err_msg, fg="red", bold=True, file=sys.stderr)
        sys.exit(1)


# =============================================================================
# MAIN
# =============================================================================


@click.command(epilog="Lets do this! ;)")
@click.option(
    "-r",
    "--reconciler",
    default="auto",
    help=(
        "The reconciler to use. When 'auto' is selected (the default), then "
        "the first reconciler loaded will be used."
    ),
    show_default=True,
    type=click.Choice(
        choices=("auto", *lep(constants.RECONCILERS_ENTRY_POINT_GROUP_NAME)),
    ),
)
@click.option(
    "-w",
    "--writer",
    default="auto",
    help=(
        "The diff-writer to use. When 'auto' is selected (the default), then "
        "the first diff-writer loaded will be used."
    ),
    show_default=True,
    type=click.Choice(
        choices=("auto", *lep(constants.DIFF_WRITERS_ENTRY_POINT_GROUP_NAME)),
    ),
)
@click.option(
    "-o",
    "--output",
    "output",
    default="-",
    help=(
        "A file or file-like object where the the produced diffs should be "
        "persisted. Defaults to using '-' (stdout) when not given."
    ),
    show_default=True,
    type=click.File(mode="w"),
)
@click.option(
    "-q",
    "--quiet",
    default=False,
    help="Disable status log messages produced by the app.",
    show_default=True,
    is_flag=True,
)
@click.option(
    "-v",
    "--verbose",
    "verbosity",
    count=True,
    default=0,
    envvar="CREDRAILS_RECONCILER_VERBOSITY",
    help=(
        "Set the level of output to expect from the program on stdout. "
        "Useful for displaying error messages with stacktraces."
    ),
)
@click.version_option(
    package_name="credrails-reconciler", message="%(version)s"
)
@click.argument(
    "source",
    type=click.Path(
        allow_dash=False,
        dir_okay=False,
        exists=True,
        executable=False,
        file_okay=True,
        readable=True,
        resolve_path=True,
        writable=False,
    ),
)
@click.argument(
    "target",
    type=click.Path(
        allow_dash=False,
        dir_okay=False,
        exists=True,
        executable=False,
        file_okay=True,
        readable=True,
        resolve_path=True,
        writable=False,
    ),
)
def main(
    reconciler: str,
    writer: str,
    output: IO[Any],
    source: str,
    target: str,
    quiet: bool,
    verbosity: int,
) -> None:  # pragma: no cover
    """
    A tool that compares two items/datasets and produces a sequence of diffs
    detailing their differences.

    \f

    :return: None.
    """  # noqa: D205, D212, D301, D401
    _set_up_app(
        reconciler=reconciler, writer=writer, quiet=quiet, verbosity=verbosity
    )

    from credrails.reconciler.cli import tui, usecases

    try:
        tui.print_info("Starting ...")

        with open(source) as source_file, open(target) as target_file:
            usecases.run(source_file, target_file, output)

        tui.print_success("Done ;)")
    except Exception as exp:  # noqa: BLE001
        _err_msg: str = (
            "An error occurred while running the application. The cause of the"
            f" error was: {exp!s}."
        )
        tui.print_error(error_message=_err_msg, exception=exp)
        sys.exit(2)


if __name__ == "__main__":  # pragma: no cover
    main()
