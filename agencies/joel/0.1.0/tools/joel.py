#!/usr/bin/env python3
"""Dependency-free inspection and validation for a JoEL Agency."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
BLUEPRINT_NAME = re.compile(r"^[a-z][a-z0-9-]*$")
IGNORED_NAMES = {".gitkeep", ".DS_Store", "__pycache__"}


class FrontmatterError(ValueError):
    pass


def scalar(value: str) -> str | bool | None:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    lowered = value.lower()
    if lowered in {"null", "~"}:
        return None
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    return value


def frontmatter(path: Path) -> dict[str, str | bool | None]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise FrontmatterError(str(exc)) from exc
    if not lines or lines[0].strip() != "---":
        raise FrontmatterError("missing opening ---")
    try:
        end = next(i for i, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration as exc:
        raise FrontmatterError("missing closing ---") from exc
    data: dict[str, str | bool | None] = {}
    for number, line in enumerate(lines[1:end], 2):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if line[:1].isspace() or ":" not in line:
            raise FrontmatterError(f"line {number} is not a flat key: value pair")
        key, value = line.split(":", 1)
        key = key.strip()
        if not re.fullmatch(r"[a-z][a-z0-9_-]*", key):
            raise FrontmatterError(f"line {number} has invalid key {key!r}")
        if key in data:
            raise FrontmatterError(f"duplicate key {key!r}")
        data[key] = scalar(value)
    return data


def visible_directories(path: Path) -> list[Path]:
    if not path.is_dir():
        return []
    return sorted(
        item for item in path.iterdir()
        if item.is_dir() and not item.name.startswith(".") and item.name not in IGNORED_NAMES
    )


def pinned_blueprint(value: object) -> bool:
    if not isinstance(value, str) or value.count("@") != 1:
        return False
    name, version = value.split("@", 1)
    return bool(BLUEPRINT_NAME.fullmatch(name) and SEMVER.fullmatch(version))


@dataclass
class Validation:
    root: Path
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    agency_ids: set[str] = field(default_factory=set)
    agent_ids: set[str] = field(default_factory=set)

    def relative(self, path: Path) -> str:
        try:
            return str(path.relative_to(self.root)) or "."
        except ValueError:
            return str(path)

    def require_file(self, path: Path) -> None:
        if not path.is_file():
            self.errors.append(f"missing file: {self.relative(path)}")

    def require_dir(self, path: Path) -> None:
        if not path.is_dir():
            self.errors.append(f"missing directory: {self.relative(path)}")

    def read_header(self, path: Path) -> dict[str, str | bool | None]:
        if not path.is_file():
            return {}
        try:
            return frontmatter(path)
        except FrontmatterError as exc:
            self.errors.append(f"invalid frontmatter in {self.relative(path)}: {exc}")
            return {}

    def check_version(self, header: dict[str, str | bool | None], path: Path) -> None:
        version = header.get("version")
        if not isinstance(version, str) or not SEMVER.fullmatch(version):
            self.errors.append(f"invalid or missing version in {self.relative(path)}")

    def check_claude_adapter(self, path: Path) -> None:
        if path.is_file() and path.read_text(encoding="utf-8").strip() != "@AGENTS.md":
            self.errors.append(f"Claude adapter must contain only @AGENTS.md: {self.relative(path)}")

    def check_forbidden_runtime_state(self, agency: Path) -> None:
        forbidden_files = ("identity.json", "identity.yaml", "state.json", "state.yaml", "blueprint-ref.json", "blueprint-ref.yaml")
        for name in forbidden_files:
            if (agency / name).exists():
                self.errors.append(f"duplicate state or identity file is forbidden: {self.relative(agency / name)}")
        for name in ("state", "managers"):
            if (agency / name).exists():
                self.errors.append(f"obsolete Agency directory is forbidden: {self.relative(agency / name)}")

    def validate_agent(self, agent: Path) -> dict[str, str | bool | None]:
        for relative in ("AGENTS.md", "CLAUDE.md"):
            self.require_file(agent / relative)
        for relative in ("assignments", "workbench", "memory", "adaptations", "handoff"):
            self.require_dir(agent / relative)
        self.check_claude_adapter(agent / "CLAUDE.md")
        header = self.read_header(agent / "AGENTS.md")
        if header.get("kind") != "agent":
            self.errors.append(f"wrong kind in {self.relative(agent / 'AGENTS.md')}: expected agent")
        self.check_version(header, agent / "AGENTS.md")
        agent_id = header.get("id")
        if not isinstance(agent_id, str) or not re.fullmatch(r"agent-\d{4,}", agent_id):
            self.errors.append(f"invalid Agent ID in {self.relative(agent / 'AGENTS.md')}")
        else:
            if agent_id != agent.name:
                self.errors.append(f"Agent folder and ID differ: {self.relative(agent)} != {agent_id}")
            if agent_id in self.agent_ids:
                self.errors.append(f"duplicate Agent ID: {agent_id}")
            self.agent_ids.add(agent_id)
        if not isinstance(header.get("name"), str) or not header.get("name"):
            self.errors.append(f"missing Agent name in {self.relative(agent / 'AGENTS.md')}")
        if not isinstance(header.get("role"), str) or not header.get("role"):
            self.errors.append(f"missing Agent role in {self.relative(agent / 'AGENTS.md')}")
        if not pinned_blueprint(header.get("blueprint")):
            self.errors.append(f"invalid Agent Blueprint reference in {self.relative(agent / 'AGENTS.md')}")
        return header

    def validate_project(self, project: Path) -> None:
        descriptor = project / "PROJECT.md"
        self.require_file(descriptor)
        header = self.read_header(descriptor)
        if not header:
            return
        if header.get("kind") != "project":
            self.errors.append(f"wrong kind in {self.relative(descriptor)}: expected project")
        self.check_version(header, descriptor)
        project_id = header.get("id")
        if project_id != project.name:
            self.errors.append(f"Project folder and ID differ: {self.relative(project)} != {project_id}")

    def validate_agency(self, agency: Path, *, root_agency: bool = False) -> None:
        for relative in ("AGENTS.md", "CLAUDE.md", "AGENCY.md"):
            self.require_file(agency / relative)
        for relative in ("agents", "agencies", "knowledge", "workspace/projects", "workspace/shared", "archive/projects", "archive/agents", "archive/agencies"):
            self.require_dir(agency / relative)
        self.check_claude_adapter(agency / "CLAUDE.md")
        self.check_forbidden_runtime_state(agency)

        agency_header = self.read_header(agency / "AGENCY.md")
        boot_header = self.read_header(agency / "AGENTS.md")
        if agency_header.get("kind") != "agency":
            self.errors.append(f"wrong kind in {self.relative(agency / 'AGENCY.md')}: expected agency")
        if boot_header.get("kind") != "agency-bootloader":
            self.errors.append(f"wrong kind in {self.relative(agency / 'AGENTS.md')}: expected agency-bootloader")
        self.check_version(agency_header, agency / "AGENCY.md")
        self.check_version(boot_header, agency / "AGENTS.md")

        agency_id = agency_header.get("id")
        if not isinstance(agency_id, str) or not re.fullmatch(r"agency-\d{4,}", agency_id):
            self.errors.append(f"invalid Agency ID in {self.relative(agency / 'AGENCY.md')}")
        else:
            if not root_agency and agency_id != agency.name:
                self.errors.append(f"Agency folder and ID differ: {self.relative(agency)} != {agency_id}")
            if agency_id in self.agency_ids:
                self.errors.append(f"duplicate Agency ID: {agency_id}")
            self.agency_ids.add(agency_id)
            if boot_header.get("agency") != agency_id:
                self.errors.append(f"Bootloader points at the wrong Agency: {self.relative(agency / 'AGENTS.md')}")
        if not isinstance(agency_header.get("name"), str) or not agency_header.get("name"):
            self.errors.append(f"missing Agency name in {self.relative(agency / 'AGENCY.md')}")
        if not pinned_blueprint(agency_header.get("blueprint")):
            self.errors.append(f"invalid Agency Blueprint reference in {self.relative(agency / 'AGENCY.md')}")

        manager_count = 0
        for agent in visible_directories(agency / "agents"):
            header = self.validate_agent(agent)
            if header.get("role") == "agency-manager":
                manager_count += 1
        if manager_count != 1:
            self.errors.append(f"Agency must have exactly one active Agency Manager: {self.relative(agency)} has {manager_count}")

        for project in visible_directories(agency / "workspace" / "projects"):
            self.validate_project(project)
        for child in visible_directories(agency / "agencies"):
            self.validate_agency(child)

        for optional, expected_kind in (("harness.md", "harness-profile"), ("steward.md", "steward")):
            path = agency / optional
            if path.exists():
                header = self.read_header(path)
                if header.get("kind") != expected_kind:
                    self.errors.append(f"wrong kind in {self.relative(path)}: expected {expected_kind}")
                self.check_version(header, path)


def validate(root: Path) -> Validation:
    result = Validation(root=root)
    for relative in ("README.md", "CHANGELOG.md", "VERSION", "tools/joel.py"):
        result.require_file(root / relative)
    if (root / "VERSION").is_file():
        package_version = (root / "VERSION").read_text(encoding="utf-8").strip()
        if not SEMVER.fullmatch(package_version):
            result.errors.append("VERSION is not a semantic version")
        boot_header = result.read_header(root / "AGENTS.md")
        if boot_header and boot_header.get("version") != package_version:
            result.errors.append("Root bootloader version and VERSION differ")
    if (root / "blueprints").exists() or (root / "installer").exists():
        result.errors.append("running Agency must not bundle a Blueprint Library or installer")
    result.validate_agency(root, root_agency=True)
    check_id_reuse(root, result)
    return result


def check_id_reuse(root: Path, result: Validation) -> None:
    """Reserve stable IDs across active and archived filesystem locations."""

    namespaces: dict[str, dict[str, list[Path]]] = {
        "Agency": {},
        "Agent": {},
        "Project": {},
    }

    def register(namespace: str, identifier: str, path: Path) -> None:
        namespaces[namespace].setdefault(identifier, []).append(path)

    try:
        root_id = frontmatter(root / "AGENCY.md").get("id")
    except FrontmatterError:
        root_id = None
    if isinstance(root_id, str):
        register("Agency", root_id, root)

    for path in root.rglob("*"):
        if not path.is_dir():
            continue
        relative = path.relative_to(root)
        if any(part.startswith(".") for part in relative.parts):
            continue
        if path.parent.name == "agencies" and re.fullmatch(r"agency-\d{4,}", path.name):
            register("Agency", path.name, path)
        elif path.parent.name == "agents" and re.fullmatch(r"agent-\d{4,}", path.name):
            register("Agent", path.name, path)
        elif (
            path.parent.name == "projects"
            and path.parent.parent.name in {"workspace", "archive"}
            and re.fullmatch(r"project-\d{4,}", path.name)
        ):
            register("Project", path.name, path)

    for namespace, identifiers in namespaces.items():
        for identifier, paths in identifiers.items():
            if len(paths) > 1:
                rendered = ", ".join(result.relative(path) for path in paths)
                result.errors.append(f"reused {namespace} ID {identifier}: {rendered}")


def count_recursive(root: Path, directory_name: str) -> int:
    count = len(visible_directories(root / directory_name))
    for child in visible_directories(root / "agencies"):
        count += count_recursive(child, directory_name)
    return count


def derived_status(root: Path) -> str:
    harness = (root / "harness.md").is_file()
    steward = (root / "steward.md").is_file()
    if not harness and not steward:
        return "first contact: harness check and Steward introduction pending"
    if harness and not steward:
        return "waiting for Steward introduction"
    if not harness and steward:
        return "harness check required before resuming"
    return "ready to resume"


def status(root: Path) -> int:
    agency = frontmatter(root / "AGENCY.md")
    managers = []
    for agent in visible_directories(root / "agents"):
        try:
            header = frontmatter(agent / "AGENTS.md")
        except FrontmatterError:
            continue
        if header.get("role") == "agency-manager":
            managers.append(header)
    version = (root / "VERSION").read_text(encoding="utf-8").strip() if (root / "VERSION").is_file() else "unknown"
    manager = managers[0].get("name") if len(managers) == 1 else "unresolved"
    print(f"JoEL {version}")
    print(f"Agency: {agency.get('name', 'unknown')} ({agency.get('id', 'unknown')})")
    print(f"Manager: {manager}")
    print(f"Status: {derived_status(root)}")
    print(f"Active Agents: {count_recursive(root, 'agents')}")
    print(f"Child Agencies: {count_recursive(root, 'agencies')}")
    print(f"Active Projects: {sum(len(visible_directories(path / 'workspace' / 'projects')) for path in [root, *all_child_agencies(root)])}")
    return 0


def all_child_agencies(root: Path) -> list[Path]:
    found: list[Path] = []
    for child in visible_directories(root / "agencies"):
        found.append(child)
        found.extend(all_child_agencies(child))
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect or validate a JoEL Agency")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Agency root (defaults to this distribution)")
    parser.add_argument("command", nargs="?", choices=("status", "validate"), default="status")
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        if args.command == "status":
            return status(root)
        result = validate(root)
    except (OSError, FrontmatterError) as exc:
        print(f"JoEL inspection failed: {exc}", file=sys.stderr)
        return 2
    if result.errors:
        print("JoEL validation failed:")
        for error in result.errors:
            print(f"- {error}")
        return 1
    print(
        f"JoEL {(root / 'VERSION').read_text(encoding='utf-8').strip()} is valid "
        f"({len(result.agency_ids)} Agency, {len(result.agent_ids)} Agent)."
    )
    for warning in result.warnings:
        print(f"Warning: {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
