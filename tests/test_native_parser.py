"""Keep the native helper's Typer CLI compatible and noninteractive."""

from __future__ import annotations

import os
import runpy
import subprocess
import sys
from pathlib import Path

import pytest
import typer
from typer.testing import CliRunner

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "foundationOverlay/docker/native_acceptance.py"


@pytest.mark.parametrize("help_flag", ["--help", "-h"])
def test_typer_help_needs_no_source_and_has_no_completion_setup(
    help_flag: str,
) -> None:
    namespace = runpy.run_path(str(HELPER), run_name="native_acceptance_cli_test")
    app = namespace.get("app")
    assert isinstance(app, typer.Typer)
    result = CliRunner().invoke(app, [help_flag])
    assert result.exit_code == 0, result.output
    for name in ("source", "installed", "--python", "--report", "--persistence"):
        assert name in result.output
    assert "--install-completion" not in result.output


@pytest.mark.parametrize(
    "arguments",
    [
        [],
        ["unknown"],
        ["source", "--unexpected"],
        ["source", "--python", "python", "--report", "reports"],
        ["source", "--source", "missing", "--report", "reports"],
        ["installed", "--source", "missing", "--python", "python"],
    ],
)
def test_invalid_or_missing_arguments_exit_two_without_reading_source(
    tmp_path: Path, arguments: list[str]
) -> None:
    result = subprocess.run(
        [sys.executable, "-I", "-B", str(HELPER), *arguments],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    assert result.returncode == 2, result.stdout + result.stderr
    assert "Traceback" not in result.stdout + result.stderr
    assert not list(tmp_path.iterdir())


def test_runtime_failure_does_not_display_environment_locals(tmp_path: Path) -> None:
    (tmp_path / ".github").mkdir()
    (tmp_path / ".github/native-integration.json").write_text("[]\n")
    sentinel = "SYNTHETIC_NATIVE_PARSER_ENVIRONMENT_MUST_NOT_BE_SHOWN"
    result = subprocess.run(
        [
            sys.executable,
            "-I",
            "-B",
            str(HELPER),
            "installed",
            "--source",
            str(tmp_path),
            "--python",
            sys.executable,
            "--report",
            str(tmp_path / "reports"),
        ],
        env={**os.environ, "NATIVE_PARSER_SYNTHETIC_SECRET": sentinel},
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    assert result.returncode == 1
    assert "Missing wheel/fixture" in result.stdout + result.stderr
    assert sentinel not in result.stdout + result.stderr
    assert not (tmp_path / "reports").exists()
