"""Global application state definitions.

This module defines a global property :attr:`conf` that refers to the
application configuration in use. For all intents and purposes, this
property should be thought of and used as a constant.

The :func:`setup` function is used to change the value of the ``Config`` in
use. This is only invoked once, early on in the application start up phase.
"""

from __future__ import annotations

from typing import Final

from ._config import (
    Config,
    ConfigurationError,
    NoSuchSettingError,
    NotSetupError,
)

conf: Final[Config] = Config.of_awaiting_setup()
"""The application configurations in use."""


def setup(config: Config) -> None:
    """Prepare the application and ready it for use."""
    global conf
    conf = config  # type: ignore


__all__ = [
    "Config",
    "ConfigurationError",
    "NotSetupError",
    "NoSuchSettingError",
    "conf",
    "setup",
]
