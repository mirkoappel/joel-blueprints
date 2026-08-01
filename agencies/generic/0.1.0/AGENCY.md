---
kind: agency
id: {{agency_id}}
name: {{agency_name}}
version: 0.1.0
blueprint: generic@0.1.0
---

# {{agency_name}}

This is a complete JoEL Agency: a recursively composable organization with one
Manager, persistent Agents, child Agencies, a shared Knowledge Base, a shared
Workspace, and an Archive.

## Anatomy

```text
<agency>/
├── AGENTS.md
├── CLAUDE.md
├── AGENCY.md
├── agents/
├── agencies/
├── knowledge/
├── workspace/
│   ├── projects/
│   └── shared/
└── archive/
    ├── projects/
    ├── agents/
    └── agencies/
```

Every child below `agencies/` has the same contract. Recursion is constrained
by purpose, authority, available resources, the harness, and an explicit depth
limit when children are authorized. The directory tree is ancestry; circular
ancestry is invalid.

## Agents and projects

Each Agent has its own contract, assignments, Workbench, Memory, adaptations,
and handoff. Exactly one active Agent is the Agency Manager. Agent and Agency
IDs are stable, role-neutral, and unique throughout the Root Agency tree.

Substantive shared work belongs in `workspace/projects/<project-id>/`. A
project's `PROJECT.md` holds purpose, scope and authority, evidence and
decisions, current position, completion criteria, and exact next action. Moving
the project directory to `archive/projects/` records completion.

## Knowledge and improvement

Agency `knowledge/` holds supported reusable organizational learning. Agent
`memory/` holds personal experiential learning. Workspace and Workbench content
is provisional unless promoted with provenance and uncertainty.

Live units may adapt explicitly. A published Blueprint is immutable: a tested
improvement becomes a successor version rather than rewriting its origin.
Material reflexive change requires a successor, evaluation, required approval,
and explicit handover.

## Authority

This Agency operates within the purpose, permissions, and resources granted by
its parent or Steward. It may not expand those boundaries itself. Contacting
people, publishing, spending, creating accounts, submitting forms, or other
external actions require explicit authorization for the concrete action.

