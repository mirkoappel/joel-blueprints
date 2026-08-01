#!/usr/bin/env python3
"""List, validate, and safely materialize JoEL Blueprints."""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
KINDS = {"agency": "agencies", "agent": "agents", "skill": "skills"}
SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$"
)
NAME = re.compile(r"^[a-z][a-z0-9-]*$")
TOKEN = re.compile(r"\{\{([a-z][a-z0-9_]*)\}\}")
AGENCY_ID = re.compile(r"^agency-\d{4,}$")
AGENT_ID = re.compile(r"^agent-\d{4,}$")
ROLE = re.compile(r"^[a-z][a-z0-9-]*$")
IGNORED = {"__pycache__", ".DS_Store"}
DEFAULT_VALUES = {("agent", "generalist"): {"role": "generalist"}}


class BlueprintError(ValueError):
    pass


@dataclass(frozen=True)
class Blueprint:
    kind: str
    name: str
    version: str
    path: Path

    @property
    def reference(self) -> str:
        return f"{self.name}@{self.version}"


def scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def frontmatter(path: Path) -> dict[str, str]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        raise BlueprintError(f"cannot read {path}: {exc}") from exc
    if not lines or lines[0].strip() != "---":
        raise BlueprintError(f"missing opening frontmatter delimiter in {path}")
    try:
        end = next(index for index, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration as exc:
        raise BlueprintError(f"missing closing frontmatter delimiter in {path}") from exc
    result: dict[str, str] = {}
    for number, line in enumerate(lines[1:end], 2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line[:1].isspace() or ":" not in line:
            raise BlueprintError(f"non-flat frontmatter at {path}:{number}")
        key, value = line.split(":", 1)
        key = key.strip()
        if not re.fullmatch(r"[a-z][a-z0-9_-]*", key):
            raise BlueprintError(f"invalid frontmatter key {key!r} at {path}:{number}")
        if key in result:
            raise BlueprintError(f"duplicate frontmatter key {key!r} in {path}")
        result[key] = scalar(value)
    return result


def ignored(path: Path) -> bool:
    return path.name in IGNORED or path.suffix in {".pyc", ".pyo"}


def blueprint_files(path: Path) -> list[Path]:
    files: list[Path] = []
    for candidate in sorted(path.rglob("*")):
        if any(ignored(parent) for parent in (candidate, *candidate.parents) if parent != path.parent):
            continue
        if candidate.is_symlink():
            raise BlueprintError(f"symlinks are not portable Blueprint content: {candidate}")
        if candidate.is_file():
            files.append(candidate)
    return files


def text(path: Path) -> str | None:
    data = path.read_bytes()
    if b"\0" in data:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def tokens_in(blueprint: Blueprint) -> set[str]:
    found: set[str] = set()
    for candidate in blueprint.path.rglob("*"):
        if ignored(candidate):
            continue
        found.update(TOKEN.findall(str(candidate.relative_to(blueprint.path))))
        if candidate.is_file():
            content = text(candidate)
            if content is not None:
                found.update(TOKEN.findall(content))
    return found


def discover(root: Path) -> list[Blueprint]:
    found: list[Blueprint] = []
    for kind, plural in KINDS.items():
        category = root / plural
        if not category.is_dir():
            continue
        for name_path in sorted(item for item in category.iterdir() if item.is_dir()):
            if not NAME.fullmatch(name_path.name):
                continue
            for version_path in sorted(item for item in name_path.iterdir() if item.is_dir()):
                if SEMVER.fullmatch(version_path.name):
                    found.append(Blueprint(kind, name_path.name, version_path.name, version_path))
    return found


def resolve_blueprint(root: Path, kind: str, reference: str) -> Blueprint:
    if reference.count("@") != 1:
        raise BlueprintError("Blueprint reference must be exact: <name>@<semantic-version>")
    name, version = reference.split("@", 1)
    if not NAME.fullmatch(name) or not SEMVER.fullmatch(version):
        raise BlueprintError(f"invalid pinned Blueprint reference: {reference}")
    path = root / KINDS[kind] / name / version
    if not path.is_dir():
        raise BlueprintError(f"Blueprint not found: {kind} {reference}")
    return Blueprint(kind, name, version, path)


def require(path: Path, *, directory: bool, errors: list[str], root: Path) -> None:
    exists = path.is_dir() if directory else path.is_file()
    if not exists:
        noun = "directory" if directory else "file"
        errors.append(f"missing {noun}: {path.relative_to(root)}")


def validate_agent_shape(
    blueprint: Blueprint, errors: list[str], *, published_agent: bool = True
) -> None:
    root = blueprint.path
    for name in ("AGENTS.md", "CLAUDE.md"):
        require(root / name, directory=False, errors=errors, root=root)
    for name in ("assignments", "workbench", "memory", "adaptations", "handoff"):
        require(root / name, directory=True, errors=errors, root=root)
    if (root / "CLAUDE.md").is_file() and (root / "CLAUDE.md").read_text(encoding="utf-8").strip() != "@AGENTS.md":
        errors.append(f"{blueprint.kind} {blueprint.reference}: CLAUDE.md must contain only @AGENTS.md")
    if not (root / "AGENTS.md").is_file():
        return
    try:
        header = frontmatter(root / "AGENTS.md")
    except BlueprintError as exc:
        errors.append(str(exc))
        return
    if header.get("kind") != "agent":
        errors.append(f"{blueprint.kind} {blueprint.reference}: AGENTS.md kind must be 'agent'")
    if published_agent:
        expected = {"version": blueprint.version, "blueprint": blueprint.reference}
        for key, value in expected.items():
            if header.get(key) != value:
                errors.append(f"{blueprint.kind} {blueprint.reference}: AGENTS.md {key} must be {value!r}")
    else:
        if not SEMVER.fullmatch(header.get("version", "")):
            errors.append(f"embedded Agent in {blueprint.reference}: invalid version")
        origin = header.get("blueprint", "")
        if origin.count("@") != 1:
            errors.append(f"embedded Agent in {blueprint.reference}: Blueprint reference is not pinned")
        else:
            origin_name, origin_version = origin.split("@", 1)
            if not NAME.fullmatch(origin_name) or not SEMVER.fullmatch(origin_version):
                errors.append(f"embedded Agent in {blueprint.reference}: invalid Blueprint reference")
        if header.get("id") != root.name:
            errors.append(f"embedded Agent folder and ID differ in {blueprint.reference}")
    for key in ("id", "name", "role"):
        if not header.get(key):
            errors.append(f"{blueprint.kind} {blueprint.reference}: AGENTS.md lacks {key}")


def validate_agency_shape(blueprint: Blueprint, errors: list[str]) -> None:
    root = blueprint.path
    for name in ("AGENTS.md", "CLAUDE.md", "AGENCY.md"):
        require(root / name, directory=False, errors=errors, root=root)
    for name in (
        "agents", "agencies", "knowledge", "workspace/projects", "workspace/shared",
        "archive/projects", "archive/agents", "archive/agencies",
    ):
        require(root / name, directory=True, errors=errors, root=root)
    if (root / "CLAUDE.md").is_file() and (root / "CLAUDE.md").read_text(encoding="utf-8").strip() != "@AGENTS.md":
        errors.append(f"agency {blueprint.reference}: CLAUDE.md must contain only @AGENTS.md")
    if (root / "AGENCY.md").is_file():
        try:
            header = frontmatter(root / "AGENCY.md")
        except BlueprintError as exc:
            errors.append(str(exc))
            header = {}
        expected = {"kind": "agency", "version": blueprint.version, "blueprint": blueprint.reference}
        for key, value in expected.items():
            if header.get(key) != value:
                errors.append(f"agency {blueprint.reference}: AGENCY.md {key} must be {value!r}")
        for key in ("id", "name"):
            if not header.get(key):
                errors.append(f"agency {blueprint.reference}: AGENCY.md lacks {key}")
    else:
        header = {}
    if (root / "AGENTS.md").is_file():
        try:
            boot = frontmatter(root / "AGENTS.md")
        except BlueprintError as exc:
            errors.append(str(exc))
            boot = {}
        if boot.get("kind") != "agency-bootloader" or boot.get("version") != blueprint.version:
            errors.append(f"agency {blueprint.reference}: invalid bootloader kind or version")
        if header and boot.get("agency") != header.get("id"):
            errors.append(f"agency {blueprint.reference}: bootloader points at the wrong Agency")
    managers = 0
    agents_root = root / "agents"
    if agents_root.is_dir():
        for agent in sorted(item for item in agents_root.iterdir() if item.is_dir() and not ignored(item)):
            nested = Blueprint("agent", blueprint.name, blueprint.version, agent)
            validate_agent_shape(nested, errors, published_agent=False)
            if (agent / "AGENTS.md").is_file():
                try:
                    if frontmatter(agent / "AGENTS.md").get("role") == "agency-manager":
                        managers += 1
                except BlueprintError:
                    pass
    if managers != 1:
        errors.append(f"agency {blueprint.reference}: expected one Agency Manager, found {managers}")


def validate_skill_shape(blueprint: Blueprint, errors: list[str]) -> None:
    require(blueprint.path / "SKILL.md", directory=False, errors=errors, root=blueprint.path)


def validate_library(root: Path) -> list[str]:
    errors: list[str] = []
    for name in ("AGENTS.md", "CLAUDE.md", "README.md", "VERSION", "CHANGELOG.md"):
        require(root / name, directory=False, errors=errors, root=root)
    for name in KINDS.values():
        require(root / name, directory=True, errors=errors, root=root)
        category = root / name
        if category.is_dir():
            for blueprint_name in sorted(item for item in category.iterdir() if item.is_dir()):
                if not NAME.fullmatch(blueprint_name.name):
                    errors.append(f"invalid Blueprint name directory: {blueprint_name.relative_to(root)}")
                    continue
                for version in sorted(item for item in blueprint_name.iterdir() if item.is_dir()):
                    if not SEMVER.fullmatch(version.name):
                        errors.append(f"invalid Blueprint version directory: {version.relative_to(root)}")
    package_version = ""
    if (root / "VERSION").is_file():
        package_version = (root / "VERSION").read_text(encoding="utf-8").strip()
        if not SEMVER.fullmatch(package_version):
            errors.append("VERSION is not a semantic version")
    if (root / "CLAUDE.md").is_file() and (root / "CLAUDE.md").read_text(encoding="utf-8").strip() != "@AGENTS.md":
        errors.append("root CLAUDE.md must contain only @AGENTS.md")
    if (root / "AGENTS.md").is_file():
        try:
            header = frontmatter(root / "AGENTS.md")
            if header.get("kind") != "blueprint-library":
                errors.append("root AGENTS.md kind must be blueprint-library")
            if package_version and header.get("version") != package_version:
                errors.append("root AGENTS.md version and VERSION differ")
        except BlueprintError as exc:
            errors.append(str(exc))
    blueprints = discover(root)
    references: set[tuple[str, str]] = set()
    for blueprint in blueprints:
        key = (blueprint.kind, blueprint.reference)
        if key in references:
            errors.append(f"duplicate Blueprint: {blueprint.kind} {blueprint.reference}")
        references.add(key)
        try:
            blueprint_files(blueprint.path)
        except BlueprintError as exc:
            errors.append(str(exc))
        if blueprint.kind == "agency":
            validate_agency_shape(blueprint, errors)
        elif blueprint.kind == "agent":
            validate_agent_shape(blueprint, errors)
        else:
            validate_skill_shape(blueprint, errors)
    available = {
        kind: {blueprint.reference for blueprint in blueprints if blueprint.kind == kind}
        for kind in KINDS
    }
    for blueprint in (item for item in blueprints if item.kind == "agency"):
        descriptors = [("agency", blueprint.path / "AGENCY.md")]
        agents_root = blueprint.path / "agents"
        if agents_root.is_dir():
            descriptors.extend(
                ("agent", agent / "AGENTS.md")
                for agent in agents_root.iterdir()
                if agent.is_dir() and not ignored(agent)
            )
        for origin_kind, descriptor in descriptors:
            if not descriptor.is_file():
                continue
            try:
                origin = frontmatter(descriptor).get("blueprint", "")
            except BlueprintError:
                continue
            if origin not in available[origin_kind]:
                errors.append(
                    f"dangling {origin_kind} Blueprint origin {origin!r} in "
                    f"{descriptor.relative_to(root)}"
                )
    if not blueprints:
        errors.append("Library contains no versioned Blueprints")
    return errors


def parse_values(items: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in items:
        if "=" not in item:
            raise BlueprintError(f"--set value must be key=value: {item!r}")
        key, value = item.split("=", 1)
        if not re.fullmatch(r"[a-z][a-z0-9_]*", key):
            raise BlueprintError(f"invalid token name: {key!r}")
        if key in result:
            raise BlueprintError(f"token supplied more than once: {key}")
        if not value.strip() or any(character in value for character in "\r\n\0"):
            raise BlueprintError(f"token {key} must be a non-empty single-line value")
        if "{{" in value or "}}" in value or "/" in value or "\\" in value:
            raise BlueprintError(f"token {key} contains reserved path or template characters")
        result[key] = value
    return result


def validate_token_values(values: dict[str, str]) -> None:
    for key, value in values.items():
        if key == "agency_id" and not AGENCY_ID.fullmatch(value):
            raise BlueprintError("agency_id must match agency-0001 or a longer numeric suffix")
        if key in {"agent_id", "manager_id"} and not AGENT_ID.fullmatch(value):
            raise BlueprintError(f"{key} must match agent-0001 or a longer numeric suffix")
        if key == "role" and not ROLE.fullmatch(value):
            raise BlueprintError("role must be a lowercase hyphenated identifier")


def render(value: str, replacements: dict[str, str]) -> str:
    return TOKEN.sub(lambda match: replacements[match.group(1)], value)


def materialize(blueprint: Blueprint, target: Path, supplied: dict[str, str], library_root: Path) -> None:
    required = tokens_in(blueprint)
    replacements = dict(DEFAULT_VALUES.get((blueprint.kind, blueprint.name), {}))
    replacements.update(supplied)
    unknown = set(replacements) - required
    missing = required - set(replacements)
    if unknown:
        raise BlueprintError(f"unknown token(s) for {blueprint.reference}: {', '.join(sorted(unknown))}")
    if missing:
        raise BlueprintError(f"missing token(s) for {blueprint.reference}: {', '.join(sorted(missing))}")
    validate_token_values(replacements)

    target = target.expanduser().resolve()
    library_root = library_root.resolve()
    if target.exists():
        raise BlueprintError(f"target already exists: {target}")
    if target == library_root or library_root in target.parents:
        raise BlueprintError("materialization target must be outside the Blueprint Library")

    target.parent.mkdir(parents=True, exist_ok=True)
    target.mkdir()
    try:
        for source in sorted(blueprint.path.rglob("*")):
            if any(ignored(part) for part in (source, *source.parents) if part != blueprint.path.parent):
                continue
            relative = source.relative_to(blueprint.path)
            rendered_parts = [render(part, replacements) for part in relative.parts]
            destination = target.joinpath(*rendered_parts)
            if source.is_symlink():
                raise BlueprintError(f"refusing Blueprint symlink: {relative}")
            if source.is_dir():
                destination.mkdir(parents=True, exist_ok=True)
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            content = text(source)
            if content is None:
                shutil.copy2(source, destination)
            else:
                destination.write_text(render(content, replacements), encoding="utf-8")
                shutil.copymode(source, destination)
        unresolved: list[str] = []
        for candidate in target.rglob("*"):
            if TOKEN.search(str(candidate.relative_to(target))):
                unresolved.append(str(candidate.relative_to(target)))
            if candidate.is_file():
                content = text(candidate)
                if content is not None and TOKEN.search(content):
                    unresolved.append(str(candidate.relative_to(target)))
        if unresolved:
            raise BlueprintError(f"unresolved token after materialization: {unresolved[0]}")
    except Exception:
        shutil.rmtree(target)
        raise


def command_list(root: Path) -> int:
    blueprints = discover(root)
    print("KIND    REFERENCE")
    for blueprint in blueprints:
        print(f"{blueprint.kind:<7} {blueprint.reference}")
    return 0


def command_validate(root: Path) -> int:
    errors = validate_library(root)
    if errors:
        print("Blueprint Library validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    blueprints = discover(root)
    print(f"JoEL Blueprint Library {(root / 'VERSION').read_text(encoding='utf-8').strip()} is valid ({len(blueprints)} Blueprints).")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="JoEL Blueprint Library tools")
    parser.add_argument("--library-root", type=Path, default=DEFAULT_ROOT)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="list exact pinned Blueprint references")
    commands.add_parser("validate", help="validate the Library structure and contracts")
    materializer = commands.add_parser("materialize", help="materialize a Blueprint into a new target")
    materializer.add_argument("kind", choices=tuple(KINDS))
    materializer.add_argument("reference")
    materializer.add_argument("target", type=Path)
    materializer.add_argument("--set", action="append", default=[], metavar="KEY=VALUE")
    args = parser.parse_args()
    root = args.library_root.resolve()
    try:
        if args.command == "list":
            return command_list(root)
        if args.command == "validate":
            return command_validate(root)
        blueprint = resolve_blueprint(root, args.kind, args.reference)
        values = parse_values(args.set)
        materialize(blueprint, args.target, values, root)
        print(f"Materialized {args.kind} {blueprint.reference} at {args.target.resolve()}")
        return 0
    except (BlueprintError, OSError) as exc:
        print(f"Blueprint operation failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
