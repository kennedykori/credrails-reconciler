from __future__ import annotations

from typing import TYPE_CHECKING

from importlib_metadata import entry_points

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping


def list_available_entry_point_names(
    entrypoint_group_name: str,
) -> Iterable[str]:
    _entry_points = entry_points(group=entrypoint_group_name)
    return tuple(entry_point.name for entry_point in _entry_points)


def load_from_entrypoint[T](entrypoint_group_name: str) -> Mapping[str, T]:  # pyright: ignore
    _entry_points = entry_points(group=entrypoint_group_name)
    return {
        entry_point.name: entry_point.load() for entry_point in _entry_points
    }
