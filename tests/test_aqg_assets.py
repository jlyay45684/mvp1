import json
import tomllib
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]


def test_aqg_commands_are_explicit_argv_arrays() -> None:
    config = tomllib.loads((REPO / ".aqg.toml").read_text(encoding="utf-8"))

    assert config["version"] == 1
    for command_group in ("static", "tests"):
        commands = config["commands"][command_group]
        assert commands
        assert all(isinstance(argv, list) and argv for argv in commands)
        assert all(isinstance(argument, str) for argv in commands for argument in argv)


def test_file_evidence_sources_match_their_targets() -> None:
    evidence = json.loads((REPO / ".aqg" / "evidence.json").read_text(encoding="utf-8"))

    assert evidence["version"] == 1
    assert evidence["claims"]
    for claim in evidence["claims"]:
        if "target" in claim:
            assert claim["source"] == {"kind": "file", "path": claim["target"]}


def test_ci_does_not_publish_artifacts_or_reference_private_credentials() -> None:
    workflow = (REPO / ".github" / "workflows" / "aqg-validation.yml").read_text(
        encoding="utf-8"
    )

    assert "upload-artifact" not in workflow
    assert "secrets." not in workflow
    assert "AGENT-QUALITY-GATE.git" not in workflow
    assert "persist-credentials: false" in workflow
