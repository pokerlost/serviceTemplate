"""Exercise rendered native CI and real isolated pytest acceptance boundaries."""

from __future__ import annotations

import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "foundationOverlay/docker/native_acceptance.py"


@pytest.mark.parametrize("persistence", [False, True])
@pytest.mark.parametrize("kubernetes", [False, True])
def test_rendered_native_gate_and_provider_boundary(
    tmp_path: Path, persistence: bool, kubernetes: bool
) -> None:
    output = tmp_path / "application"
    subprocess.run(
        [
            sys.executable,
            "-B",
            "-m",
            "copier",
            "copy",
            "--quiet",
            "--defaults",
            str(ROOT),
            str(output),
            "-d",
            "service_name=nativeService",
            "-d",
            f"withPersistence={str(persistence).lower()}",
            "-d",
            f"withKubernetes={str(kubernetes).lower()}",
        ],
        check=True,
        capture_output=True,
        timeout=60,
    )
    workflow_text = (output / ".github/workflows/ci.yml").read_text()
    assert all(line == line.rstrip() for line in workflow_text.splitlines())
    workflow = yaml.safe_load(workflow_text)
    jobs = workflow["jobs"]
    assert jobs["required"]["needs"] == ["source", "native"]
    native = jobs["native"]
    assert bool(native.get("services")) is persistence
    assert bool(jobs["release-builder"].get("services")) is persistence
    commands = "\n".join(step.get("run", "") for step in native["steps"])
    assert "make CONTAINERIZED=1 check" in commands
    assert "--no-install-project --no-editable" in commands
    assert "native_acceptance.py" in commands
    assert "--require-hashes" not in commands
    assert "kind create" not in commands
    assert "docker build" not in commands
    assert "id-token" not in native.get("permissions", {})
    allocation = jobs["release-allocation"]
    assert "github.event_name == 'push'" in allocation["if"]
    assert "github.ref_name == 'dev'" in allocation["if"]
    assert "github.ref_name == 'main'" in allocation["if"]
    provider = "e5cac33af228224af9deaef308e39c1b9f788033"
    assert allocation["uses"].endswith("@" + provider)
    publication = jobs["release-publication"]
    assert publication["uses"].endswith("@" + provider)
    assert "build-required == 'false'" in publication["if"]
    acceptance = json.loads((output / ".github/native-integration.json").read_text())
    assert len(acceptance) == (2 if persistence else 0)
    assert (output / "docker/native_acceptance.py").read_bytes() == (
        HELPER.read_bytes()
    )
    for job in jobs.values():
        for step in job.get("steps", []):
            if "run" in step:
                subprocess.run(["bash", "-n"], input=step["run"], text=True, check=True)


def run_acceptance(
    tmp_path: Path,
    integration: str,
    expected: list[str],
    *,
    persistence: bool = True,
) -> tuple[subprocess.CompletedProcess[str], Path, Path]:
    source = tmp_path / "source"
    source.mkdir()
    tests = source / "tests"
    tests.mkdir()
    (tests / "database_integration.py").write_text(integration)
    (tests / "test_native.py").write_text(
        "import os, sys\nfrom pathlib import Path\n"
        "def test_isolated_fixture():\n"
        "    assert sys.flags.isolated == 1\n"
        "    assert not Path('src').exists()\n"
        "    assert os.environ['TEST_INSTALLED_WHEEL'] == '1'\n"
        "    assert os.environ['TEST_EXACT_WHEEL'] == '1'\n"
        "    assert os.environ['EXPECTED_WHEEL_SHA256']\n"
    )
    (source / "pyproject.toml").write_text(
        '[project]\nname="native-fixture"\nversion="1.2.3.dev4"\n'
        '[tool.pytest.ini_options]\naddopts="--import-mode=importlib"\n'
    )
    (source / ".github").mkdir()
    (source / ".github/native-integration.json").write_text(json.dumps(expected))
    (source / "app_logging.json").write_text("{}\n")
    (source / "src").mkdir()
    (source / "src/checkout_only.py").write_text("raise RuntimeError\n")
    (source / "migrations").mkdir()
    (source / "migrations/env.py").write_text("# preserved migration fixture\n")
    (tests / "foundation").mkdir()
    (tests / "foundation/database_integration.py").write_text("# explicit fixture\n")
    (source / "alembic.ini").write_text("[alembic]\n")
    wheel = tmp_path / "native_fixture-1.2.3.dev4-py3-none-any.whl"
    wheel.write_bytes(b"synthetic orchestration fixture, not a package proof")
    output, report = tmp_path / "installed", tmp_path / "report"
    result = subprocess.run(
        [
            sys.executable,
            "-I",
            "-B",
            str(HELPER),
            "installed",
            "--source",
            str(source),
            "--fixture",
            str(output),
            "--report",
            str(report),
            "--python",
            sys.executable,
            "--wheel",
            str(wheel),
            *(["--persistence"] if persistence else []),
        ],
        env={**os.environ, "TEST_DATABASE_URL": "synthetic-not-opened"},
        text=True,
        capture_output=True,
        timeout=60,
        check=False,
    )
    return result, output, report


