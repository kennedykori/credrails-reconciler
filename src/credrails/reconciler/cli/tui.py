# ruff: noqa: D100, D103
from __future__ import annotations

import sys
import traceback

import click

from credrails.reconciler import app
from credrails.reconciler.cli import constants


def print_debug(message: str, nl: bool = True) -> None:
    if not app.conf.get_or_default(
        setting=constants.APP_STDOUT_TOGGLE_CONFIG_KEY,
        default=True,
    ):
        return
    click.secho(message, dim=True, fg="yellow", italic=True, nl=nl)


def print_info(message: str) -> None:
    if not app.conf.get_or_default(
        setting=constants.APP_STDOUT_TOGGLE_CONFIG_KEY,
        default=True,
    ):
        return
    click.echo(click.style(message, fg="bright_blue"))


def print_error(error_message: str, exception: BaseException | None) -> None:
    verbosity: int = app.conf.get_or_default(
        setting=constants.APP_VERBOSITY_CONFIG_KEY,
        default=0,
    )
    click.secho(error_message, fg="red", bold=True, file=sys.stderr)
    match verbosity:
        case 1 if exception is not None:
            click.secho(
                "".join(traceback.format_exception(exception, chain=False)),
                fg="magenta",
                file=sys.stderr,
            )
        case _ if verbosity > 1 and exception is not None:
            click.secho(
                "".join(traceback.format_exception(exception, chain=True)),
                fg="magenta",
                file=sys.stderr,
            )


def print_success(message: str) -> None:
    if not app.conf.get_or_default(
        setting=constants.APP_STDOUT_TOGGLE_CONFIG_KEY,
        default=True,
    ):
        return
    click.echo(click.style(message, fg="green"))
