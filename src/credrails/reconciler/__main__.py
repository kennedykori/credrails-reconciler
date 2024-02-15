"""Application entry point."""
from __future__ import annotations

import click


def dummy_method() -> bool:
    """Do nothing method.

    This method exists solely to be invoked by the test runner. It's a
    temporary hack to allow pytest to be invoked in a realistic way. Once
    testable code is added, it will be removed.

    :return: Always return ``True``.
    """
    # TODO: Remove this!!!
    return True


@click.command(epilog="Lets do this! ;)")
@click.version_option(
    package_name="credrails-reconciler", message="%(version)s"
)
def main() -> None:  # pragma: no cover
    """Reconcile datasets.

    \f

    :return: None.
    """  # noqa: D301
    ...


if __name__ == "__main__":  # pragma: no cover
    main()
