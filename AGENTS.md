---
kind: blueprint-library
system: JoEL
version: 0.1.0
---

# JoEL Blueprint Library

This repository is a versioned catalog of immutable starting points for JoEL
Agencies, Agents, and Skills. It is not a running Agency and must not be treated
as one.

## Mandatory startup

Before changing or materializing a Blueprint:

1. read `README.md` completely;
2. inspect the exact pinned Blueprint requested;
3. run `python3 tools/blueprints.py validate` when Python 3 is available;
4. materialize into a new, absent target path;
5. inspect and validate the result before execution.

No package installation is required. If Python is unavailable, copy the exact
versioned directory, replace every declared `{{token}}`, and verify that no
unresolved token remains.

## Library contract

- Blueprint references are exact and pinned: `<name>@<semantic-version>`.
- Published version directories are immutable. A behavioral change creates a
  new version; it never edits the meaning of an existing reference.
- An Agency Blueprint produces a complete Agency. An Agent Blueprint produces
  a complete Agent folder. Skill Blueprints may be added under `skills/`.
- The directory hierarchy and managed Markdown frontmatter are canonical. Do
  not add a second manifest that duplicates them.
- Materialization records origin in the resulting managed document's
  `blueprint` field.
- A live unit may adapt locally. Its Blueprint origin does not change
  retroactively.
- Promotion of a live adaptation into this Library requires evidence, review,
  migration notes when relevant, and a new version.

## Change boundary

Do not silently change purpose, authority, safety boundaries, or the semantics
of versioning. Do not overwrite a materialization target, perform external
actions, or publish changes without the Steward's explicit authorization.

