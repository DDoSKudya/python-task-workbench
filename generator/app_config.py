"""Configuration model for CLI execution modes."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    """Store immutable CLI generation and verification settings.

    Attributes:
        count: Number of tasks to generate in a session.
        seed: Optional random seed for deterministic generation.
        show_solution: Whether to print reference solutions.
        topic: Topic filter passed to task generation.
        stage: Stage selector used by the generator.
        data_volume: Data volume profile.
        data_order: Data ordering profile.
        data_quality: Data quality profile.
        profile: Generation profile preset.
        domain: Domain filter.
        surprise_me: Whether profile settings are randomized.
        focus_tool: Preferred tool token for generated tasks.
        mode: CLI mode name.
        solution_file: Path to the solution file.
        state_file: Path to the state file.
        export_format: Export format name.
        export_file: Optional explicit export path.
        story_mode: Whether story mode is enabled.
        session_size: Target story-session size.
        inverse_rate: Ratio of inverse tasks in generation.
        show_full_example: Whether to show full examples in output.
        hints_step: Whether to print step-by-step hints.
        strict_types: Whether strict answer comparison is enabled.
        content_pack: Source content pack identifier.
    """

    count: int
    seed: int | None
    show_solution: bool
    topic: str
    stage: str
    data_volume: str
    data_order: str
    data_quality: str
    profile: str
    domain: str
    surprise_me: bool
    focus_tool: str
    mode: str
    solution_file: str
    state_file: str
    export_format: str
    export_file: str | None
    story_mode: bool
    session_size: int
    inverse_rate: float
    show_full_example: bool
    hints_step: bool
    strict_types: bool
    content_pack: str
