# ruff: noqa: D101, D102, D103, D105
"""A ``Reconciler`` implementation for working with CSV files."""
from __future__ import annotations

import csv
from abc import ABCMeta, abstractmethod
from collections.abc import Callable, Iterable, Mapping
from enum import StrEnum
from itertools import zip_longest
from typing import TYPE_CHECKING, Any, Self, override

import attrs
from attrs import field, frozen, validators

from credrails.reconciler.core import (
    Diff,
    Differ,
    DiffWriter,
    Reconciler,
    ReconcilerError,
)

if TYPE_CHECKING:
    from _typeshed import SupportsWrite

# =============================================================================
# TYPES
# =============================================================================


type CSVRecord = Mapping[str, Any]

type CSVRecordDifferFactory = Callable[[], CSVRecordDiffer]


# =============================================================================
# EXCEPTIONS
# =============================================================================


class RecordIDMissingError(ReconcilerError):
    """Record ID was not provided.

    Implementors of :class:`CSVRecordDiffer` can raise this exception to
    indicate that the `record_id` keyword argument wasn't provided to the
    :meth:`CSVRecordDiffer.compare` method.
    """


class UnsupportedDiffTypeError(ReconcilerError):
    """Indicates that a provided :class:`Diff` instance is not supported.

    This is raised by the :class:`CSVDiffWriter` to indicate that the given
    `Diff` instance(s) are not of type :class:`CSVDiff`.
    """


# =============================================================================
# HELPERS
# =============================================================================


class CSVDiffKinds(StrEnum):
    """Common CSV Diff types."""

    EXTRA_TGT_FIELD = "Extra Target Column"
    """
    Used to denote a :class:`Diff` where the target record has an extra column.
    """

    FIELD_MISMATCH = "Field Discrepancy"
    """
    Used to denote a :class:`Diff` where there is a discrepancy between the
    source and target record on one of the available fields.
    """

    NOT_IN_SOURCE = "Missing in Source"
    """
    Used to denote a :class:`Diff` where there exists a record that is on the
    target dataset but missing on the source dataset.
    """

    NOT_IN_TARGET = "Missing in Target"
    """
    Used to denote a :class:`Diff` where there exists a record that is on the
    source dataset but missing on the target dataset.
    """


# =============================================================================
# CONCRETE IMPLEMENTATIONS
# =============================================================================


@frozen
class CSVDiff(Diff[str]):
    """:class:`Diff` produced when reconciling CSV datasets/records."""

    _kind: CSVDiffKinds = field(alias="kind")
    _record_id: str = field(
        alias="record_id",
        validator=validators.instance_of(str),
    )
    _field: str | None = field(
        alias="field",
        default=None,
        validator=validators.optional(validators.instance_of(str)),
    )
    _source_value: str | None = field(
        alias="source_value",
        default=None,
        validator=validators.optional(validators.instance_of(str)),
    )
    _target_value: str | None = field(
        alias="target_value",
        default=None,
        validator=validators.optional(validators.instance_of(str)),
    )

    @property
    @override
    def expected(self) -> str:
        """A summary of the expected value."""
        match self._kind:
            case CSVDiffKinds.NOT_IN_TARGET:
                return f"Record: {self._record_id}"
            case CSVDiffKinds.FIELD_MISMATCH:
                return f"Value: {self._source_value}"
            case _:
                return ""

    @property
    def field(self) -> str | None:
        """The field or column in focus."""
        return self._field

    @property
    @override
    def found(self) -> Any:
        """A summary of what the actual value in the target was."""
        match self._kind:
            case CSVDiffKinds.EXTRA_TGT_FIELD:
                return f"Column: {self.field}"
            case CSVDiffKinds.FIELD_MISMATCH:
                return f"Value: {self._target_value}"
            case CSVDiffKinds.NOT_IN_SOURCE:
                return f"Record: {self._record_id}"
            case _:
                return ""

    @property
    @override
    def kind(self) -> CSVDiffKinds:
        """The type of this diff."""
        return self._kind

    @property
    def record_id(self) -> str:
        """The identifier of the record in focus."""
        return self._record_id

    @property
    def source_value(self) -> str | None:
        """The value on the source record when available."""
        return self._source_value

    @property
    def target_value(self) -> str | None:
        """The value on the target record when available."""
        return self._target_value

    @classmethod
    def of_extra_target_field(
        cls,
        record_id: str,
        field: str,
    ) -> Self:
        """Create a ``CSVDiff`` of kind :attr:`~CSVDiffKinds.EXTRA_TGT_FIELD`.

        Create and return a ``CSVDiff`` of kind
        :attr:`~CSVDiffKinds.EXTRA_TGT_FIELD` for the given field and the
        record with the given identifier.

        :param record_id: The identifier of the target record with an extra
            field.
        :param field: The name of the extra field on the target record that is
            missing on the source record.

        :return: An instance of ``CSVDiff`` with the given properties.
        """
        return cls(
            kind=CSVDiffKinds.EXTRA_TGT_FIELD,
            record_id=record_id,
            field=field,
        )

    @classmethod
    def of_field_mismatch(
        cls,
        record_id: str,
        field: str,
        source_value: str,
        target_value: str,
    ) -> Self:
        """Create a ``CSVDiff`` of kind :attr:`~CSVDiffKinds.FIELD_MISMATCH`.

        Create and return a ``CSVDiff`` of kind
        :attr:`~CSVDiffKinds.FIELD_MISMATCH` for the given field, record with
        the specified identifier and source and target values.

        :param record_id: The shared identifier of the records (both source and
            target) where there is a field discrepancy.
        :param field: The name of the field with the discrepancy.
        :param source_value: The value on the source record.
        :param target_value: The value on the target record.

        :return: An instance of ``CSVDiff`` with the given properties.
        """
        return cls(
            kind=CSVDiffKinds.FIELD_MISMATCH,
            record_id=record_id,
            field=field,
            source_value=source_value,
            target_value=target_value,
        )

    @classmethod
    def of_not_in_source(cls, record_id: str) -> Self:
        """Create a ``CSVDiff`` of kind :attr:`~CSVDiffKinds.NOT_IN_SOURCE`.

        Create and return a ``CSVDiff`` of kind
        :attr:`~CSVDiffKinds.NOT_IN_SOURCE` for the target record with the
        given identifier.

        :param record_id: The identifier of the record on the target dataset
            that is missing on the source record.

        :return: An instance of ``CSVDiff`` with the given properties.
        """
        return cls(kind=CSVDiffKinds.NOT_IN_SOURCE, record_id=record_id)

    @classmethod
    def of_not_in_target(cls, record_id: str) -> Self:
        """Create a ``CSVDiff`` of kind :attr:`~CSVDiffKinds.NOT_IN_TARGET`.

        Create and return a ``CSVDiff`` of kind
        :attr:`~CSVDiffKinds.NOT_IN_TARGET` for the source record with the
        given identifier.

        :param record_id: The identifier of the record on the source dataset
            that is missing on the target record.

        :return: An instance of ``CSVDiff`` with the given properties.
        """
        return cls(kind=CSVDiffKinds.NOT_IN_TARGET, record_id=record_id)


