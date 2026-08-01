# JoEL 0.1.0

**Joint Orchestration & Evolution Lab**

![JoEL — a recursive, file-based Agency](docs/joel-hero.jpg)

> A small, inspectable filesystem for Agencies that work with Agents, learn from experience, and improve without losing their history.

JoEL is a portable, harness-neutral starting point for building persistent AI-supported organizations. It is intentionally made of ordinary folders, Markdown files, YAML frontmatter, and a few optional standard-library tools. Open the directory in an Agent Harness and the first Agency can begin a conversation.

The important idea is not a particular prompt. It is the relationship between **structure, authority, memory, work, evidence, and change**. The filesystem is the visible surface of the organization: its working environment, durable memory, lineage, and handoff protocol in one place.

## Why JoEL exists

Most Agent experiments are easy to start and hard to continue. Instructions live in a chat window, decisions disappear into transcripts, and a “better version” often means silently replacing the old one. That makes it difficult to inspect what an Agent actually is, to reproduce a setup, or to learn from failure.

JoEL explores a different premise:

> If an organization is represented by a small, explicit filesystem, can people and Agents understand it, operate it, and improve it across different Agent Harnesses?

This is an experiment in **persistent agency**, not a claim that folders automatically create intelligence. The files provide a shared, inspectable substrate. Judgment, evidence, authorization, and human participation still matter.

## The experiment

Version 0.1.0 asks a deliberately small set of questions:

1. Can the presence, absence, and contents of files be enough to express operational state without a hidden state database?
2. Can one Agency contract be reused recursively, so that a child Agency is the same kind of thing as the Root Agency rather than a special “sub-system”?
3. Can a useful organization start with one manager Agent and create further structure only when a real need appears?
4. Can local observations become durable learning and then explicit, reviewable improvements instead of invisible self-modification?
5. Can the same seed be opened in different Agent Harnesses without an installer, package manager, or vendor-specific runtime?
6. Which assumptions fail when the system meets real work, different permissions, or a different Harness?

JoEL is therefore intentionally mission-neutral at first start. It does not create a research mission, a project, a team, or a child Agency on its own. It first establishes a relationship with the Steward and waits for a meaningful purpose.

## The design in one sentence

**A Root Agency is a self-similar, file-based organization whose manager coordinates bounded Agents and child Agencies; durable learning moves from local work into explicit knowledge, adaptations, and versioned Blueprints.**

## Design principles

### 1. The filesystem is the canonical surface

The directory tree is not a cache of some more authoritative hidden object. It is the inspectable surface of the Agency. A missing `steward.md`, an existing project, or an archived Agent is meaningful because it is visible and reviewable. Harness-specific runtime state may exist, but it must not silently redefine the Agency.

### 2. The Root is already an Agency

There is no extra “instance” wrapper around the first Agency. The directory you open is the Root Agency. A child Agency uses the same contract and shape. This removes an unnecessary layer and makes recursive composition possible.

### 3. Self-similarity with limits

An Agency may create a child Agency when a durable boundary, separate knowledge base, or independent work context is justified. The child is not a different species. Recursion is constrained by authority, available resources, human intent, and practical depth; “unlimited” means the model does not hard-code an arbitrary architectural ceiling, not that it should create structure without purpose.

### 4. The manager is an Agent, not a god-object

The Root starts with one persistent Agent, `agent-0001`, whose role is `agency-manager` and whose name is JoEL by default. The manager coordinates work and is the primary conversational contact. It remains an Agent with an Agent’s memory, workbench, assignments, and handoff rather than gaining a magical second identity outside the model.

### 5. Keep the smallest useful hierarchy

JoEL separates only what needs a different owner or scope:

- An **Agency** owns shared Workspace, Knowledge, child Agencies, and the coordination contract.
- An **Agent** owns a Workbench, Memory, assignments, adaptations, and handoff records.
- A **Project** is a durable unit of work inside the Agency Workspace.

Names describe scope. They do not create a second hidden state model.

### 6. Agency Workspace is not Agent Workbench

The shared `workspace/` is where an Agency’s projects and collaboration material live. An Agent’s `workbench/` is its private or assignment-scoped working area. This distinction supports collaboration without pretending that every scratch note is shared truth.

### 7. Agency Knowledge is not Agent Memory

