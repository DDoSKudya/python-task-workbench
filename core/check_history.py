"""
This module manages persistent storage and export of code check history
using a SQLite database and Python source file exports.

It defines a history_entries SQLite table and a large set of constants
for schema keys, limits, export labels, and formatting details.

It provides helper functions to truncate long text, pretty-print and
serialize values, coerce types from JSON/SQLite, and safely build
triple-quoted string literals and slugified filenames.

The _HistoryStore class encapsulates connecting to SQLite, initializing
the schema, migrating legacy JSON history into the database, inserting
new check records, trimming old rows beyond a configured limit, loading
rows newest-first, and clearing all history.

The HistoryRowView dataclass represents a normalized, immutable view of
a history row for UI layers, with a factory that interprets raw SQLite
rows and derives the passed flag and booleans.

Export-related functions assemble a single history row into a structured
Python module string with ASCII banners, metadata, result and error
sections, and Python-literal assignments for input and expected result,
and then write it to disk.

Top-level convenience functions (append_check_record,
load_entries_newest_first, clear_history_file, and the export helpers)
delegate to a default _HistoryStore and are intended to be used by the
rest of the system to record, browse, clear, and export check runs.
"""

from __future__ import annotations

import ast
import json
import re
import sqlite3
from collections.abc import Sequence
from datetime import datetime, timezone

from dataclasses import dataclass
from pathlib import Path
from typing import Final, TypeGuard

from messages import (
    HISTORY_EXPORT_BANNER_ERROR_DINAMIC_POSTFIX_Q4PT,
    HISTORY_EXPORT_BANNER_METADATA_DINAMIC_POSTFIX_Q4PT,
    HISTORY_EXPORT_BANNER_RESULT_DINAMIC_POSTFIX_Q4PT,
    HISTORY_EXPORT_HEADER_DINAMIC_POSTFIX_Q4PT,
    HISTORY_EXPORT_LABEL_DURATION_DINAMIC_POSTFIX_Q4PT,
    HISTORY_EXPORT_LABEL_EXECUTED_AT_DINAMIC_POSTFIX_Q4PT,
    HISTORY_EXPORT_LABEL_HISTORY_ID_DINAMIC_POSTFIX_Q4PT,
    HISTORY_EXPORT_LABEL_PACK_NAME_DINAMIC_POSTFIX_Q4PT,
    HISTORY_EXPORT_LABEL_SESSION_SEED_DINAMIC_POSTFIX_Q4PT,
    HISTORY_EXPORT_LABEL_STATUS_DINAMIC_POSTFIX_Q4PT,
    HISTORY_EXPORT_LABEL_STRICT_TYPES_DINAMIC_POSTFIX_Q4PT,
    HISTORY_EXPORT_LABEL_TASK_ID_DINAMIC_POSTFIX_Q4PT,
    HISTORY_EXPORT_LABEL_TASK_TITLE_DINAMIC_POSTFIX_Q4PT,
    HISTORY_EXPORT_STATUS_FAILED_DINAMIC_POSTFIX_Q4PT,
    HISTORY_EXPORT_STATUS_LINE_PREFIX_DINAMIC_POSTFIX_Q4PT,
    HISTORY_EXPORT_STATUS_PASSED_DINAMIC_POSTFIX_Q4PT,
)

from .formatting import pretty
from .models import CheckResult, SessionConfig, Task
from .paths import CHECK_HISTORY_DB_PATH, CHECK_HISTORY_PATH

