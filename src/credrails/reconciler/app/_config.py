"""``Config`` interface definition, implementing classes and helpers."""
from __future__ import annotations

from abc import ABCMeta, abstractmethod
from collections.abc import Callable, Iterable, Mapping
from typing import IO, Any, Never, override

from attrs import field, frozen, validators

from credrails.reconciler.core import DiffWriter, Reconciler, ReconcilerError
from credrails.reconciler.lib import NoOpDiffWriter, NoOpReconciler

# =============================================================================
# TYPES
# =============================================================================


type DiffWriterFactory = Callable[[IO[Any]], DiffWriter[Any]]


type ReconcilerFactor = Callable[
    [Iterable[Any], Iterable[Any]], Reconciler[Any]
]


# =============================================================================
# EXCEPTIONS
# =============================================================================


class ConfigurationError(ReconcilerError):
    """Indicates a generic configuration error occurred."""


class NotSetupError(ConfigurationError):
    """Indicates that the application is yet to be set up."""

    def __init__(self, message: str | None = None) -> None:
        _message: str = message or (
            "Application not set up. Please call the "
            "'credrails.reconciler.app.setup()' function before proceeding."
        )
        super().__init__(message=_message)


class NoSuchSettingError(ConfigurationError, LookupError):
    """Non-existent setting access error."""

    def __init__(self, setting: str, message: str | None = None) -> None:
        """Initialize a ``NoSuchSettingError`` with the given properties.

        :param setting: The missing setting. This MUST not be ``None`` or
            empty.
        :param message: An optional message for the resulting exception. If
            none is provided, then a generic one is automatically generated.

        :raise ValueError: If the specified setting name is ``None`` or empty.
        """
        _message: str = message or f"Setting '{setting}' does not exist."
        ConfigurationError.__init__(self, message=_message)
        self._setting: str = setting

    @property
    def setting(self) -> str:
        """The missing setting.

        This is the missing setting whose attempted access resulted in this
        exception being raised.
        """
        return self._setting


# =============================================================================
# CONFIG INTERFACE
# =============================================================================


class Config(metaclass=ABCMeta):
    """An object that holds application settings.

    Only read-only access to the settings is available post initialization.
    The configured settings/options can be accessed using the ``get`` methods.
    There are two such methods, :meth:`get` and :meth:`get_or_default`.

    The factory methods for the :class:`DiffWriter` and :class:`Reconciler` in
    use can also be accessed using the :attr:`diff_writer_factory` and
    :attr:`reconciler_factory` properties respectively.
    """

    __slots__ = ()

    @property
    @abstractmethod
    def diff_writer_factory(self) -> DiffWriterFactory:
        """Factory to initialize the :class:`DiffWriter` in use."""
        ...

    @property
    @abstractmethod
    def reconciler_factory(self) -> ReconcilerFactor:
        """Factory to initialize the :class:`Reconciler` in use."""
        ...

    @abstractmethod
    def get[T](self, setting: str) -> T:  # pyright: ignore
        """Retrieve the configuration value of the given setting.

        :param setting: The name of the setting value to retrieve.

        :return: The value of the given setting.

        :raise NoSuchSettingError: if the given setting has no associated value
            in this ``Config`` object.
        """
        ...

    @abstractmethod
    def get_or_default[T](self, setting: str, default: T) -> T:
        """Retrieve the config value of the given setting or return default.

        :param setting: The name of the setting value to retrieve.
        :param default: A value to return when no setting with the given name
            exists in this ``Config``.

        :return: The value of the given setting when available or the given
            default otherwise.
        """
        ...

    @staticmethod
    def of(
        diff_writer_factory: DiffWriterFactory | None = None,
        reconciler_factory: ReconcilerFactor | None = None,
        config: Mapping[str, Any] | None = None,
    ) -> Config:
        """Create and return a ``Config`` instance with the given properties.

        :param diff_writer_factory: The ``DiffWriter`` factory that the created
            ``Config`` instance should have. When not given or when ``None``,
            a default will be used. The default is just a placeholder that
            discards all diffs given to it.
        :param reconciler_factory: The ``Reconciler`` factory that the created
            ``Config`` instance should have. When not provided or when
            ``None``, a default will be used. The default is a just a
            placeholder that always resolves to no diffs.
        :param config: A mapping of extra config values that can be accessed
            using the returned ``Config`` instances' ``get_*`` methods.

        :return: An instance of ``Config`` with the given properties.
        """
        return _ConfigImp(
            diff_writer_factory=diff_writer_factory or NoOpDiffWriter.of,
            reconciler_factory=reconciler_factory or NoOpReconciler.of,
            config=dict(config) if config else {},
        )

    @staticmethod
    def of_awaiting_setup(err_msg: str | None = None) -> Config:
        """Create a ``Config`` instance to indicate the app is not uet set up.

        The returned ``Config`` instances raises the :exc:`NotSetupError` in
        each attempted usage. The purpose of these instances is to indicate to
        the clients/users that the application has not yet been set up, and
        they should invoke :func:`credrails.reconciler.app.setup` first before
        proceeding. This ensures that all modules are properly initialized and
        are ready for use before normal operations of the application can
        proceed.

        :param err_msg: An optional error message to use on the raised
            ``NotSetupError`` exceptions. If ``None`` is provided, then a
            default message is used.

        :return: An instance of ``Config`` with the characteristics described
            above.
        """
        return _NotSetup(err_msg)


# =============================================================================
# CONFIG IMPLEMENTATIONS
# =============================================================================


@frozen
class _NotSetup(Config):
    _err_msg: str | None = field(
        alias="err_msg",
        default=None,
        repr=False,
        validator=validators.optional(validators.instance_of(str)),
    )

    @property
    def diff_writer_factory(self) -> DiffWriterFactory:
        return self._raise(self._err_msg)

    @property
    def reconciler_factory(self) -> ReconcilerFactor:
        return self._raise(self._err_msg)

    @override
    def get[T](self, setting: str) -> T:  # pyright: ignore
        return self._raise(self._err_msg)

    @override
    def get_or_default[T](self, setting: str, default: T) -> T:
        return self._raise(self._err_msg)

    @staticmethod
    def _raise(err_msg: str | None) -> Never:
        raise NotSetupError(message=err_msg)


@frozen
class _ConfigImp(Config):
    _diff_writer_factory: DiffWriterFactory = field(
        alias="diff_writer_factory",
        repr=False,
        validator=validators.is_callable(),
    )
    _reconciler_factory: ReconcilerFactor = field(
        alias="reconciler_factory",
        repr=False,
        validator=validators.is_callable(),
    )
    _config: Mapping[str, Any] = field(
        alias="config",
        factory=dict,
        repr=False,
    )

    @property
    @override
    def diff_writer_factory(self) -> DiffWriterFactory:
        return self._diff_writer_factory

    @property
    @override
    def reconciler_factory(self) -> ReconcilerFactor:
        return self._reconciler_factory

    @override
    def get[T](self, setting: str) -> T:  # pyright: ignore
        if setting not in self._config:
            raise NoSuchSettingError(setting=setting)
        return self._config[setting]

    @override
    def get_or_default[T](self, setting: str, default: T) -> T:
        return self._config.get(setting, default)