def test_actual_pytest_collection_and_exact_junit(tmp_path: Path) -> None:
    node = "tests/database_integration.py::test_existing_database_case"
    result, output, report = run_acceptance(
        tmp_path, "def test_existing_database_case():\n    assert True\n", [node]
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert not (output / "src").exists()
    assert (output / "migrations/env.py").read_text().startswith("# preserved")
    assert (report / "integration.xml").is_file()
    assert (report / "junit.xml").is_file()


@pytest.mark.parametrize(
    "body,expected",
    [
        (
            "def test_extra():\n    pass\n",
            ["tests/database_integration.py::test_missing"],
        ),
        ("def test_extra():\n    pass\n", []),
        (
            "import pytest\ndef test_skipped():\n    pytest.skip('synthetic')\n",
            ["tests/database_integration.py::test_skipped"],
        ),
        (
            "def test_failed():\n    assert False\n",
            ["tests/database_integration.py::test_failed"],
        ),
    ],
)
def test_empty_missing_skipped_or_failed_database_never_passes(
    tmp_path: Path, body: str, expected: list[str]
) -> None:
    result, _, report = run_acceptance(tmp_path, body, expected)
    assert result.returncode != 0
    assert not (report / "junit.xml").exists()


def test_source_uses_existing_junit_and_rejects_stale_cases(tmp_path: Path) -> None:
    node = "tests/database_integration.py::test_existing_database_case"
    result, _, report = run_acceptance(
        tmp_path,
        "from pathlib import Path\n"
        "def test_existing_database_case():\n    Path('db-executed').touch()\n",
        [node],
    )
    assert result.returncode == 0, result.stdout + result.stderr
    source = tmp_path / "source"
    command = [
        sys.executable,
        "-I",
        "-B",
        str(HELPER),
        "source",
        "--source",
        str(source),
        "--report",
        str(report),
        "--python",
        sys.executable,
        "--persistence",
    ]
    passed = subprocess.run(command, capture_output=True, text=True, check=False)
    assert passed.returncode == 0, passed.stdout + passed.stderr
    assert not (source / "db-executed").exists()
    xml = report / "integration.xml"
    tree = ET.parse(xml)
    case = next(tree.getroot().iter("testcase"))
    case.set("name", "stale_unreviewed_case")
    tree.write(xml)
    rejected = subprocess.run(command, capture_output=True, text=True, check=False)
    assert rejected.returncode != 0
    assert "JUnit cases differ" in rejected.stderr


@pytest.mark.parametrize("defect", ["duplicate", "missing-resource", "symlink"])
def test_invalid_manifest_or_resources_fail_closed(tmp_path: Path, defect: str) -> None:
    node = "tests/database_integration.py::test_existing_database_case"
    result, _, _ = run_acceptance(
        tmp_path, "def test_existing_database_case():\n    pass\n", [node]
    )
    assert result.returncode == 0, result.stdout + result.stderr
    source = tmp_path / "source"
    if defect == "duplicate":
        (source / ".github/native-integration.json").write_text(
            json.dumps([node, node])
        )
    elif defect == "missing-resource":
        (source / "app_logging.json").unlink()
    else:
        (source / "scripts").mkdir()
        (source / "scripts/escape.py").symlink_to(tmp_path / "outside.py")
    command = list(result.args)
    command[command.index("--fixture") + 1] = str(tmp_path / "second-fixture")
    command[command.index("--report") + 1] = str(tmp_path / "second-report")
    rejected = subprocess.run(command, capture_output=True, text=True, check=False)
    assert rejected.returncode != 0
    assert "ValueError" in rejected.stderr


@pytest.mark.parametrize("owner_count", [6, 7])
def test_real_update_preserves_owner_integration_manifest(
    tmp_path: Path, owner_count: int
) -> None:
    source = tmp_path / "template"
    source.mkdir()
    archive = subprocess.check_output(
        [
            "git",
            "-C",
            str(ROOT),
            "archive",
            "599e7573a7f86fae277bef300af5b373252906e5",
            "copier.yml",
            "composedTemplate",
        ]
    )
    with tarfile.open(fileobj=io.BytesIO(archive)) as bundle:
        bundle.extractall(source, filter="data")

    def git(root: Path, *args: str) -> str:
        return subprocess.check_output(
            ["git", "-C", str(root), *args], text=True
        ).strip()

    def commit(root: Path, message: str) -> str:
        git(root, "add", ".")
        git(
            root,
            "-c",
            "user.name=Native Fixture",
            "-c",
            "user.email=native@example.invalid",
            "commit",
            "--quiet",
            "-m",
            message,
        )
        return git(root, "rev-parse", "HEAD")

    git(source, "init", "--quiet")
    first = commit(source, "initial native source fixture")
    output = tmp_path / "application"
    copier = [sys.executable, "-B", "-m", "copier"]
    subprocess.run(
        [
            *copier,
            "copy",
            "--quiet",
            "--defaults",
            f"--vcs-ref={first}",
            str(source),
            str(output),
            "-d",
            "service_name=nativeService",
            "-d",
            "withPersistence=true",
            "-d",
            "withKubernetes=true",
        ],
        capture_output=True,
        check=True,
        timeout=60,
    )
    git(output, "init", "--quiet")
    expected = [
        "tests/foundation/database_integration.py::test_real_readiness_and_transaction_ownership",
        "tests/database_integration.py::test_real_database_readiness",
        *[
            f"tests/migrations_integration.py::test_owner_case_{i}"
            for i in range(owner_count - 2)
        ],
    ]
    manifest = output / ".github/native-integration.json"
    manifest.write_text(json.dumps(expected, indent=2) + "\n")
    owner = output / "migrations/versions/owner.py"
    owner.write_text('"""Existing owner revision."""\n')
    before = {str(p.relative_to(output)): p.read_bytes() for p in (manifest, owner)}
    commit(output, "preserve reviewed owner integration identities")
    shutil.copy2(ROOT / "copier.yml", source / "copier.yml")
    shutil.rmtree(source / "composedTemplate")
    shutil.copytree(ROOT / "composedTemplate", source / "composedTemplate")
    managed = source / "composedTemplate/docker/native_acceptance.py"
    managed.write_text(managed.read_text() + "\n# reviewed fixture update\n")
    second = commit(source, "update native technical helper fixture")
    for index in range(2):
        subprocess.run(
            [*copier, "update", "--quiet", "--defaults", f"--vcs-ref={second}"],
            cwd=output,
            capture_output=True,
            check=True,
            timeout=60,
        )
        assert all(
            (output / name).read_bytes() == data for name, data in before.items()
        )
        assert not git(output, "ls-files", "-u")
        if index == 0:
            commit(output, "accept managed helper update fixture")
        else:
            assert not git(output, "status", "--porcelain")