_MIN_DURATION_SEC: Final[float] = 0.0
_LEGACY_MIGRATION_DURATION_SEC: Final[float] = 0.0
_MAX_FILE_ITEMS: Final[int] = 2500
_MAX_CODE_CHARS: Final[int] = 48_000
_MAX_ERROR_CHARS: Final[int] = 80_000
_MAX_VALUE_CHARS: Final[int] = 80_000
_TRUNCATION_SUFFIX: Final[str] = "… [truncated]"
_JSON_ENCODING: Final[str] = "utf-8"
_ISO_TIMESPEC_SECONDS: Final[str] = "seconds"
_EMPTY_TEXT: Final[str] = ""
_DB_TIMEOUT_SEC: Final[float] = 5.0
_STATUS_PASSED: Final[str] = "passed"
_STATUS_FAILED: Final[str] = "failed"
_PYTHON_MODULE_HEADER: Final[str] = (
    f'"""{HISTORY_EXPORT_HEADER_DINAMIC_POSTFIX_Q4PT}"""\n\n'
)
_FILENAME_SANITIZE_RE: Final[re.Pattern[str]] = re.compile(
    r"[^a-zA-Z0-9]+",
)
_FILENAME_MAX_STEM_LEN: Final[int] = 48
_EXPORT_DEFAULT_SLUG: Final[str] = "history"
_EXPORT_FILENAME_PREFIX: Final[str] = "history_"
_EXPORT_FILENAME_EXT: Final[str] = ".py"
_EXPORT_FILENAME_PART_SEP: Final[str] = "_"
_EXPORT_BANNER_INNER_WIDTH: Final[int] = 71
_EXPORT_HASH_CHAR: Final[str] = "#"
_EXPORT_BANNER_SIDE_TEMPLATE: Final[str] = "# {content} #"
_EXPORT_NAME_INPUT_DATA: Final[str] = "INPUT_DATA"
_EXPORT_NAME_EXPECTED_RESULT: Final[str] = "EXPECTED_RESULT"
_EXPORT_EMPTY_TRIPLE_QUOTED: Final[str] = '""""""'
_TRIPLE_QUOTE_TOKEN: Final[str] = '"""'
_TRIPLE_QUOTE_ESCAPED: Final[str] = '\\"""'
_NEWLINE: Final[str] = "\n"

_KEY_ID: Final[str] = "id"
_KEY_TS: Final[str] = "ts"
_KEY_DURATION_SEC: Final[str] = "duration_sec"
_KEY_TASK_ID: Final[str] = "task_id"
_KEY_TASK_TITLE: Final[str] = "task_title"
_KEY_PACK_NAME: Final[str] = "pack_name"
_KEY_STATUS: Final[str] = "status"
_KEY_PASSED: Final[str] = "passed"
_KEY_CODE: Final[str] = "code"
_KEY_ERROR_TEXT: Final[str] = "error_text"
_KEY_RESULT_TEXT: Final[str] = "result_text"
_KEY_INPUT_DATA: Final[str] = "input_data"
_KEY_EXPECTED_RESULT: Final[str] = "expected_result"
_KEY_ACTUAL_PREVIEW: Final[str] = "actual_preview"
_KEY_SESSION_SEED: Final[str] = "session_seed"
_KEY_STRICT_TYPES: Final[str] = "strict_types"

_SQL_COUNT_HISTORY_ROWS: Final[str] = (
    "SELECT COUNT(1) AS count FROM history_entries"
)
_SQL_DELETE_ALL_HISTORY: Final[str] = "DELETE FROM history_entries"

_CREATE_HISTORY_TABLE_SQL: Final[
    str
] = """
CREATE TABLE IF NOT EXISTS history_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    duration_sec REAL NOT NULL,
    task_id TEXT NOT NULL,
    task_title TEXT NOT NULL,
    pack_name TEXT NOT NULL,
    status TEXT NOT NULL,
    input_data TEXT NOT NULL,
    expected_result TEXT NOT NULL,
    code TEXT NOT NULL,
    result_text TEXT NOT NULL,
    error_text TEXT NOT NULL,
    session_seed INTEGER,
    strict_types INTEGER NOT NULL
)
"""

_INSERT_HISTORY_ENTRY_SQL: Final[
    str
] = """
INSERT INTO history_entries (
    ts,
    duration_sec,
    task_id,
    task_title,
    pack_name,
    status,
    input_data,
    expected_result,
    code,
    result_text,
    error_text,
    session_seed,
    strict_types
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

_SELECT_NEWEST_SQL: Final[
    str
] = """
SELECT
    id,
    ts,
    duration_sec,
    task_id,
    task_title,
    pack_name,
    status,
    input_data,
    expected_result,
    code,
    result_text,
    error_text,
    session_seed,
    strict_types