`knowledge/` contains Agency-level, promoted understanding: decisions, validated patterns, and reference material that others may rely on. `memory/` contains an Agent’s experience, provisional observations, and working context. Promotion is deliberate; an Agent’s recollection does not become organizational truth merely because it was written down.

### 8. No installation and no surprise mission

The initial seed has no installer and no required Python dependency. The Harness opens the directory, reads the bootstrap files, and JoEL performs a safe capability check. The first conversation asks how the person wants to be addressed and how JoEL can help. Only then can a real assignment create a project, additional Agents, or a child Agency.

### 9. Authority is explicit

The human Steward controls the purpose, external actions, safety boundaries, and constitutional changes. Agents may research public information and work inside the repository by default. Contacting people, publishing, spending money, creating accounts, or representing a finding as market-validated requires explicit authorization.

### 10. Evidence before confidence

JoEL distinguishes observation, source-backed fact, inference, hypothesis, uncertainty, and failed search. A solution gap is never proven by not finding a product once. Claims record their search scope, sources, access date, and limitations. A failed path is useful learning and should remain visible.

### 11. Evolution is explicit, not mystical

Experience can lead to a local adaptation. A tested structural change can become a successor Agency or Agent contract. A reusable, reviewed variant can become a published Blueprint. The system does not require a genome metaphor, automatic mutation, or a hidden “self-rewrite” to improve. It requires traceable changes, evaluation, and a way to hand control back to the Steward.

### 12. Portability is a design constraint

`AGENTS.md` is the canonical bootstrap file. `CLAUDE.md` is a one-line compatibility entry point for Claude-style Harnesses. The core format uses ordinary Markdown and YAML frontmatter. The Python helpers are validators and convenience tools, not a runtime dependency.

## What happens on first start

The first run is intentionally uneventful:

1. The Harness reads `AGENTS.md` (or the compatible `CLAUDE.md`) and follows the order of operations described there.
2. It reads the Root Agency contract and the manager Agent’s contract.
3. It checks the visible directory and records safe Harness capabilities in `harness.md`.
4. JoEL introduces itself as the Agency manager and asks how to address the Steward.
5. After the Steward answers, JoEL records that relationship in `steward.md` and asks how it can help.
6. The first actual need determines whether a Project, another Agent, or a child Agency is warranted.

No mission is invented. No population is spawned. No remote Blueprint Library is required to boot the Root.

## Initial shape

The seed is small enough to understand at a glance:

```text
joel-0.1.0/
├── AGENTS.md                 # canonical Harness bootstrap
├── CLAUDE.md                 # compatibility entry point
├── AGENCY.md                 # Root Agency contract
├── README.md                 # this design and experiment brief
├── VERSION                   # distribution version
├── CHANGELOG.md
├── agents/
│   └── agent-0001/            # JoEL, the first agency-manager Agent
│       ├── AGENTS.md
│       ├── CLAUDE.md
│       ├── assignments/
│       ├── workbench/
│       ├── memory/
│       ├── adaptations/
│       └── handoff/
├── agencies/                 # child Agencies, created only when needed
├── knowledge/                # shared, promoted Agency knowledge
├── workspace/
│   ├── projects/              # durable Agency work
│   └── shared/                # collaboration material
├── archive/                   # explicit historical record
│   ├── agents/
│   ├── agencies/
│   └── projects/
├── docs/
│   └── joel-hero.jpg
└── tools/                    # optional validation helpers
```

`harness.md` and `steward.md` are intentionally absent from a fresh seed. They appear as part of first contact. The same principle applies to projects and children: structure is created by need, not by ceremony.

## Filesystem model

