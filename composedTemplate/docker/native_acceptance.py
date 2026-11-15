"""Bind existing pytest collection and JUnit to isolated installed resources."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import xml.etree.ElementTree as ET
from collections import Counter
from enum import StrEnum
from pathlib import Path
from typing import Annotated, cast

import typer

app = typer.Typer(
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
    pretty_exceptions_show_locals=False,
)
MANIFEST = ".github/native-integration.json"


class Mode(StrEnum):
    """Select the existing source or installed pytest boundary."""

    SOURCE = "source"
    INSTALLED = "installed"


def require(condition: object, message: str) -> None:
    if not condition:
        raise ValueError(message)


def integration_nodes(source: Path, persistence: bool) -> list[str]:
    manifest = source / MANIFEST
    require(
        not manifest.is_symlink() and manifest.resolve().is_relative_to(source),
        "Integration manifest must be a regular source file",
    )
    nodes = json.loads(manifest.read_text())
    require(isinstance(nodes, list), "Integration manifest must be a JSON array")
    require(
        all(isinstance(node, str) and "::" in node for node in nodes),
        "Integration manifest requires explicit pytest node IDs",
    )
    require(len(nodes) == len(set(nodes)), "Duplicate integration node ID")
    require(bool(nodes) is persistence, "Integration manifest/profile mismatch")
    for node in nodes:
        path = Path(node.split("::", 1)[0])
        require(
            not path.is_absolute()
            and ".." not in path.parts
            and path.parts[0] == "tests"
            and not any(char in node for char in "\r\n\0")
            and (source / path).is_file(),
            "Invalid integration node path",
        )
    if persistence:
        require(
            (source / "tests/foundation/database_integration.py").is_file(),
            "Persistent profile requires foundation database acceptance",
        )
    return list(nodes)


def junit(path: Path, nodes: list[str] | None = None) -> None:
    root = ET.parse(path).getroot()
    suites = list(root.iter("testsuite"))
    require(suites, "Missing JUnit suites")
    for key in ("failures", "errors", "skipped"):
        require(
            sum(int(suite.get(key, "0")) for suite in suites) == 0,
            "JUnit has failures, errors or skipped tests",
        )
    cases = list(root.iter("testcase"))
    require(cases, "Empty JUnit acceptance")
    require(
        sum(int(suite.get("tests", "0")) for suite in suites) == len(cases),
        "JUnit test count mismatch",
    )
    if nodes is not None:
        expected = Counter(
            (
                ".".join([parts[0][:-3].replace("/", "."), *parts[1:-1]]),
                parts[-1],
            )
            for parts in (node.split("::") for node in nodes)
        )
        actual = Counter((case.get("classname"), case.get("name")) for case in cases)
        require(actual == expected, "JUnit cases differ from reviewed integration IDs")


def copy_fixture(source: Path, target: Path, persistence: bool) -> None:
    require(not target.exists(), "Installed fixture must be new")
    require(not target.is_relative_to(source), "Fixture must be outside source")
    required = ["tests", "pyproject.toml", "app_logging.json", MANIFEST]
    if persistence:
        required += ["alembic.ini", "migrations"]
    require(
        all((source / name).exists() for name in required), "Missing test resources"
    )
    target.mkdir(parents=True)
    for name in [*required, "scripts"]:
        entry = source / name
        if not entry.exists():
            continue
        paths = [entry, *entry.rglob("*")] if entry.is_dir() else [entry]
        for path in paths:
            require(not path.is_symlink(), "Symlink in installed test resources")
            require(path.is_file() or path.is_dir(), "Special installed resource")
            if (
                path.is_file()
                and "__pycache__" not in path.parts
                and path.suffix != ".pyc"
            ):
                destination = target / path.relative_to(source)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, destination)
                require(
                    destination.read_bytes() == path.read_bytes(),
                    "Resource copy differs",
                )


@app.command("native-acceptance")
def main(
    mode: Annotated[Mode, typer.Argument(help="Existing pytest acceptance mode.")],
    source: Annotated[Path, typer.Option("--source")],
    python: Annotated[Path, typer.Option("--python")],
    report: Annotated[Path, typer.Option("--report")],
    fixture: Annotated[Path | None, typer.Option("--fixture")] = None,
    wheel: Annotated[Path | None, typer.Option("--wheel")] = None,
    persistence: Annotated[bool, typer.Option("--persistence")] = False,
) -> None:
    source, report = source.resolve(), report.resolve()
    nodes = integration_nodes(source, persistence)
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    if mode == "installed":
        require(fixture is not None and wheel is not None, "Missing wheel/fixture")
        fixture, wheel = cast(Path, fixture), cast(Path, wheel)
        source_fixture = fixture.resolve()
        require(not report.exists(), "Installed reports must be new")
        require(not report.is_relative_to(source), "Reports must be outside source")
        copy_fixture(source, source_fixture, persistence)
        report.mkdir(parents=True)
        require(wheel.is_file() and not wheel.is_symlink(), "Invalid wheel file")
        wheel = wheel.resolve(strict=True)
        env.update(
            TEST_INSTALLED_WHEEL="1",
            TEST_EXACT_WHEEL="1",
            EXPECTED_WHEEL_PATH=str(wheel),
            EXPECTED_WHEEL_SHA256=hashlib.sha256(wheel.read_bytes()).hexdigest(),
        )
        source = source_fixture
    command = [str(python), "-I", "-B", "-m", "pytest"]
    command += ["-q", "-p", "no:cacheprovider"]
    if persistence:
        files = sorted(
            {"tests/foundation/database_integration.py"}
            | {
                str(path.relative_to(source))
                for path in (source / "tests").glob("*_integration.py")
            }
            | {node.split("::", 1)[0] for node in nodes}
        )
        collected = subprocess.run(
            [*command, "--collect-only", *files],
            cwd=source,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        print(collected.stdout, end="")
        require(collected.returncode == 0, "Integration collection failed")
        actual = [
            line
            for line in collected.stdout.splitlines()
            if line.startswith("tests/") and "::" in line
        ]
        require(
            Counter(actual) == Counter(nodes),
            "Integration collection differs from reviewed IDs",
        )
        if mode == "installed":
            subprocess.run(
                [*command, "--junitxml=" + str(report / "integration.xml"), *files],
                cwd=source,
                env=env,
                check=True,
            )
        junit(report / "integration.xml", nodes)
    if mode == "installed":
        subprocess.run(
            [*command, "--junitxml=" + str(report / "junit.xml")],
            cwd=source,
            env=env,
            check=True,
        )
    junit(report / "junit.xml")


if __name__ == "__main__":
    app()