FROM history_entries
ORDER BY id DESC
"""

_TRIM_HISTORY_SQL: Final[
    str
] = """
DELETE FROM history_entries
WHERE id NOT IN (
    SELECT id
    FROM history_entries
    ORDER BY id DESC
    LIMIT ?
)
"""


def _is_string_key_object_dict(value: object) -> TypeGuard[dict[str, object]]:
    """Return whether ``value`` is a dict with only string keys.

    Args:
        value: Candidate value from JSON decoding.

    Returns:
        ``True`` when ``value`` is a ``dict[str, object]``-like mapping.
    """
    if not isinstance(value, dict):
        return False
    return all(isinstance(key, str) for key in value)


def _truncate_text(value: str, limit: int) -> str:
    """Truncate ``value`` to ``limit`` characters, keeping a suffix.

    Args:
        value: Source text.
        limit: Maximum number of characters allowed.

    Returns:
        The original string when short enough, otherwise a truncated
        string ending with ``_TRUNCATION_SUFFIX``.
    """
    if len(value) <= limit:
        return value
    reserve = len(_TRUNCATION_SUFFIX)
    if limit <= reserve:
        return value[:limit]
    return f"{value[: limit - reserve]}{_TRUNCATION_SUFFIX}"


def _render_value(value: object, *, limit: int) -> str:
    """Render structured data as persisted text with a size cap.

    Args:
        value: Arbitrary Python value to format.
        limit: Maximum number of characters for the rendered text.

    Returns:
        Pretty-printed, truncated text suitable for storage.
    """
    return _truncate_text(pretty(value), limit)


def _required_str(value: object) -> str:
    """Coerce ``value`` to ``str``, falling back to empty text.

    Args:
        value: Raw value from JSON or SQLite.

    Returns:
        ``value`` when it is a ``str``, otherwise ``_EMPTY_TEXT``.
    """
    return value if isinstance(value, str) else _EMPTY_TEXT


def _required_bool(value: object) -> bool:
    """Coerce ``value`` to ``bool`` when it is already boolean.

    Args:
        value: Raw value from legacy JSON.

    Returns:
        ``value`` when it is a ``bool``, otherwise ``False``.
    """
    return value if isinstance(value, bool) else False


def _required_float(value: object) -> float:
    """Coerce ``value`` to ``float`` when possible.

    Args:
        value: Raw numeric value from SQLite or JSON.

    Returns:
        A finite float, or ``0.0`` when coercion is not possible.
    """
    if isinstance(value, bool):
        return _MIN_DURATION_SEC
    return (
        float(value) if isinstance(value, (int, float)) else _MIN_DURATION_SEC
    )


def _optional_int(value: object) -> int | None:
    """Parse an optional integer, rejecting booleans.

    Args:
        value: Raw value from JSON or SQLite.

    Returns:
        ``None`` for ``None`` or bool, an ``int`` when ``value`` is int,
        otherwise ``None``.
    """
    if value is None or isinstance(value, bool):
        return None
    return value if isinstance(value, int) else None


def _strict_types_from_sql(value: object) -> bool:
    """Interpret SQLite strict_types integer as a boolean.

    Args:
        value: Raw ``strict_types`` cell value.

    Returns:
        ``True`` for truthy integers, explicit ``True`` booleans, and
        ``False`` otherwise.
    """
    if isinstance(value, bool):
        return value
    return value != 0 if isinstance(value, int) else False


def _as_triple_quoted(value: str) -> str:
    """Wrap ``value`` as a triple-quoted Python string literal.

    Args:
        value: Raw text to embed in generated Python source.

    Returns:
        A syntactically valid triple-quoted string literal token.
    """
    normalized = value.replace(_TRIPLE_QUOTE_TOKEN, _TRIPLE_QUOTE_ESCAPED)
    return f"{_TRIPLE_QUOTE_TOKEN}{normalized}{_TRIPLE_QUOTE_TOKEN}"


def _export_banner(title: str) -> str:
    """Build an ASCII banner as a triple-quoted literal expression.

    Args:
        title: Short section title; normalized to upper case.

    Returns:
        Python source fragment containing one triple-quoted banner.
    """
    label = title.strip().upper()
    mid = _EXPORT_BANNER_SIDE_TEMPLATE.format(
        content=label.center(_EXPORT_BANNER_INNER_WIDTH),
    )
    border = _EXPORT_HASH_CHAR * len(mid)
    body = f"{border}{_NEWLINE}{mid}{_NEWLINE}{border}"
    return _as_triple_quoted(body)


def _export_metadata_lines(row: HistoryRowView) -> str:
    """Build the metadata block for a Python export.

    Args:
        row: History row to describe.

    Returns:
        Multi-line metadata text for embedding in exports.
    """
    lines: list[str] = [
        f"{HISTORY_EXPORT_LABEL_HISTORY_ID_DINAMIC_POSTFIX_Q4PT}{row.id}",
        _EMPTY_TEXT,
        f"{HISTORY_EXPORT_LABEL_TASK_ID_DINAMIC_POSTFIX_Q4PT}{row.task_id!r}",
        _EMPTY_TEXT,
        (
            f"{HISTORY_EXPORT_LABEL_TASK_TITLE_DINAMIC_POSTFIX_Q4PT}"
            f"{row.task_title!r}"
        ),
        _EMPTY_TEXT,
        (
            f"{HISTORY_EXPORT_LABEL_EXECUTED_AT_DINAMIC_POSTFIX_Q4PT}"
            f"{row.ts!r}"
        ),
        _EMPTY_TEXT,
        (
            f"{HISTORY_EXPORT_LABEL_DURATION_DINAMIC_POSTFIX_Q4PT}"
            f"{row.duration_sec!r}"
        ),
        _EMPTY_TEXT,
        f"{HISTORY_EXPORT_LABEL_STATUS_DINAMIC_POSTFIX_Q4PT}{row.status!r}",
        _EMPTY_TEXT,
        (
            f"{HISTORY_EXPORT_LABEL_PACK_NAME_DINAMIC_POSTFIX_Q4PT}"
            f"{row.pack_name!r}"
        ),
        _EMPTY_TEXT,
        (
            f"{HISTORY_EXPORT_LABEL_SESSION_SEED_DINAMIC_POSTFIX_Q4PT}"
            f"{row.session_seed}"
        ),
        _EMPTY_TEXT,
        (
            f"{HISTORY_EXPORT_LABEL_STRICT_TYPES_DINAMIC_POSTFIX_Q4PT}"
            f"{row.strict_types}"
        ),
    ]
    return _NEWLINE.join(lines)


def _try_literal_eval_export(text: str) -> object | None:
    """Parse stored task text as a Python literal when safe.

    Args:
        text: Persisted pretty-printed or literal text.

    Returns:
        The evaluated object on success, otherwise ``None``.
    """
    stripped = text.strip()
    if not stripped:
        return None
    try:
        return ast.literal_eval(stripped)
    except (ValueError, SyntaxError, MemoryError, TypeError):
        return None


def _export_python_literal_assignment(name: str, stored_text: str) -> str:
    """Emit ``name = ...`` using ``pretty`` when ``stored_text`` parses.

    Args:
        name: Left-hand assignment target name.
        stored_text: Persisted representation of the value.

    Returns:
        One assignment line plus a trailing newline.
    """
    parsed = _try_literal_eval_export(stored_text)
    if parsed is None:
        return f"{name} = {_as_triple_quoted(stored_text)}{_NEWLINE}"
    return f"{name} = {pretty(parsed)}{_NEWLINE}"


def _python_module_for_row(row: HistoryRowView) -> str:
    """Render one history row as an exportable Python module.

    Args:
        row: History row to serialize.

    Returns:
        Complete ``.py`` file contents for the row.
    """
    status_label = (
        HISTORY_EXPORT_STATUS_PASSED_DINAMIC_POSTFIX_Q4PT
        if row.passed
        else HISTORY_EXPORT_STATUS_FAILED_DINAMIC_POSTFIX_Q4PT
    )
    result_body = row.result_text
    error_body = row.error_text
    if result_body.strip():
        result_literal = _as_triple_quoted(result_body)
    else:
        result_literal = _EXPORT_EMPTY_TRIPLE_QUOTED
    error_literal = _as_triple_quoted(error_body)
    code_block = row.code.rstrip(_NEWLINE)
    if code_block:
        code_block = f"{code_block}{_NEWLINE}"
    status_line = (
        f"{HISTORY_EXPORT_STATUS_LINE_PREFIX_DINAMIC_POSTFIX_Q4PT}"
        f"{status_label}{_NEWLINE}{_NEWLINE}"
    )
    parts: list[str] = [
        _PYTHON_MODULE_HEADER,
        status_line,
        _export_banner(HISTORY_EXPORT_BANNER_METADATA_DINAMIC_POSTFIX_Q4PT),
        _NEWLINE,
        _NEWLINE,
        _as_triple_quoted(_export_metadata_lines(row)),
        _NEWLINE,
        _NEWLINE,
        _export_banner(HISTORY_EXPORT_BANNER_RESULT_DINAMIC_POSTFIX_Q4PT),
        _NEWLINE,
        _NEWLINE,
        result_literal,
        _NEWLINE,
        _NEWLINE,
        _export_banner(HISTORY_EXPORT_BANNER_ERROR_DINAMIC_POSTFIX_Q4PT),
        _NEWLINE,
        _NEWLINE,
        error_literal,
        _NEWLINE,
        _NEWLINE,
        _export_python_literal_assignment(
            _EXPORT_NAME_INPUT_DATA,
            row.input_data,
        ),
        _NEWLINE,
        _export_python_literal_assignment(
            _EXPORT_NAME_EXPECTED_RESULT,
            row.expected_result,
        ),
        _NEWLINE,
        code_block,
    ]
    return "".join(parts)


def _slugify_filename(value: str) -> str:
    """Normalize free text for use inside export filenames.

    Args:
        value: Arbitrary human-readable text.

    Returns:
        Lowercase slug capped by ``_FILENAME_MAX_STEM_LEN``, or the
        default slug when nothing usable remains.
    """
    cleaned = _FILENAME_SANITIZE_RE.sub(
        _EXPORT_FILENAME_PART_SEP,
        value.strip(),
    ).strip(_EXPORT_FILENAME_PART_SEP)
    if not cleaned:
        return _EXPORT_DEFAULT_SLUG
    return cleaned[:_FILENAME_MAX_STEM_LEN].lower()


def _default_export_name(row: HistoryRowView) -> str:
    """Build the default ``.py`` filename for one history row.

    Args:
        row: History row used for id, timestamp, and task slug.

    Returns:
        A filesystem-safe filename ending with ``_EXPORT_FILENAME_EXT``.
    """
    timestamp = _slugify_filename(row.ts)
    task_slug = _slugify_filename(row.task_id or row.task_title)
    return (
        f"{_EXPORT_FILENAME_PREFIX}{row.id}{_EXPORT_FILENAME_PART_SEP}"
        f"{timestamp}{_EXPORT_FILENAME_PART_SEP}{task_slug}"
        f"{_EXPORT_FILENAME_EXT}"
    )


class _HistoryStore:
    """SQLite persistence for append, listing, trim, and migration."""

    __slots__ = ("_db_path", "_legacy_json_path")

    def __init__(self, db_path: Path, legacy_json_path: Path) -> None:
        """Initialize the store with concrete filesystem paths.

        Args:
            db_path: SQLite database file path.
            legacy_json_path: Legacy JSON history file path, if any.
        """
        self._db_path = db_path
        self._legacy_json_path = legacy_json_path

    def _connect(self) -> sqlite3.Connection:
        """Open a SQLite connection with row factories and schema ready.

        Returns:
            Open connection; caller must close or use as context mgr.
        """
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(
            self._db_path,
            timeout=_DB_TIMEOUT_SEC,
        )
        conn.row_factory = sqlite3.Row
        self._initialize_schema(conn)
        return conn

    def _row_count(self, conn: sqlite3.Connection) -> int:
        """Return the number of rows in ``history_entries``.

        Args:
            conn: Active SQLite connection.

        Returns:
            Non-negative row count.
        """
        row = conn.execute(_SQL_COUNT_HISTORY_ROWS).fetchone()
        return 0 if row is None else int(row["count"])

    def _load_legacy_rows(self) -> list[dict[str, object]]:
        """Load legacy JSON history rows when the file exists.

        Returns:
            Parsed legacy rows, or an empty list on missing or bad data.
        """
        if not self._legacy_json_path.is_file():
            return []
        try:
            raw = self._legacy_json_path.read_text(encoding=_JSON_ENCODING)
            payload = json.loads(raw)
        except (OSError, json.JSONDecodeError):
            return []
        if not isinstance(payload, list):
            return []
        return [item for item in payload if _is_string_key_object_dict(item)]

    def _trim_excess_rows(self, conn: sqlite3.Connection) -> None:
        """Delete older rows beyond ``_MAX_FILE_ITEMS``.

        Args:
            conn: Active SQLite connection.
        """
        conn.execute(_TRIM_HISTORY_SQL, (_MAX_FILE_ITEMS,))

    def _migrate_legacy_json_if_needed(
        self,
        conn: sqlite3.Connection,
    ) -> None:
        """Import legacy JSON into SQLite when the table is still empty.

        Args:
            conn: Active SQLite connection.
        """
        if self._row_count(conn) > 0:
            return
        legacy_rows = self._load_legacy_rows()
        if not legacy_rows:
            return
        for raw in legacy_rows:
            passed = _required_bool(raw.get(_KEY_PASSED))
            conn.execute(
                _INSERT_HISTORY_ENTRY_SQL,
                (
                    _required_str(raw.get(_KEY_TS)),
                    _LEGACY_MIGRATION_DURATION_SEC,
                    _required_str(raw.get(_KEY_TASK_ID)),
                    _required_str(raw.get(_KEY_TASK_TITLE)),
                    _required_str(raw.get(_KEY_PACK_NAME)),
                    _STATUS_PASSED if passed else _STATUS_FAILED,
                    _EMPTY_TEXT,
                    _EMPTY_TEXT,
                    _required_str(raw.get(_KEY_CODE)),
                    (
                        _required_str(raw.get(_KEY_ACTUAL_PREVIEW))
                        if passed
                        else _EMPTY_TEXT
                    ),
                    (
                        _EMPTY_TEXT
                        if passed
                        else _required_str(raw.get(_KEY_ERROR_TEXT))
                    ),
                    _optional_int(raw.get(_KEY_SESSION_SEED)),
                    int(_required_bool(raw.get(_KEY_STRICT_TYPES))),
                ),
            )
        self._trim_excess_rows(conn)

    def _initialize_schema(self, conn: sqlite3.Connection) -> None:
        """Ensure schema exists and run one-time legacy import.

        Args:
            conn: Active SQLite connection.
        """
        conn.execute(_CREATE_HISTORY_TABLE_SQL)
        self._migrate_legacy_json_if_needed(conn)

    def record_check(
        self,
        *,
        task: Task,
        result: CheckResult,
        code: str,
        config: SessionConfig,
        duration_sec: float,
    ) -> None:
        """Insert one check record and trim history to the row cap.

        Args:
            task: Task metadata and payloads to persist.
            result: Outcome and payloads from the checker.
            code: Learner source code snapshot.
            config: Session seed and strict typing flag.
            duration_sec: Wall-clock duration of the check in seconds.
        """
        now = datetime.now(timezone.utc).astimezone()
        passed = result.passed
        status = _STATUS_PASSED if passed else _STATUS_FAILED
        if passed:
            result_text = _render_value(
                result.actual_result,
                limit=_MAX_VALUE_CHARS,
            )
        else:
            result_text = _EMPTY_TEXT
        if passed:
            error_text = _EMPTY_TEXT
        else:
            error_text = _truncate_text(
                result.error_text or _EMPTY_TEXT,
                _MAX_ERROR_CHARS,
            )
        with self._connect() as conn:
            conn.execute(
                _INSERT_HISTORY_ENTRY_SQL,
                (
                    now.isoformat(timespec=_ISO_TIMESPEC_SECONDS),
                    max(_MIN_DURATION_SEC, duration_sec),
                    task.task_id,
                    task.title,
                    task.pack_name,
                    status,
                    _render_value(task.input_data, limit=_MAX_VALUE_CHARS),
                    _render_value(
                        task.expected_result,
                        limit=_MAX_VALUE_CHARS,
                    ),
                    _truncate_text(code, _MAX_CODE_CHARS),
                    result_text,
                    error_text,
                    config.seed,
                    int(config.strict_types),
                ),
            )
            self._trim_excess_rows(conn)

    def load_entries_newest_first(self) -> list[HistoryRowView]:
        """Load all rows ordered from newest primary key to oldest.

        Returns:
            Normalized row views for UI consumption.
        """
        with self._connect() as conn:
            rows = conn.execute(_SELECT_NEWEST_SQL).fetchall()
        return [HistoryRowView.from_row(row) for row in rows]

    def clear_all(self) -> None:
        """Remove every persisted history row."""
        with self._connect() as conn:
            conn.execute(_SQL_DELETE_ALL_HISTORY)


_DEFAULT_STORE: Final[_HistoryStore] = _HistoryStore(
    CHECK_HISTORY_DB_PATH,
    CHECK_HISTORY_PATH,
)


@dataclass(frozen=True)
class HistoryRowView:
    """Immutable view of one ``history_entries`` row for UI layers."""

    id: int
    ts: str
    duration_sec: float
    task_id: str
    task_title: str
    pack_name: str
    status: str
    passed: bool
    input_data: str
    expected_result: str
    code: str
    result_text: str
    error_text: str
    session_seed: int | None
    strict_types: bool

    @classmethod
    def from_row(cls, raw: sqlite3.Row) -> HistoryRowView:
        """Build a view from a SQLite ``history_entries`` row.

        Args:
            raw: Row object produced with ``sqlite3.Row`` factory.

        Returns:
            Normalized, immutable model for callers.
        """
        status = _required_str(raw[_KEY_STATUS])
        return cls(
            id=int(raw[_KEY_ID]),
            ts=_required_str(raw[_KEY_TS]),
            duration_sec=_required_float(raw[_KEY_DURATION_SEC]),
            task_id=_required_str(raw[_KEY_TASK_ID]),
            task_title=_required_str(raw[_KEY_TASK_TITLE]),
            pack_name=_required_str(raw[_KEY_PACK_NAME]),
            status=status,
            passed=status == _STATUS_PASSED,
            input_data=_required_str(raw[_KEY_INPUT_DATA]),
            expected_result=_required_str(raw[_KEY_EXPECTED_RESULT]),
            code=_required_str(raw[_KEY_CODE]),
            result_text=_required_str(raw[_KEY_RESULT_TEXT]),
            error_text=_required_str(raw[_KEY_ERROR_TEXT]),
            session_seed=_optional_int(raw[_KEY_SESSION_SEED]),
            strict_types=_strict_types_from_sql(raw[_KEY_STRICT_TYPES]),
        )


def append_check_record(
    *,
    task: Task,
    result: CheckResult,
    code: str,
    config: SessionConfig,
    duration_sec: float,
) -> None:
    """Append a check result to the default SQLite history store.

    Args:
        task: Task metadata and payloads to persist.
        result: Outcome and payloads from the checker.
        code: Learner source code snapshot.
        config: Session seed and strict typing flag.
        duration_sec: Wall-clock duration of the check in seconds.
    """
    _DEFAULT_STORE.record_check(
        task=task,
        result=result,
        code=code,
        config=config,
        duration_sec=duration_sec,
    )


def load_entries_newest_first() -> list[HistoryRowView]:
    """Return history rows with the most recent entry first.

    Returns:
        Row views ordered by descending ``id``.
    """
    return _DEFAULT_STORE.load_entries_newest_first()


def clear_history_file() -> None:
    """Delete all rows from the default SQLite history database."""
    _DEFAULT_STORE.clear_all()


def export_history_entry_to_python(
    row: HistoryRowView,
    target_path: Path,
) -> Path:
    """Write one history row to a ``.py`` file at ``target_path``.

    Args:
        row: History row to export.
        target_path: Destination path for generated source.

    Returns:
        The ``target_path`` that was written.
    """
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(
        _python_module_for_row(row),
        encoding=_JSON_ENCODING,
    )
    return target_path


def export_history_rows_to_python(
    rows: Sequence[HistoryRowView],
    target_dir: Path,
) -> list[Path]:
    """Export each history row to its own ``.py`` file under
    ``target_dir``.

    Args:
        rows: History rows to export.
        target_dir: Directory that will contain the new files.

    Returns:
        Paths of all written files, in input order.
    """
    target_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for row in rows:
        path = target_dir / _default_export_name(row)
        export_history_entry_to_python(row, path)
        written.append(path)
    return written


def default_history_export_filename(row: HistoryRowView) -> str:
    """Return the suggested single-row export filename.

    Args:
        row: History row used for naming.

    Returns:
        Basename ending with ``_EXPORT_FILENAME_EXT``.
    """
    return _default_export_name(row)
