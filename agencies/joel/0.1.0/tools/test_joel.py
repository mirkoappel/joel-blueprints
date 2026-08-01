#!/usr/bin/env python3
"""Smoke tests for a fresh and recursively extended JoEL Agency."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1]


def run(root: Path, command: str, *, succeeds: bool = True) -> str:
    result = subprocess.run(
        [sys.executable, str(root / "tools" / "joel.py"), "--root", str(root), command],
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


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")


def create_child_agency(parent: Path) -> Path:
    child = parent / "agencies" / "agency-0002"
    manager = child / "agents" / "agent-0002"
    for path in (
        child / "agencies",
        child / "knowledge",
        child / "workspace" / "projects",
        child / "workspace" / "shared",
        child / "archive" / "projects",
        child / "archive" / "agents",
        child / "archive" / "agencies",
        manager / "assignments",
        manager / "workbench",
        manager / "memory",
        manager / "adaptations",
        manager / "handoff",
    ):
        path.mkdir(parents=True, exist_ok=True)
    write(
        child / "AGENTS.md",
        """
        ---
        kind: agency-bootloader
        system: JoEL
        version: 0.1.0
        agency: agency-0002
        ---

        # Child bootloader

        Read `AGENCY.md`, then load the one Agency Manager in `agents/`.
        """,
    )
    write(child / "CLAUDE.md", "@AGENTS.md\n")
    write(
        child / "AGENCY.md",
        """
        ---
        kind: agency
        id: agency-0002
        name: Test Agency
        version: 0.1.0
        blueprint: generic@0.1.0
        ---

        # Test Agency
        """,
    )
    write(
        manager / "AGENTS.md",
        """
        ---
        kind: agent
        id: agent-0002
        name: Test Manager
        role: agency-manager
        version: 0.1.0
        blueprint: agency-manager@0.1.0
        ---

        # Test Manager
        """,
    )
    write(manager / "CLAUDE.md", "@AGENTS.md\n")
    return child


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="joel-0.1.0-test-") as temporary:
        root = Path(temporary) / "joel"
        shutil.copytree(SOURCE, root, ignore=shutil.ignore_patterns("__pycache__"))

        run(root, "validate")
        initial = run(root, "status")
        assert "first contact" in initial
        assert "Active Agents: 1" in initial
        assert "Child Agencies: 0" in initial

        write(
            root / "harness.md",
            """
            ---
            kind: harness-profile
            version: 0.1.0
            harness: test
            ---

            # Harness profile

            Test-only observation.
            """,
        )
        waiting = run(root, "status")
        assert "waiting for Steward" in waiting

        write(
            root / "steward.md",
            """
            ---
            kind: steward
            version: 0.1.0
            name: Test Steward
            address_as: Steward
            ---

            # Steward
            """,
        )
        ready = run(root, "status")
        assert "ready to resume" in ready

        project = root / "workspace" / "projects" / "project-0001"
        write(
            project / "PROJECT.md",
            """
            ---
            kind: project
            id: project-0001
            name: Smoke Test
            version: 0.1.0
            ---

            # Smoke Test

            ## Exact next action

            Validate recursion.
            """,
        )
        create_child_agency(root)
        recursive = run(root, "validate")
        assert "2 Agency" in recursive
        status_output = run(root, "status")
        assert "Active Agents: 2" in status_output
        assert "Child Agencies: 1" in status_output
        assert "Active Projects: 1" in status_output

        reused_agent = root / "archive" / "agents" / "agent-0002"
        reused_agent.mkdir()
        duplicate = run(root, "validate", succeeds=False)
        assert "reused Agent ID agent-0002" in duplicate
        reused_agent.rmdir()

        reused_project = root / "archive" / "projects" / "project-0001"
        reused_project.mkdir()
        duplicate = run(root, "validate", succeeds=False)
        assert "reused Project ID project-0001" in duplicate
        reused_project.rmdir()

        agency_document = root / "agencies" / "agency-0002" / "AGENCY.md"
        original_agency_document = agency_document.read_text(encoding="utf-8")
        agency_document.write_text(
            original_agency_document.replace("blueprint: generic@0.1.0", "blueprint: generic"),
            encoding="utf-8",
        )
        unpinned = run(root, "validate", succeeds=False)
        assert "invalid Agency Blueprint reference" in unpinned
        agency_document.write_text(original_agency_document, encoding="utf-8")

        write(root / "identity.json", "{}\n")
        run(root, "validate", succeeds=False)
        (root / "identity.json").unlink()

        (root / "agencies" / "agency-0002" / "agents" / "agent-0002" / "AGENTS.md").unlink()
        run(root, "validate", succeeds=False)

    print("JoEL fresh-start and recursive Agency smoke tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
