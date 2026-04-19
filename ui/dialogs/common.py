"""
This module provides a thin wrapper for resolving internal content-pack
identifiers to user-visible labels.

It works by delegating directly to task_packs.pack_label_by_id,
returning the registered label for the given pack_id or the ID itself
when no label exists.

It contains a single function, pack_label(pack_id: str) -> str, which is
used by the UI and other layers to display human-friendly pack names
instead of raw identifiers.
"""

from __future__ import annotations

from task_packs import pack_label_by_id


def pack_label(pack_id: str) -> str:
    """Resolve a content pack identifier to a user-visible label.

    Args:
        pack_id: Internal pack id from session or configuration.

    Returns:
        Label returned by pack discovery, or ``pack_id`` when no label
        is registered for that id.
    """
    return pack_label_by_id(pack_id)
