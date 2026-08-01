#!/usr/bin/env python3
"""End-to-end tests for every JoEL 0.1.0 Blueprint."""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path


LIBRARY = Path(__file__).resolve().parents[1]
TOOL = LIBRARY / "tools" / "blueprints.py"
TOKEN = re.compile(r"\{\{[a-z][a-z0-9_]*\}\}")


def run(arguments: list[str], *, succeeds: bool = True) -> str:
    result = subprocess.run(
        [sys.executable, str(TOOL), *arguments],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if succeeds and result.returncode != 0:
        raise AssertionError(result.stdout)
    if not succeeds and result.returncode == 0:
        raise AssertionError(f"expected failure, got success:\n{result.stdout}")
    return result.stdout


def run_joel(root: Path, *arguments: str, succeeds: bool = True) -> str:
    result = subprocess.run(
        [sys.executable, str(root / "tools" / "joel.py"), "--root", str(root), *arguments],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if succeeds and result.returncode != 0:
        raise AssertionError(result.stdout)
    if not succeeds and result.returncode == 0:
        raise AssertionError(f"expected JoEL failure, got success:\n{result.stdout}")
    return result.stdout


def assert_no_tokens(path: Path) -> None:
    for candidate in path.rglob("*"):
        assert not TOKEN.search(str(candidate.relative_to(path))), candidate
        if candidate.is_file():
            try:
                content = candidate.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            assert not TOKEN.search(content), candidate


def materialize(kind: str, reference: str, target: Path, values: dict[str, str] | None = None) -> str:
    arguments = ["materialize", kind, reference, str(target)]
    for key, value in (values or {}).items():
        arguments.extend(("--set", f"{key}={value}"))
    return run(arguments)


def main() -> int:
    assert "5 Blueprints" in run(["validate"])
    catalog = run(["list"])
    for reference in (
        "joel@0.1.0",
        "generic@0.1.0",
        "agency-manager@0.1.0",
        "generalist@0.1.0",
        "developer@0.1.0",
    ):
        assert reference in catalog

    with tempfile.TemporaryDirectory(prefix="joel-blueprints-0.1.0-test-") as temporary:
        sandbox = Path(temporary)
        root = sandbox / "joel"
        materialize("agency", "joel@0.1.0", root)
        assert_no_tokens(root)
        assert not (root / "harness.md").exists()
        assert not (root / "steward.md").exists()
        assert "first contact" in run_joel(root, "status")
        assert "1 Agency, 1 Agent" in run_joel(root, "validate")

        smoke = subprocess.run(
            [sys.executable, str(root / "tools" / "test_joel.py")],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        if smoke.returncode != 0:
            raise AssertionError(smoke.stdout)

        child = root / "agencies" / "agency-0002"
        materialize(
            "agency",
            "generic@0.1.0",
            child,
            {
                "agency_id": "agency-0002",
                "agency_name": "Opportunity Research",
                "manager_id": "agent-0002",
                "manager_name": "Scout",
            },
        )
        assert_no_tokens(child)

        generalist = root / "agents" / "agent-0003"
        materialize(
            "agent",
            "generalist@0.1.0",
            generalist,
            {"agent_id": "agent-0003", "agent_name": "Researcher", "role": "researcher"},
        )
        developer = root / "agents" / "agent-0004"
        materialize(
            "agent",
            "developer@0.1.0",
            developer,
            {"agent_id": "agent-0004", "agent_name": "Developer"},
        )
        standalone_manager = sandbox / "agent-0005"
        materialize(
            "agent",
            "agency-manager@0.1.0",
            standalone_manager,
            {"agent_id": "agent-0005", "agent_name": "Manager"},
        )
        for path in (generalist, developer, standalone_manager):
            assert_no_tokens(path)

        recursive = run_joel(root, "validate")
        assert "2 Agency, 4 Agent" in recursive
        status = run_joel(root, "status")
        assert "Active Agents: 4" in status
        assert "Child Agencies: 1" in status

        existing = run(
            ["materialize", "agency", "joel@0.1.0", str(root)],
            succeeds=False,
        )
        assert "target already exists" in existing

        missing_target = sandbox / "missing-values"
        missing = run(
            ["materialize", "agency", "generic@0.1.0", str(missing_target)],
            succeeds=False,
        )
        assert "missing token" in missing
        assert not missing_target.exists()

        unpinned = run(
            ["materialize", "agent", "generalist", str(sandbox / "unpinned")],
            succeeds=False,
        )
        assert "must be exact" in unpinned

        invalid_id = run(
            [
                "materialize", "agent", "developer@0.1.0", str(sandbox / "bad-id"),
                "--set", "agent_id=developer", "--set", "agent_name=Developer",
            ],
            succeeds=False,
        )
        assert "agent_id must match" in invalid_id

    print("All JoEL Blueprint validation and materialization tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

