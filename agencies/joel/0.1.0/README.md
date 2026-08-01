# JoEL 0.1.0

**Joint Orchestration & Evolution Lab**

JoEL is a portable, file-based Agency that can work in different Agent
harnesses. The repository is already the first, fully materialized Agency. It
does not install software and it does not create a mission, project, child
Agency, or extra Agent before the Steward asks for one.

## Start

1. Clone or unpack this repository into a writable directory.
2. Open the repository root in an Agent harness.
3. Ask the harness to begin, or simply say hello.

The harness reads `AGENTS.md`. Claude Code reads `CLAUDE.md`, which imports the
same instructions. JoEL checks the harness, introduces itself, asks how to
address the Steward, and asks how it can help.

No `pip install`, package manager, setup wizard, or generated runtime directory
is required.

## Initial shape

```text
.
├── AGENTS.md
├── CLAUDE.md
├── AGENCY.md
├── README.md
├── VERSION
├── CHANGELOG.md
├── agents/
│   └── agent-0001/
│       ├── AGENTS.md
│       ├── CLAUDE.md
│       ├── assignments/
│       ├── workbench/
│       ├── memory/
│       ├── adaptations/
│       └── handoff/
├── agencies/
├── knowledge/
├── workspace/
│   ├── projects/
│   └── shared/
├── archive/
└── tools/
```

The root is the Root Agency, not a wrapper around one. A child directory below
`agencies/` repeats the Agency shape and may itself contain Agents and child
Agencies.

## Derived status

JoEL stores no separate state file:

- no `harness.md` and no `steward.md`: first start;
- `harness.md` only: environment checked, waiting to meet the Steward;
- both files: ready to resume;
- active projects: directories below `workspace/projects/`;
- completed projects: directories below `archive/projects/`.

Inspect this derived status with:

```sh
python3 tools/joel.py status
```

Validate the complete structure with:

```sh
python3 tools/joel.py validate
python3 tools/test_joel.py
```

Python is only an optional validation convenience and uses the standard
library. The Agency remains operable without it.

## Blueprint Library

Reusable Agent, Agency, and Skill Blueprints live in a separate repository.
The library is not copied into ordinary JoEL Agencies and is not needed during
first contact. A Manager resolves an exact pinned Blueprint only when a new
persistent Agent or Agency is requested.

## Development

Live learning stays local until it is tested. A Developer can prepare a
successor JoEL or Blueprint, but active contracts and historical releases are
not silently rewritten. Record release-level changes in `CHANGELOG.md`.

This release intentionally contains no mission-specific Agency.
