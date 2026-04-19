# `config`

Shared configuration and JSON **Schemas** for **Python Task Workbench**.

## Files

| File | Purpose |
|------|---------|
| `config.json` | Default UI and CLI settings: generation options (`default_*`), task pack, state/solution paths, checker behaviour (`checker_entry_mode`), and PyQt preferences (language, fonts, timeouts, splitter sizes). The app resolves these into the effective runtime config. |
| `content_task.schema.json` | JSON Schema for declarative **task** rows inside content packs (`tasks.json` and related). Used to validate structure when authoring packs. |
| `content_module.schema.json` | JSON Schema for pack **manifests** (`module.json` under `content_modules/`). Documents required fields and how packs plug into discovery. |

## Usage

- Edit `config.json` to change defaults before launching `python app.py` or `python app.py cli`. The CLI does not take a separate flag surface; behaviour is driven by this file and internal resolution.
- Schema `$id` values are stable identifiers for tooling (e.g. editors that associate JSON files with a schema). They are not network endpoints.

## Related

- Pack authoring details: `content_modules/README.md`.
- High-level project overview: repository root `README.md`.
