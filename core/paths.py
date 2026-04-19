"""
This module centralizes filesystem paths and directory setup for
configuration and history data used by the application.

It computes a project root directory based on the location of the
current file and defines constant subdirectory and file names for
config, data, and history storage.

It exposes CONFIG_DIR, DATA_DIR, HISTORY_DIR and corresponding full file
paths like CONFIG_PATH, CHECK_HISTORY_PATH, and CHECK_HISTORY_DB_PATH as
Path constants for consistent use elsewhere.

The ensure_data_directories function creates the config, data, and
history directories (with parents) if they do not already exist,
ensuring the environment is ready before reading or writing files.

Within the broader system, this module acts as the single source of
truth for on-disk layout, reducing path duplication and avoiding
scattered directory-creation logic.
"""

from __future__ import annotations

from pathlib import Path
from typing import Final

CONFIG_DIR_NAME: Final[str] = "config"
DATA_DIR_NAME: Final[str] = "data"
HISTORY_DIR_NAME: Final[str] = "history"
CONFIG_FILE_NAME: Final[str] = "config.json"
HISTORY_FILE_NAME: Final[str] = "history.json"
HISTORY_DB_FILE_NAME: Final[str] = "history.sqlite3"

ROOT: Final[Path] = Path(__file__).resolve().parent.parent

CONFIG_DIR: Final[Path] = ROOT / CONFIG_DIR_NAME
DATA_DIR: Final[Path] = ROOT / DATA_DIR_NAME
HISTORY_DIR: Final[Path] = DATA_DIR / HISTORY_DIR_NAME

CONFIG_PATH: Final[Path] = CONFIG_DIR / CONFIG_FILE_NAME
CHECK_HISTORY_PATH: Final[Path] = HISTORY_DIR / HISTORY_FILE_NAME
CHECK_HISTORY_DB_PATH: Final[Path] = HISTORY_DIR / HISTORY_DB_FILE_NAME


def ensure_data_directories() -> None:
    """Ensure all persisted-data directories exist.

    Returns:
        None
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
