"""Tests for :mod:`generator.cli.entry`."""

from __future__ import annotations

import re

import pytest

from generator.cli import entry
from messages import UNSUPPORTED_ARGV_ERROR_DINAMIC_POSTFIX_FT6H


def test_cli_main_rejects_non_empty_argv() -> None:
    """Reject argv when the CLI is configured for config-file-only use.

    Returns:
        None.
    """
    unexpected = ["unexpected"]
    expected_msg = UNSUPPORTED_ARGV_ERROR_DINAMIC_POSTFIX_FT6H
    with pytest.raises(ValueError, match=re.escape(expected_msg)):
        entry.cli_main(unexpected)
