from pathlib import Path
import json
import pytest
from docker_doctor.scanner import scan_project
from docker_doctor.cli import main

def write(root: Path, name: str, text: str) -> None:
    (root / name).write_text(text, encoding="utf-8")

def codes(report):
    return {f.code for f in report.findings}

def test_safe_dockerfile(tmp_path):
    write(tmp_path, "Dockerfile", "FROM python:3.12-slim\nRUN useradd -r app\nUSER app\nHEALTHCHECK CMD python -c 'exit(0)'\nCMD [\"python\"]\n")
    report = scan_project(tmp_path)
    assert report.ok
    assert "D002" not in codes(report)
    assert "D007" not in codes(report)

def test_dockerfile_risky_patterns(tmp_path):
    write(tmp_path, "Dockerfile", "FROM ubuntu:latest\nARG API_TOKEN=oops\nRUN apt-get upgrade -y\n")
    report = scan_project(tmp_path)
    assert {"D002", "D004", "D005", "D007"} <= codes(report)
    assert not report.ok

def test_compose_dangerous_settings(tmp_path):
    write(tmp_path, "compose.yml", "services:\n  app:\n    image: demo:latest\n    privileged: true\n    volumes:\n      - /var/run/docker.sock:/var/run/docker.sock\n")
    report = scan_project(tmp_path)
    assert {"C001", "C003", "C004"} <= codes(report)
    assert report.counts["error"] == 2

def test_inline_secret_detection(tmp_path):
    write(tmp_path, "compose.yaml", "services:\n  app:\n    environment:\n      API_KEY: definitely-not-a-real-key\n")
    assert "C005" in codes(scan_project(tmp_path))

def test_missing_files_is_error(tmp_path):
    report = scan_project(tmp_path)
    assert codes(report) == {"P001"}
    assert not report.ok

def test_invalid_root():
    with pytest.raises(ValueError):
        scan_project("/path/that/should/not/exist/docker-doctor")

def test_cli_json_and_exit_policy(tmp_path, capsys):
    write(tmp_path, "Dockerfile", "FROM python:3.12-slim\nUSER 10001\nHEALTHCHECK NONE\n")
    assert main([str(tmp_path), "--json", "--fail-on", "error"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["files_scanned"] == ["Dockerfile"]

def test_cli_fail_on_warning(tmp_path):
    write(tmp_path, "Dockerfile", "FROM ubuntu:latest\nUSER 1000\nHEALTHCHECK NONE\n")
    assert main([str(tmp_path), "--fail-on", "warning"]) == 1
    assert main([str(tmp_path), "--fail-on", "never"]) == 0
