# JoEL Blueprint Library 0.1.0

This is the remote-ready Blueprint Library for JoEL. Keep it in a repository
separate from a running JoEL Agency. A running Agency does not need the Library
to start or resume; it needs an exact Blueprint only when it creates a
persistent Agent or child Agency.

## Catalog

| Reference | Produces | Required values |
| --- | --- | --- |
| `joel@0.1.0` | Complete, uninitialized JoEL Root Agency | none |
| `generic@0.1.0` | Child or standalone Agency | `agency_id`, `agency_name`, `manager_id`, `manager_name` |
| `agency-manager@0.1.0` | Agency Manager Agent | `agent_id`, `agent_name` |
| `generalist@0.1.0` | General-purpose Agent | `agent_id`, `agent_name`, optional `role` |
| `developer@0.1.0` | System-development Agent | `agent_id`, `agent_name` |

Skill Blueprints have a reserved namespace under `skills/`; JoEL 0.1.0 ships
without a task-specific Skill.

## No-install use

```sh
python3 tools/blueprints.py list
python3 tools/blueprints.py validate
```

Materialize a fresh JoEL repository:

```sh
python3 tools/blueprints.py materialize agency joel@0.1.0 ../joel
```

Materialize a child Agency:

```sh
python3 tools/blueprints.py materialize agency generic@0.1.0 ../agency-0002 \
  --set agency_id=agency-0002 \
  --set agency_name="Opportunity Research" \
  --set manager_id=agent-0002 \
  --set manager_name="Scout"
```

Materialize an Agent:

```sh
python3 tools/blueprints.py materialize agent generalist@0.1.0 ../agent-0003 \
  --set agent_id=agent-0003 \
  --set agent_name="Researcher" \
  --set role=researcher
```

The target must not already exist. Materialization is deliberately
non-destructive and does not run the resulting Agent or Agency.

## Repository layout

```text
agencies/<blueprint-name>/<version>/
agents/<blueprint-name>/<version>/
skills/<blueprint-name>/<version>/
tools/blueprints.py
```

There is no `blueprint.yaml`: the path supplies kind, name, and version; the
managed Markdown frontmatter supplies the materialized contract. Avoiding a
second metadata source keeps the Library auditable and prevents drift.

## Version and promotion rules

Blueprint directories are immutable once published. Contract-compatible
capability additions use a minor version; incompatible identity, authority, or
contract changes use a major version; clarifications without changed behavior
use a patch version.

A proposed improvement normally travels through:

1. observed learning in an Agent's Memory or Agency Knowledge;
2. an explicit local adaptation;
3. evaluation against the previous behavior;
4. a proposed successor Blueprint;
5. Steward-approved review and publication as a new version.

Git is the recommended publication, review, rollback, and contribution layer,
but the on-disk format remains usable in harnesses without Git.

