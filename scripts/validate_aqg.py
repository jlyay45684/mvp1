"""Run cross-project AQG v0.1.0 acceptance scenarios."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


def run_aqg(repo: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    completed = subprocess.run(
        [sys.executable, "-m", "agent_quality_gate", "check", "--repo", str(repo)],
        check=False,
        capture_output=True,
        text=True,
        timeout=180,
    )
    report_path = repo / ".aqg" / "reports" / "aqg-report.json"
    if not report_path.is_file():
        raise AssertionError(
            f"AQG did not create {report_path}\nstdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )
    return completed, json.loads(report_path.read_text(encoding="utf-8"))


def gate_status(report: dict[str, Any], name: str) -> str:
    statuses = {gate["name"]: gate["status"] for gate in report["gates"]}
    if name not in statuses:
        raise AssertionError(f"Missing gate in report: {name}")
    return statuses[name]


def assert_result(
    label: str,
    completed: subprocess.CompletedProcess[str],
    report: dict[str, Any],
    expected_exit: int,
    expected_ahg: str,
) -> None:
    if completed.returncode != expected_exit:
        raise AssertionError(
            f"{label}: expected exit {expected_exit}, got {completed.returncode}\n"
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )
    actual_ahg = gate_status(report, "ahg")
    if actual_ahg != expected_ahg:
        raise AssertionError(f"{label}: expected AHG {expected_ahg}, got {actual_ahg}")
    print(
        f"{label}: exit={completed.returncode} "
        f"overall={report['overall_status']} ahg={actual_ahg}"
    )


def scenario_config() -> str:
    return """version = 1

[scan]
include = ["sample.py"]
exclude = []

[commands]
static = [["python", "-m", "compileall", "-q", "sample.py"]]
tests = [["python", "-c", "print('scenario test passed')"]]

[timeouts]
static = 30
test = 30

[ahg]
evidence_file = ".aqg/evidence.json"

[report]
json = ".aqg/reports/aqg-report.json"
markdown = ".aqg/reports/aqg-report.md"
"""


def write_scenario(repo: Path, claim: dict[str, Any]) -> None:
    (repo / ".aqg").mkdir(parents=True)
    (repo / "sample.py").write_text("VALUE = 1\n", encoding="utf-8")
    (repo / ".aqg.toml").write_text(scenario_config(), encoding="utf-8")
    evidence = {"version": 1, "claims": [claim]}
    (repo / ".aqg" / "evidence.json").write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def validate(repo: Path) -> None:
    pass_completed, pass_report = run_aqg(repo)
    assert_result("PASS", pass_completed, pass_report, expected_exit=0, expected_ahg="PASS")
    for gate in pass_report["gates"]:
        if gate["status"] != "PASS":
            raise AssertionError(f"PASS scenario gate {gate['name']} was {gate['status']}")

    with tempfile.TemporaryDirectory(prefix="aqg-fail-") as temp_dir:
        fail_repo = Path(temp_dir)
        write_scenario(
            fail_repo,
            {
                "id": "missing-evidence",
                "claim": "必要證據檔案存在且非空",
                "type": "file_nonempty",
                "target": "missing.txt",
                "source": {"kind": "file", "path": "missing.txt"},
            },
        )
        fail_completed, fail_report = run_aqg(fail_repo)
        assert_result("FAIL", fail_completed, fail_report, expected_exit=1, expected_ahg="FAIL")

    with tempfile.TemporaryDirectory(prefix="aqg-unverified-") as temp_dir:
        unverified_repo = Path(temp_dir)
        write_scenario(
            unverified_repo,
            {
                "id": "subjective-claim",
                "claim": "產出內容語意完全正確",
                "type": "subjective_correctness",
            },
        )
        unverified_completed, unverified_report = run_aqg(unverified_repo)
        assert_result(
            "UNVERIFIED",
            unverified_completed,
            unverified_report,
            expected_exit=1,
            expected_ahg="UNVERIFIED",
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="Repository root to validate")
    args = parser.parse_args()
    validate(Path(args.repo).resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