@frozen
class CSVDiffWriter(DiffWriter[str]):
    """:class:`Writer` that consumes :class:`CSV Diffs<CSVDiff>`.

    The consumed diffs are persisted on a CSV file.
    """

    _writable: SupportsWrite = field(alias="writable", repr=False)
    _csv_writer: csv.DictWriter = field(init=False, repr=False)

    def __attrs_post_init__(self) -> None:
        csv_writer = csv.DictWriter(
            f=self._writable,
            fieldnames=tuple(
                attribute.name for attribute in attrs.fields(CSVDiff)
            ),
        )
        object.__setattr__(self, "_csv_writer", csv_writer)
        self._csv_writer.writeheader()

    @override
    def write(self, diffs: Iterable[Diff[str]]) -> None:
        for diff in diffs:
            if not isinstance(diff, CSVDiff):
                _err_msg: str = (
                    "Only Diff instances of type"
                    "'credrails.reconciler.lib.csv_reconciler:CSVDiff' are "
                    "allowed by this method."
                )
                raise UnsupportedDiffTypeError(_err_msg)
            self._csv_writer.writerow(attrs.asdict(diff))


class CSVRecordDiffer(Differ[CSVRecord, CSVRecord, str], metaclass=ABCMeta):
    """Base :class:`Differ` for all differs operating on CSV records.

    All ``Differ`` implementations for comparing CSV records are derived from
    this one.
    """

    @abstractmethod
    def compare(
        self,
        source: CSVRecord,
        target: CSVRecord,
        *,
        record_id: str | None = None,
        **kwargs,
    ) -> Iterable[CSVDiff]:
        ...


