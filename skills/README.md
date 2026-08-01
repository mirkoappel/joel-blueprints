# Skill Blueprints

This namespace is reserved for reusable, versioned capability contracts that
an Agency or Agent may adapt to its purpose. JoEL 0.1.0 deliberately includes
no task-specific Skill: the first Agency starts without a mission.

A future Skill Blueprint lives at `skills/<name>/<version>/`, declares its
inputs, outputs, authority boundaries, verification, and adaptation points, and
is materialized from an exact pinned reference. A Skill does not own Agency
state and does not replace an Agent's identity or an Agency's governance.