| Path | Owner | Purpose |
| --- | --- | --- |
| `AGENTS.md` | Harness / Root | Bootstrap order, permissions, and operating rules. |
| `CLAUDE.md` | Harness / Root | Compatibility include for Harnesses that look for this name. |
| `AGENCY.md` | Agency | The Agency contract: purpose, roles, boundaries, and lifecycle. |
| `agents/` | Agency | Persistent Agents belonging to this Agency. |
| `agents/<id>/AGENTS.md` | Agent | The Agent’s contract, role, and local operating rules. |
| `assignments/` | Agent | Bounded work received from the Agency or a parent Agent. |
| `workbench/` | Agent | Mutable scratch and working files for that Agent. |
| `memory/` | Agent | Experience, observations, and provisional learning. |
| `adaptations/` | Agent | Explicit proposed or tested changes to the Agent’s method. |
| `handoff/` | Agent | Findings, open questions, and transfer notes for the Agency. |
| `agencies/` | Agency | Child Agencies that use the same recursive contract. |
| `knowledge/` | Agency | Shared knowledge promoted beyond one Agent’s memory. |
| `workspace/projects/` | Agency | Durable Projects and their evidence, decisions, and outputs. |
| `workspace/shared/` | Agency | Shared material that is not itself a Project. |
| `archive/` | Agency | Historical Agents, Agencies, and Projects kept out of the active tree. |
| `harness.md` | Root / Harness | Observed Harness capabilities and compatibility notes. |
| `steward.md` | Root / Steward relationship | How the Agency addresses and works with its human Steward. |

The exact file names are intentionally conventional. A human should be able to understand the architecture from the tree before reading every prompt.

## Agencies, Agents, and Projects

### Agencies

An Agency is the smallest recursive organization in JoEL. It has a contract, a shared Workspace, a Knowledge area, persistent Agents, and optional child Agencies. A child Agency should exist because a boundary is useful: a distinct mission, responsibility, knowledge domain, risk boundary, or long-lived work context. It should not exist merely because spawning is available.

### Agents

Agents receive stable, location-independent IDs such as `agent-0001`. A human-readable name and role are recorded separately. IDs are useful for lineage; names are useful for collaboration. An Agent may be a manager, researcher, validator, developer, generalist, or another role described by its contract. Roles are replaceable; history is not.

The manager can create and coordinate other Agents within the Agency’s authority. It cannot silently grant itself new permissions or erase a difficult result. When an Agent is retired, its whole record can move to `archive/agents/` so that later work can learn from it.

### Projects

Projects live below `workspace/projects/`. They hold a bounded purpose, assignments, evidence, decisions, outputs, and open questions. A Project can involve multiple Agents. When it is closed, the Project is archived as a unit rather than having its useful context scattered across unrelated folders.

## The Blueprint model

