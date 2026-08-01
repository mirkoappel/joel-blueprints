# JoEL Blueprint Library 0.1.0

![JoEL Blueprint Library — reusable organizational patterns](docs/joel-hero.jpg)

> A public collection of exact, inspectable starting points for Agencies, Agents, and future Skills.

This repository is the external Blueprint Library for [JoEL](https://github.com/mirkoappel/joel). It is a catalogue and publication surface, not a running Agency. A live Agency can boot, converse, and do local work without this repository. It consults the Library when it deliberately wants to create a new persistent object from a known, versioned starting point.

## Why the Library is separate

Keeping reusable Blueprints outside the live Root solves several problems at once:

- a fresh Agency stays small and has no required network or installation step;
- running work can evolve locally without rewriting the published origin;
- a Blueprint can be inspected, reviewed, tested, forked, and reproduced independently;
- several Agencies and Harnesses can share a stable reference;
- a later Library release does not silently mutate an existing Agency.

The separation is a boundary, not a second hidden runtime. The live filesystem remains the source of truth for a running Agency. This repository is the source of truth for published starting points.

## What a Blueprint is

A Blueprint is a complete, named, versioned contract for an object that can be materialized:

- an **Agency Blueprint** defines the recursive organizational shape, manager relationship, shared Workspace, Knowledge, and authority boundaries;
- an **Agent Blueprint** defines a persistent Agent’s role, operating rules, memory boundary, and handoff expectations;
- a **Skill Blueprint** is a reserved future namespace for a reusable capability contract. JoEL 0.1.0 intentionally ships without a task-specific Skill.

A Blueprint is therefore more than a prompt fragment and less than a running process. It describes a reproducible starting condition. Each managed Markdown file records its Blueprint origin and version in frontmatter. The directory path also carries the canonical identity: `<kind>/<name>/<version>`.

Use exact references such as `joel@0.1.0` or `agency-manager@0.1.0`. Do not resolve “latest” when creating a persistent object; reproducibility is more valuable than convenience.

## The current catalogue

| Reference | Kind | Produces | Required values |
| --- | --- | --- | --- |
| `joel@0.1.0` | Agency | Complete, uninitialized JoEL Root Agency | none |
| `generic@0.1.0` | Agency | Child or standalone Agency | `agency_id`, `agency_name`, `manager_id`, `manager_name` |
| `agency-manager@0.1.0` | Agent | Agency Manager Agent | `agent_id`, `agent_name` |
| `generalist@0.1.0` | Agent | General-purpose Agent | `agent_id`, `agent_name`, optional `role` |
| `developer@0.1.0` | Agent | System-development Agent | `agent_id`, `agent_name` |

The catalogue is intentionally small. It demonstrates the recursive core without pretending that every domain-specific role is already solved. New research, validation, facilitation, or domain Blueprints should arrive because real use exposed a repeatable need.

## How the Library relates to the Root

The [JoEL runtime repository](https://github.com/mirkoappel/joel) contains a complete `joel@0.1.0` Root seed. This Library contains the same concrete Blueprint below `agencies/joel/0.1.0/` so that it can be inspected and materialized like any other published starting point.

That duplication is deliberate:

1. the Root can start offline and remain self-contained;
2. the Library can publish immutable, reusable origins;
3. a running Agency can record the exact reference from which a child was created;
4. later versions can be compared rather than silently substituted.

The live Root does not need a local `blueprints/` directory. A Harness or Agency may fetch this repository when a materialization is authorized, but a child Agent does not inherit a whole Library just because it was created from one Blueprint.

## No-install use

The helper uses only Python’s standard library. It is a validator and materializer, not a runtime dependency of a generated Agency.

List the catalogue and validate all published Blueprints:

```sh
python3 tools/blueprints.py list
python3 tools/blueprints.py validate
python3 tools/test_blueprints.py
```

Materialize a fresh JoEL Root:

```sh
python3 tools/blueprints.py materialize agency joel@0.1.0 ../joel
```

Materialize a child Agency with explicit values:

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

The target must not already exist. Materialization is non-destructive, does not run the resulting object, does not contact anyone, and does not grant permissions that are not already allowed by the parent Agency.

## Repository layout

```text
joel-blueprints-0.1.0/
├── README.md
├── AGENTS.md
├── CLAUDE.md
├── VERSION
├── CHANGELOG.md
├── LICENSE
├── docs/
│   └── joel-hero.jpg
├── agencies/
│   ├── joel/0.1.0/          # complete Root Agency Blueprint
│   └── generic/0.1.0/       # recursive child Agency Blueprint
├── agents/
│   ├── agency-manager/0.1.0/
│   ├── generalist/0.1.0/
│   └── developer/0.1.0/
├── skills/                  # reserved namespace; no task Skill in 0.1.0
└── tools/
    ├── blueprints.py
    └── test_blueprints.py
```

There is no `blueprint.yaml`. The path supplies kind, name, and version; managed Markdown frontmatter supplies the contract metadata. Avoiding a second metadata source keeps the Library auditable and reduces drift between an index and the files it describes.

## Materialization is a boundary

Creating an object from a Blueprint is not the same as running it. A responsible caller should:

1. resolve an exact reference;
2. inspect its contract, required values, and authority limits;
3. choose a target path that does not already exist;
4. materialize the files;
5. validate the result in the parent context;
6. record the origin and the reason for creation;
7. only then hand the new object to the appropriate Harness.

The materialized object may later adapt. Its origin remains historical truth; a local change does not retroactively change the Blueprint that created it.

## Evolution and promotion

The Library is a publication endpoint for learning, not an automatic mutation engine. A healthy path from experience to publication is:

| Stage | Local evidence | Publication meaning |
| --- | --- | --- |
| Observe | Agent Memory, Agency Knowledge, Project notes | Something happened or a limitation was found. |
| Propose | explicit adaptation | A bounded change is stated rather than hidden in a prompt edit. |
| Test | comparison, validation, failure record | The change has been examined against the previous behavior. |
| Review | lineage, scope, authority, uncertainty | A human or authorized reviewer decides whether it is reusable. |
| Publish | new immutable Blueprint version | Others can reproduce the improved starting point. |

An Agency can develop a new Blueprint without turning every adjustment into a new release. A release is appropriate when a change is reusable, documented, and meaningful to a new materialization. A live object should never silently rewrite the published version it came from.

## Versioning

Blueprints follow semantic versioning:

- **patch**: clarification, typo fix, or behavior-preserving documentation change;
- **minor**: backward-compatible capability or example addition;
- **major**: incompatible identity, authority, safety, or contract change.

Published directories are immutable. If a contract changes, create a new version and preserve the old one for reproducibility. Git provides review, history, rollback, and contribution workflows, but the on-disk format remains usable in Harnesses without Git.

## Quality and contribution rules

When proposing a Blueprint:

- start from an observed need or a reusable pattern, not a speculative name;
- include exact origin metadata and explicit required values;
- keep identity, authority, safety, and ownership boundaries visible;
- distinguish facts, inferences, hypotheses, and unresolved questions;
- preserve failed attempts and uncertainty when they prevent false confidence;
- validate the complete materialization and update tests when behavior changes;
- do not overwrite existing targets or introduce an installer requirement;
- do not publish a change as “improved” based only on the Agent’s self-assessment;
- link related Blueprints and explain what is intentionally not included.

Changes to the JoEL constitution, authorization boundary, safety rules, or meaning of evidence require explicit Steward review. Documentation, examples, adapters, and tests are welcome contributions when they remain honest about what was actually exercised.

## A reference for workshops and innovation work

The Library is useful even when no one materializes a file. It gives innovation consultants, AI trainers, and teams a concrete vocabulary for discussing:

- the difference between an Agency, an Agent, and a Skill;
- why shared Knowledge and private Memory should not be conflated;
- when recursion creates useful boundaries and when it creates bureaucracy;
- how a local prompt tweak becomes a reviewable organizational change;
- what a Harness can and cannot promise;
- how an open Blueprint can invite experimentation without hiding responsibility.

Fork the repository, compare variants, use a Blueprint as a workshop exercise, or propose a better one. The catalogue is a living reference, but its versions are not disposable: the point of publishing them is to make design decisions discussable and history recoverable.

## Current scope of 0.1.0

Included:

- Agency, Agent, and reserved Skill namespaces;
- one complete JoEL Root Blueprint;
- a recursive generic Agency Blueprint;
- manager, generalist, and developer Agent Blueprints;
- exact-reference lookup, validation, and non-destructive materialization;
- tests for catalogue integrity and required values;
- MIT licensing.

Not included:

- a remote registry or marketplace protocol;
- automatic updates or “latest” resolution;
- task-specific Skills;
- automatic spawning, scoring, mutation, or publication;
- a claim that a Blueprint is market-validated merely because it exists here.

These omissions keep the first Library understandable and make future additions testable rather than implied.

## License

The Blueprint Library and its included JoEL materials are released under the [MIT License](LICENSE).
