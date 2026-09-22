from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import re
from typing import Iterable

SEVERITY = {"info": 0, "warning": 1, "error": 2}

@dataclass(frozen=True)
class Finding:
    code: str
    severity: str
    message: str
    path: str
    line: int | None = None
    hint: str | None = None

@dataclass
class Report:
    root: str
    files_scanned: list[str]
    findings: list[Finding]

    @property
    def counts(self) -> dict[str, int]:
        return {level: sum(f.severity == level for f in self.findings) for level in SEVERITY}

    @property
    def ok(self) -> bool:
        return not any(f.severity == "error" for f in self.findings)

    def to_dict(self) -> dict:
        return {"root": self.root, "files_scanned": self.files_scanned, "counts": self.counts,
                "ok": self.ok, "findings": [asdict(f) for f in self.findings]}

def _finding(code: str, severity: str, msg: str, path: Path, line: int | None = None, hint: str | None = None) -> Finding:
    return Finding(code, severity, msg, path.as_posix(), line, hint)

def scan_dockerfile(path: Path) -> list[Finding]:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    out: list[Finding] = []
    from_lines = [(i, line) for i, line in enumerate(lines, 1) if re.match(r"^\s*FROM\s+", line, re.I)]
    if not from_lines:
        out.append(_finding("D001", "error", "Dockerfile has no FROM instruction.", path, hint="Add a valid base image."))
    for i, line in from_lines:
        image = re.split(r"\s+", line.strip(), maxsplit=2)[1]
        if image.endswith(":latest") or ":" not in image.split("@", 1)[0]:
            out.append(_finding("D002", "warning", f"Base image is not pinned to an explicit tag: {image}", path, i, "Use a specific tag or digest for reproducible builds."))
    if any(re.search(r"^\s*ADD\s+https?://", line, re.I) for line in lines):
        for i, line in enumerate(lines, 1):
            if re.search(r"^\s*ADD\s+https?://", line, re.I):
                out.append(_finding("D003", "warning", "Remote URL used with ADD.", path, i, "Prefer a verified download step with checksum validation."))
    for i, line in enumerate(lines, 1):
        if re.search(r"^\s*(ENV|ARG)\s+[^=]*(PASSWORD|TOKEN|SECRET|API_KEY)", line, re.I):
            out.append(_finding("D004", "error", "Potential secret-bearing ENV/ARG variable declared in image build.", path, i, "Use BuildKit secrets or runtime secret injection; never bake credentials into images."))
        if re.search(r"^\s*RUN\s+.*\bapt(-get)?\s+upgrade\b", line, re.I):
            out.append(_finding("D005", "warning", "Package upgrade during image build can reduce reproducibility.", path, i, "Install only required packages from a pinned base image."))
        if re.search(r"^\s*RUN\s+.*apt-get\s+install", line, re.I) and "--no-install-recommends" not in line:
            out.append(_finding("D006", "info", "apt-get install does not use --no-install-recommends.", path, i, "Consider it to keep images smaller."))
    final_from = from_lines[-1][0] if from_lines else 0
    has_nonroot = any(i > final_from and re.match(r"^\s*USER\s+(?!0\b|root\b)\S+", line, re.I) for i, line in enumerate(lines, 1))
    if from_lines and not has_nonroot:
        out.append(_finding("D007", "warning", "Final image does not declare a non-root USER.", path, hint="Create/use a least-privileged user when the workload permits."))
    if not any(re.match(r"^\s*HEALTHCHECK\b", line, re.I) for line in lines):
        out.append(_finding("D008", "info", "No HEALTHCHECK declared.", path, hint="Add one when the service has a meaningful health signal."))
    return out

def scan_compose(path: Path) -> list[Finding]:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    out: list[Finding] = []
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if re.match(r"privileged\s*:\s*(true|yes)\s*$", stripped, re.I):
            out.append(_finding("C001", "error", "Service enables privileged mode.", path, i, "Remove privileged mode or grant only the specific capability required."))
        if re.match(r"network_mode\s*:\s*[\"']?host[\"']?\s*$", stripped, re.I):
            out.append(_finding("C002", "warning", "Service uses host networking.", path, i, "Use an isolated Docker network unless host networking is required."))
        if re.search(r"/var/run/docker\.sock\s*:", stripped):
            out.append(_finding("C003", "error", "Docker socket is mounted into a container.", path, i, "Avoid exposing the Docker daemon socket; it grants extensive host control."))
        if re.match(r"image\s*:\s*\S+:latest\s*$", stripped, re.I) or re.match(r"image\s*:\s*[^\s:@]+(?:/[^\s:@]+)*\s*$", stripped, re.I):
            out.append(_finding("C004", "warning", "Service image is not pinned to a stable explicit version.", path, i, "Use an explicit image tag or digest."))
        if re.search(r"(?i)(password|token|secret|api_key)\s*[:=]\s*[^${\s][^\s]*", stripped) and not stripped.startswith("#"):
            out.append(_finding("C005", "error", "Possible inline credential in Compose configuration.", path, i, "Use Docker secrets or environment interpolation; keep secret values outside version control."))
    return out

def _candidates(root: Path) -> Iterable[Path]:
    names = ("Dockerfile", "dockerfile", "compose.yml", "compose.yaml", "docker-compose.yml", "docker-compose.yaml")
    for name in names:
        p = root / name
        if p.is_file():
            yield p

def scan_project(root: str | Path) -> Report:
    base = Path(root).expanduser().resolve()
    if not base.is_dir():
        raise ValueError(f"Not a directory: {base}")
    files = list(_candidates(base))
    findings: list[Finding] = []
    for path in files:
        findings.extend(scan_dockerfile(path) if path.name.lower() == "dockerfile" else scan_compose(path))
    if not files:
        findings.append(_finding("P001", "error", "No supported Dockerfile or Compose file found.", base, hint="Run Docker Doctor from a Docker project root."))
    findings.sort(key=lambda f: (-SEVERITY[f.severity], f.path, f.line or 0, f.code))
    return Report(str(base), [p.name for p in files], findings)