@frozen
class SimpleCSVRecordDiffer(CSVRecordDiffer):
    """Basic :class:`Differ` for comparing CSV records.

    This compares two CSV records for field discrepancies using the equals
    operator. It does not support complex field value sanitizations and only
    performs the following:

    - Extra leading and trailing space removal on strings.
    - Checking for case sensitivity issues on strings. All string values are
      converted to lower case before being checked for any differences.

    This ``Differ`` does also support checking for extra columns on the target
    record.
    """

    @override
    def compare(
        self,
        source: CSVRecord,
        target: CSVRecord,
        *,
        record_id: str | None = None,
        **kwargs,
    ) -> Iterable[CSVDiff]:
        if record_id is None:
            _err_msg: str = "'record_id' MUST be given."
            raise RecordIDMissingError(message=_err_msg)

        yield from self._check_for_field_mismatch(source, target, record_id)
        yield from self._check_for_extra_tgt_fields(source, target, record_id)

    @staticmethod
    def _check_for_extra_tgt_fields(
        source_fields: Iterable[str],
        target_fields: Iterable[str],
        record_id: str,
    ) -> Iterable[CSVDiff]:
        extra_fields = set(target_fields).difference(set(source_fields))
        for extra_field in extra_fields:
            yield CSVDiff.of_extra_target_field(
                record_id=record_id,
                field=extra_field,
            )

        return ()

    @staticmethod
    def _check_for_field_mismatch(
        source: CSVRecord,
        target: CSVRecord,
        record_id: str,
    ) -> Iterable[CSVDiff]:
        self = SimpleCSVRecordDiffer
        for column in source:
            src_val: Any = source[column]
            tgt_val: Any = target.get(column, None)
            if self._sanitize_value(src_val) != self._sanitize_value(tgt_val):
                yield CSVDiff.of_field_mismatch(
                    record_id=record_id,
                    field=column,
                    source_value=src_val,
                    target_value=tgt_val,
                )
        return ()

    @staticmethod
    def _sanitize_value(value: Any) -> Any:  # noqa: ANN401
        # FIXME: This should probably only be done for specific columns.
        if not isinstance(value, str):
            return value
        return value.strip().lower()


@frozen
class CSVReconciler(Reconciler):
    """A :class:`Reconciler` that operates on CSV datasets.

    This ``Reconciler`` outsources CSV records comparisons to an instance of
    :class:`CSVRecordDiffer`. It does, however, identify records missing on
    both the source and target datasets natively.
    """

    _source: Iterable[str] = field(
        alias="source",
        repr=False,
        validator=validators.instance_of((Iterable,)),
    )
    _target: Iterable[str] = field(
        alias="target",
        repr=False,
        validator=validators.instance_of((Iterable,)),
    )
    _csv_rec_differ_factory: CSVRecordDifferFactory = field(
        alias="csv_record_differ_factory",
        default=SimpleCSVRecordDiffer,
        repr=False,
        validator=validators.is_callable(),
    )
    _unresolved_src_records: dict[str, CSVRecord] = field(
        factory=dict,
        init=False,
        repr=False,
    )
    _unresolved_tgt_records: dict[str, CSVRecord] = field(
        factory=dict,
        init=False,
        repr=False,
    )

    @override
    def reconcile(self) -> Iterable[CSVDiff]:
        source: csv.DictReader = csv.DictReader(self._source)
        target: csv.DictReader = csv.DictReader(self._target)

        src_record: CSVRecord | None
        tgt_record: CSVRecord | None

        csv_record_differ: Differ[CSVRecord, CSVRecord, str]
        csv_record_differ = self._csv_rec_differ_factory()
        for src_record, tgt_record in zip_longest(source, target):
            if src_record and tgt_record:
                src_id_column: str = self._get_record_id_column(src_record)
                tgt_id_column: str = self._get_record_id_column(tgt_record)
                src_id: str = src_record[src_id_column]
                tgt_id: str = tgt_record[tgt_id_column]

                if src_id == tgt_id:
                    yield from csv_record_differ.compare(
                        source=src_record,
                        target=tgt_record,
                        record_id=src_id,
                    )
                else:
                    self._unresolved_src_records[src_id] = src_record
                    self._unresolved_tgt_records[tgt_id] = tgt_record
            elif src_record:
                src_id_column: str = self._get_record_id_column(src_record)
                src_id: str = src_record[src_id_column]

                if src_id in self._unresolved_tgt_records:
                    yield from csv_record_differ.compare(
                        source=src_record,
                        target=self._unresolved_tgt_records.pop(src_id),
                        record_id=src_id,
                    )
                else:
                    self._unresolved_src_records[src_id] = src_record
            elif tgt_record:
                tgt_id_column = self._get_record_id_column(tgt_record)
                tgt_id: str = tgt_record[tgt_id_column]

                if tgt_id in self._unresolved_src_records:
                    yield from csv_record_differ.compare(
                        source=self._unresolved_src_records.pop(tgt_id),
                        target=tgt_record,
                        record_id=tgt_id,
                    )
                else:
                    self._unresolved_tgt_records[tgt_id] = tgt_record

        for src_id in self._unresolved_src_records:
            yield CSVDiff.of_not_in_target(record_id=src_id)

        for tgt_id in self._unresolved_tgt_records:
            yield CSVDiff.of_not_in_source(record_id=tgt_id)

        return ()

    @staticmethod
    def _get_record_id_column(record: CSVRecord) -> str:
        # TODO: This should only be computed once. Consider caching this. But
        #  separate the IDs for source records and target records.
        return next(iter(record))
