---
kind: agency-bootloader
system: JoEL
version: 0.1.0
agency: {{agency_id}}
---

# {{agency_name}} bootloader

This is the single entrypoint for this Agency. The Agency is already
materialized; there is no installation step.

## Mandatory startup

1. Read `AGENCY.md` completely.
2. Find and read the one Agent under `agents/` whose `AGENTS.md` declares
   `role: agency-manager`.
3. Inspect the actual filesystem and relevant parent assignment or handoff.
4. Read `harness.md` and `steward.md` when present, then relevant Agency
   Knowledge, projects, Agent Memory, assignments, and handoffs only.
5. Resume the exact next action in the responsible project.

The filesystem is canonical. Do not create a parallel `state/` directory,
identity file, Manager registry, or duplicate status summary.

## Harness adaptation

Use observed capabilities and inherited restrictions. If no trustworthy harness
profile applies, safely check filesystem access, persistence, shell, Python,
Git, web, connectors, independent Agent capacity, sandbox, approvals, and
external-action boundaries without installing anything. Record only observed
or explicitly unknown facts in `harness.md` when this Agency needs its own
profile.

## Operating boundary

- The Agency Manager owns shared Agency changes.
- Ordinary Agents write only inside their own folder unless an assignment
  grants exact additional paths.
- Persistent Agents and child Agencies are materialized from exact pinned
  Blueprints and validated before execution.
- A child Agency receives no permission its parent lacks.
- External actions require the Steward's explicit authorization.
- Core purpose, authority, safety, and boot-contract changes require approval
  and a version increment.

Before ending substantive work, keep the responsible project's exact next
action current, promote only supported reusable learning, preserve handoffs and
uncertainty, and validate structural changes.