The live Root is deliberately separate from the public [JoEL Blueprints Library](https://github.com/mirkoappel/joel-blueprints). The Root can start without a network connection or a copy of the Library. The Library is the place for reusable, versioned starting points; it is not hidden runtime state.

A Blueprint is a complete, named, versioned contract for an Agency, Agent, or future Skill. It is more than a prompt fragment. Its origin is recorded in managed frontmatter and its reference is exact, for example `joel@0.1.0` or `agency-manager@0.1.0`.

Materializing a Blueprint means deliberately creating a new object from that exact reference. It does not make the live object permanently dependent on the Library, and later Library releases do not rewrite an existing Agency. A live Agency can propose a successor Blueprint after it has gathered evidence, tested a change, and received the appropriate approval.

The concrete `joel@0.1.0` Blueprint is kept in the Library as a reference and reproducible seed. That duplication is intentional: it lets the running Root remain self-contained while giving other Agencies a stable origin to inspect or materialize.

## Improvement and evolution loop

JoEL treats improvement as a chain of increasingly stronger claims:

| Stage | Typical artifact | What it means |
| --- | --- | --- |
| Observe | `memory/`, `handoff/`, Project notes | Something happened, was noticed, or remains uncertain. |
| Understand | `knowledge/` proposal or validated note | The Agency has checked whether the learning is reusable. |
| Adapt locally | `adaptations/` | An Agent or Agency proposes a bounded change to its method. |
| Test | evaluation notes, comparison, failure record | The change is compared against the previous method under a fair scope. |
| Promote | successor contract or Blueprint proposal | A reusable change is made explicit and reviewable. |
| Publish | a new immutable Library version | Others can reproduce the starting point without changing history. |

The Developer role can implement changes for another Agent or Agency within its authority. It can also propose changes to its own method, but it must not silently replace its active contract and declare itself improved. Self-change requires an explicit successor, evidence, evaluation, and a handoff path.

This is compatible with evolutionary experimentation, but it does not force every learning process into a genome or generation metaphor. Named differences, fair comparisons, lineage, diversity, and preserved failure lessons are more important than the metaphor.

## Harness portability

JoEL assumes only that a Harness can:

- open a directory and read Markdown files;
- follow a root instruction file;
- create and edit files in the permitted workspace;
- communicate with a human Steward.

The optional `tools/joel.py` helper uses only Python’s standard library. It can report status, validate the visible structure, and run the tests. A Harness without Python can still run JoEL; it can perform the same checks manually or with its own native tooling. No package installation is part of first start.

The compatibility rule is simple: use capabilities the Harness actually exposes, record important limitations in `harness.md`, and never pretend that a serial chat turn is independent multi-Agent validation.

## Safety and authority

JoEL is designed to make agency more inspectable, not to remove human responsibility.

- Public research and repository-local work are allowed within the assignment.
- External contact, publication, purchases, account creation, form submission, and claims of market validation require explicit Steward approval.
- Evidence must distinguish fact, inference, hypothesis, and uncertainty.
- Constitution, safety, scoring meaning, and authorization boundaries do not change silently.
- A failed search, rejected proposal, or weak result is retained when it can improve future judgment.
- Structural changes are validated before they become the new active shape.

## Use JoEL as a reference, not just a runtime

JoEL is also a compact teaching and design object. An innovation consultant, AI trainer, or workshop facilitator can use it to make otherwise abstract questions concrete:

- What does an Agent actually own?
- Where does a team’s shared knowledge live?
- When is a new Agent or child Agency justified?
- What is the difference between a useful adaptation and an undocumented prompt tweak?
- Which actions should remain human-authorized?
- How can a failed experiment become an asset rather than disappear?

You can run the seed, map it to another Harness, use the tree as a workshop exercise, fork the contracts, or propose a better vocabulary. Please challenge the assumptions. The project is meant to invite careful participation and extension, not passive consumption of a finished doctrine.

## Start using JoEL

Clone the Root Agency and open the directory in an Agent Harness:

```bash
git clone https://github.com/mirkoappel/joel.git
cd joel
```

Then let the Harness read `AGENTS.md` and start the conversation. The optional local checks are:

```bash
python3 tools/joel.py status
python3 tools/joel.py validate
python3 tools/test_joel.py
```

If you want reusable starting points for other Agencies or Agents, browse the [Blueprint Library](https://github.com/mirkoappel/joel-blueprints). The Library has its own README and validation tools.

## Current scope of 0.1.0

Included:

- one self-contained Root Agency;
- one persistent manager Agent, JoEL;
- recursive Agency and Agent contracts;
- separated Agency Workspace / Knowledge and Agent Workbench / Memory;
- explicit harness and Steward first-contact records;
- archive and handoff conventions;
- optional standard-library validation helpers and tests;
- a separate public Blueprint Library with exact references;
- MIT licensing for reuse and experimentation.

Intentionally not included:

- a preselected research mission;
- task-specific Skills or a Skill marketplace;
- automatic Agent spawning or automatic external actions;
- hidden state synchronization or a remote process manager;
- automatic fitness scoring, mutation, or publishing;
- a claim of independent market validation;
- a requirement that every Harness expose the same tools.

These are boundaries of the experiment, not promises about future versions.

## Success criteria for this experiment

JoEL 0.1.0 is useful if a person can inspect it and answer what exists, who owns it, what is allowed, and what would change next. A stronger test is whether a second Harness can open the same seed, complete first contact honestly, create a bounded Project, preserve a failure lesson, and materialize a child Agency without inventing hidden state.

The project succeeds further when improvements are explainable: someone can compare the old and new contract, see the evidence, understand the authority used, and decide whether the change deserves to become a Blueprint for others.

## Contributing

Start with a concrete observation. Explain the problem, the current behavior, the smallest proposed change, and how it can be tested. Preserve uncertainty and failed attempts. Changes to contracts, safety rules, authorization boundaries, or the meaning of evidence need explicit Steward review. Improvements to examples, adapters, tests, and explanatory material are welcome when they remain honest about what was actually tested.

The [Blueprint Library](https://github.com/mirkoappel/joel-blueprints) is the preferred place for reusable Agency, Agent, and future Skill variants. This repository is the complete `joel@0.1.0` Root seed.

## License

JoEL is released under the [MIT License](LICENSE).
