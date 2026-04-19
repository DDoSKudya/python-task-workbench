# `data/history`

Runtime data for **Python Task Workbench**. In Git, only this `README.md` is tracked under `data/history/`; other paths are ignored (see the root `.gitignore`). Paths here are referenced from `config/config.json` (`default_state_file`, `default_solution_file`) and from the GUI check-history layer.

## What lives here

| File / path | Role |
|-------------|------|
| `.collections_tasks_state.pkl` | Serialized CLI/GUI task batch: templates, inputs, expected outputs, and metadata for the current session. Required for `check` / `coach` and for resuming context. |
| `collections_solutions.py` | Solution stub produced in **solve** mode (`solve_task_N`, `TASKS`, `TASK_IDS`, `ANSWERS`). You edit this file and run **check** or use the GUI. |
| `history.sqlite3` | SQLite database used by the PyQt app to store check history (created when you use history features). |

## Notes

- These files are **machine-local** and **session-specific**. They are not a substitute for version control of your own code; copy answers elsewhere if you care about long-term retention.
- If `TASK_IDS` in your solution file does not match the pickle state, regenerate tasks with **solve** or fix paths in config.
- Safe to delete `*.pkl` / `collections_solutions.py` when starting fresh; the app will recreate them on the next **solve** run (you will lose the in-progress batch).
